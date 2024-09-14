from openai import AsyncOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def initialize_client():
    return AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

def create_vector_db():
    try:
        with open("text_file_db.txt", "r", encoding="utf-8") as file:
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

    asyncio.run(main())