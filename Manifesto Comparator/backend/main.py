import os
from openai import AsyncOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

def initialize_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    return AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

def create_vector_db():
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Construct the full path to 'text_file_db.txt'
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
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

async def retrieve_context(query, vector_store, top_k=3):
    results = vector_store.similarity_search(query, k=top_k)
    return "\n".join([doc.page_content for doc in results])

async def generate_response(prompt, client, vector_store):
    context = await retrieve_context(prompt, vector_store)
    full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
    
    completion = await client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.6,
        top_p=0.7,
        max_tokens=1024
    )
    return completion.choices[0].message.content

# New function to create vector stores for each candidate
def create_candidate_vector_stores():
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Construct the full path to 'text_file_db.txt'
        file_path = os.path.join(script_dir, "manifest.txt")
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("Manifest File read successfully")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

# New function to compare two candidates
async def compare_candidates(candidate1, candidate2, client, candidate_vector_stores):
    if candidate_vector_stores is None:
        print("Failed to create candidate_vector_stores.")
        return
    prompt = f"""Compare the manifestos of {candidate1} and {candidate2} based on the text. Provide a detailed comparison of their key policies and approaches.
    give me the response comparing both of them and response should be like a table. At the end of the table merge the both sides add common policies'"""
    
    response = await generate_response(prompt, client, candidate_vector_stores)
    print(response)
    return response
    
    

if __name__ == "__main__":
    import asyncio
    
    async def main():
        client = initialize_client()
        vector_store = create_vector_db()
        if vector_store is None:
            print("Failed to create vector store.")
            return
        prompt = "What are the main political parties mentioned in the text?"
        response = await generate_response(prompt, client, vector_store)
        print(response)
        
        # Example usage of the new comparison function
        candidate_vector_stores = create_candidate_vector_stores()
        comparison = await compare_candidates("Sajith", "Ranil", client, candidate_vector_stores)
        print("\nComparison of Sajith and Ranil's manifestos:")
        print(comparison)
    
    asyncio.run(main())