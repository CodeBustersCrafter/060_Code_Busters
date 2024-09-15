import os
from openai import AsyncOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from tavily import Client as TavilyClient
from langchain.memory import ConversationBufferMemory

load_dotenv()

def initialize_clients():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    openai_client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=openai_api_key
    )
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    tavily_client = TavilyClient(tavily_api_key)
    
    memory = ConversationBufferMemory(return_messages=True)
    
    return openai_client, tavily_client, memory

def create_vector_db():
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_dir, "text_file_db.txt")
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("File read successfully")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

async def retrieve_context(query, vector_store, top_k=5):
    results = vector_store.similarity_search(query, k=top_k)
    return "\n".join([doc.page_content for doc in results])

async def generate_response(prompt, openai_client, tavily_client, vector_store, memory, type, candidate_vector_stores=None):
    
    context = await retrieve_context(prompt, vector_store)
    
    if candidate_vector_stores is not None:
        for candidate, store in candidate_vector_stores.items():
            candidate_context = await retrieve_context(prompt, store)
            context += f"\n\n{candidate} context:\n{candidate_context}"
    

    if type == 1:
        # Retrieve conversation history from memory
        history = memory.load_memory_variables({})
        history_context = "\n".join([f"{m.type}: {m.content}" for m in history.get("history", [])])
        context = f"Conversation History:\n{history_context}\n\nContext: {context}\n\n"
        # Retrieve additional context from Tavily
        tavily_context = tavily_client.search(query=prompt)
        context += f"Additional Context: {tavily_context}\n\n"

    full_prompt = f"{context}Question: {prompt}\n\nAnswer:"
    
    completion = await openai_client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3,
        top_p=0.9,
        max_tokens=2048
    )
    return completion.choices[0].message.content

# New function to create vector stores for each candidate
def create_candidate_vector_stores():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    manifests = {
        "Ranil": "ranil_manifest.txt",
        "Sajith": "sajith_manifest.txt",
        "Anura": "anura_manifest.txt",
        "Namal": "namal_manifest.txt",
        "Dilith": "dilith_manifest.txt"
    }
    
    vector_stores = {}
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    for candidate, file_name in manifests.items():
        try:
            file_path = os.path.join(script_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            print(f"{candidate} manifest file read successfully")
            
            chunks = text_splitter.split_text(text)
            vector_stores[candidate] = FAISS.from_texts(chunks, embeddings)
            
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError in {file_name}: {e}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
    
    if not vector_stores:
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

# New function to compare two candidates
async def compare_candidates(candidate1, candidate2, openai_client, tavily_client, candidate_vector_stores):
    if candidate_vector_stores is None:
        print("Failed to create or retrieve candidate vector stores.")
        return

    async def get_candidate_response(candidate, prompt):
        if candidate not in candidate_vector_stores:
            return f"No data available for {candidate}."
        context = await retrieve_context(prompt, candidate_vector_stores[candidate], top_k=10)  # Increased top_k for more context
        full_prompt = f"""Context (from {candidate}'s manifesto): {context}

Question: {prompt}

Instructions:
1. Carefully analyze the provided context from {candidate}'s policy details.
2. Extract and summarize the specific policies and approaches mentioned for each of the requested sections.
3. If a particular section is not addressed in the context, state "No specific information available" for that section.(If there is a little bit info about it, please use those data)
4. Provide a concise but comprehensive answer, ensuring no relevant information is omitted.
5. Include any numerical data, targets, or timelines mentioned in the manifesto.
6. Highlight any unique or standout policies that differentiate this candidate from others.

Answer:"""
        completion = await client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2,
            top_p=0.95,
            max_tokens=4096
        )
        return completion.choices[0].message.content

    prompt = """What are the detailed policies and approaches in the manifesto according to this candidate
    on the following sections:
    1. Economic development
    2. Education development
    3. Energy
    4. Health development
    5. Security
    6. Law
    7. Transportation development
    8. Infrastructure development
    9. International relations
    Please provide a comprehensive description for each policy area, including specific details, numerical targets, timelines, and any unique initiatives where available."""
    
    responses = {}
    for candidate in candidates:
        responses[candidate] = await get_candidate_response(candidate, prompt)

    comparison_prompt = f"""
    Compare the following policies and approaches from {', '.join(candidates)}:

    {"".join(f"{candidate}'s policies:\n{response}\n\n" for candidate, response in responses.items())}

    Instructions:
    1. Provide a detailed comparison in a table format, highlighting differences and similarities.
    2. Include all nine policy areas for each candidate.
    3. If there's no data available for a candidate in a specific area, explicitly state 'No data available' in their column.
    4. At the end of the table, add a section for common (similar) policies among all candidates.
    5. Highlight any unique or innovative policies proposed by each candidate.
    6. Include a brief analysis of the overall focus and priorities of each candidate based on their policies.
    7. Ensure that the comparison is comprehensive and captures all relevant information from the provided responses, including numerical targets and timelines where available.

    Comparison should be done only under the following sections:
    1. Economic development
    2. Education development
    3. Energy
    4. Health development
    5. Security
    6. Law
    7. Transportation development
    8. Infrastructure development
    9. International relations
    """

    comparison = await generate_response(comparison_prompt, client, candidate_vector_stores[candidates[0]], candidate_vector_stores)
    return comparison

if __name__ == "__main__":
    import asyncio
    
    async def main():
        openai_client, tavily_client, memory = initialize_clients()
        vector_store = create_vector_db()
        if vector_store is None:
            print("Failed to create vector store.")
            return
        prompt = "When is the next election in Sri Lanka?"
        response = await generate_response(prompt, openai_client, tavily_client, vector_store, memory, 1)
        print(response)
        
        candidate_vector_stores = create_candidate_vector_stores()
        candidates = ["Sajith", "Ranil", "Anura", "Namal", "Dilith"]
        comparison = await compare_candidates(candidates, openai_client, tavily_client, candidate_vector_stores)
        print("\nComparison of candidates' manifestos:")
        print(comparison)
        
        # Debug information
        print("\nDebug Information:")
        for candidate, store in candidate_vector_stores.items():
            if store:
                print(f"{candidate}: Vector store created with {len(store.index_to_docstore_id)} documents")
            else:
                print(f"{candidate}: No vector store created")
    
    asyncio.run(main())