import os
import asyncio
import time
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

load_dotenv()

similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def initialize_clients_5():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    genai.configure(api_key=gemini_api_key)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 4096,
        "response_mime_type": "text/plain",
    }
    
    gemini_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )    

    memory = ConversationBufferMemory(return_messages=True)
    
    return memory, gemini_model

async def retrieve_context(query, vector_store, top_k=8):
    results = vector_store.similarity_search_with_score(query, k=top_k)
    weighted_context = ""
    for doc, score in results:
        weighted_context += f"{doc.page_content} (relevance: {score})\n\n"
    return weighted_context

async def generate_manifesto_response(prompt, vector_stores, memory, gemini_model):
    async def get_gemini_response(last_prompt):
        chat_session = gemini_model.start_chat()
        final_prompt = f""" 
        role: system, content: You are a helpful assistant that provides information about Sri Lankan Election candidates manifestos.
        role: user, content: {last_prompt}"""
        response = chat_session.send_message(final_prompt)
        return response.text
    
    candidate = candidate_selection(prompt)

    if candidate in vector_stores:
        vector_store = vector_stores[candidate]
        context = await retrieve_context(prompt, vector_store)    

        history = memory.load_memory_variables({})
        history_context = "\n".join([f"{m.type}: {m.content}" for m in history.get("history", [])])
        context = f"Conversation History:\n{history_context}\n\nContext: {context}\n\n"

        full_prompt = f"""
        Question: {prompt}

        Instructions:
            Use the provided Context and Additional Context to inform your response.

        {context}

        Answer:
        """
        
        return await get_gemini_response(full_prompt)
    else:
        return "I'm sorry, I don't have information about that candidate's manifesto."

def candidate_selection(prompt):
    # Creating SLM client
    SLM = InferenceClient(
        "mistralai/Mistral-7B-Instruct-v0.1",
        token=os.getenv("HuggingFace_API_KEY"),
    )

    SLM_prompt = f"""
    Determine which candidate's manifesto the following prompt is related to for the Sri Lankan Elections 2024.
    Respond with one of the following candidate names if it's about their specific manifesto:
    
    - Ranil Wickremesinghe
    - Anura Kumara Dissanayake
    - Namal Rajapaksa
    - Sajith Premadasa
    - Dilith Jayaweera

    Select only one option from the above list.

    Prompt: {prompt}
    """
        
    start_time = time.time()
        
    SLM_response = ""
    for message in SLM.chat_completion(
            messages=[{"role": "user", "content": SLM_prompt}],
            max_tokens=50,
            stream=True,
        ):
            content = message.choices[0].delta.content
            if content:
                print(content, end="")
                SLM_response += content 

    end_time = time.time()
    process_time = end_time - start_time
        
    print(f"\nSLM_response: {SLM_response.strip()}")
    print(f"Process time: {process_time:.2f} seconds")

    response = SLM_response.strip().lower()

    candidates = ["Ranil Wickremesinghe", "Anura Kumara Dissanayake", "Namal Rajapaksa", "Sajith Premadasa", "Dilith Jayaweera"]
    for candidate in candidates:
        if candidate.lower() in response:
            return candidate
    return "General"