import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

def initialize_clients_3():
    LLAMA_api_key = os.getenv("LLAMA_API_KEY")
    if not LLAMA_api_key:
        raise ValueError("LLAMA is not set in the environment variables.")
    LLAMA_client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=LLAMA_api_key
    )
    
    return LLAMA_client

async def retrieve_context(query, vector_store, top_k=5):
    results = vector_store.similarity_search_with_score(query, k=top_k)
    weighted_context = ""
    for doc, score in results:
        weighted_context += f"{doc.page_content} (relevance: {score})\n\n"
    return weighted_context

async def generate_comparison(prompt, LLAMA_client):
    try:
        completion = await LLAMA_client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about Sri Lankan Elections 2024."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            top_p=0.7,
            max_tokens=3072
        )
        return completion.choices[0].message.content
    except AttributeError:
        return completion
    except Exception as e:
        print(f"Error in get_LLAMA_response: {e}")
        return "An error occurred while processing your request. Try again later."

async def compare_candidates(candidates, LLAMA_client, candidate_vector_stores):
    if candidate_vector_stores is None:
        print("Failed to create or retrieve candidate vector stores.")
        return

    async def get_candidate_response(candidate, prompt):
        if candidate not in candidate_vector_stores:
            return f"No data available for {candidate}."
        
        sections = [
            "Economic Policy and Growth Strategies",
            "Education Reform and Innovation",
            "Energy and Sustainability",
            "Healthcare System and Public Health",
            "National Security and Defense",
            "Legal Framework and Judicial Reform",
            "Transportation and Mobility",
            "Infrastructure Development and Modernization",
            "Foreign Policy and International Relations"
        ]
        
        async def get_section_context(section):
            return await retrieve_context(f"{section} {prompt}", candidate_vector_stores[candidate], top_k=10)
        
        section_contexts = await asyncio.gather(*[get_section_context(section) for section in sections])
        context = "\n".join(f"{section}:\n{context}\n" for section, context in zip(sections, section_contexts))

        full_prompt = f"""Context (from {candidate}'s manifesto): {context}

        Question: {prompt}

        Instructions:
        1. Analyze the provided context for each section extracted from {candidate}'s manifesto.
        2. Summarize the specific policies and approaches mentioned for each section.
        3. If a section is not addressed, state "No specific information available".
        4. Provide a concise answer, focusing on key points.
        5. Include important numerical data, targets, or timelines if mentioned.
        6. Highlight any unique or standout policies."""
        
        completion = await LLAMA_client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
            top_p=0.4,
            max_tokens=4096
        )
        return completion.choices[0].message.content

    prompt = """Summarize the key policies and approaches in the manifesto for this candidate
    on the following sections:
    1. Economic Policy and Growth Strategies
    2. Education Reform and Innovation
    3. Energy and Sustainability
    4. Healthcare System and Public Health
    5. National Security and Defense
    6. Legal Framework and Judicial Reform
    7. Transportation and Mobility
    8. Infrastructure Development and Modernization
    9. Foreign Policy and International Relations
    Provide a brief overview for each policy area, focusing on main points and any unique initiatives."""
    
    responses = await asyncio.gather(*[get_candidate_response(candidate, prompt) for candidate in candidates])
    responses = dict(zip(candidates, responses))

    policies_string = "".join(f"{candidate}'s policies:\n{response}\n\n" for candidate, response in responses.items())

    comparison_prompt = f"""
    Compare the following policies and approaches from {', '.join(candidates)}:

    {policies_string}

    Instructions:
    1. Provide a concise comparison in a table format, highlighting key differences and similarities.
    2. Include all nine policy areas for each candidate.
    3. Use 'No data available' for missing information.
    4. Add a brief section for common policies among all candidates.
    5. Highlight unique or innovative policies for each candidate.
    6. Include a short analysis of each candidate's overall focus and priorities.
    7. Keep the comparison focused on the most important points from the provided responses.

    Comparison should cover these sections:
    1. Economic Policy and Growth Strategies
    2. Education Reform and Innovation
    3. Energy and Sustainability
    4. Healthcare System and Public Health
    5. National Security and Defense
    6. Legal Framework and Judicial Reform
    7. Transportation and Mobility
    8. Infrastructure Development and Modernization
    9. Foreign Policy and International Relations
    """
    
    comparison = await generate_comparison(comparison_prompt, LLAMA_client)

    return comparison
