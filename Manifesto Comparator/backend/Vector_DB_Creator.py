import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import concurrent.futures

def create_vector_db():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    vector_db_path = os.path.join(script_dir, "vector_DBs", "general_vector_db")
    
    if os.path.exists(vector_db_path):
        print("General vector store already exists. Loading from disk.")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
    
    try:
        file_path = os.path.join(script_dir,"Recources", "text_file_db.txt")
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("File read successfully")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
    vector_store.save_local(vector_db_path)
    print(f"Vector store saved to {vector_db_path}")
    
    return vector_store


def create_candidate_vector_stores():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    manifests = {
        "Ranil Wickremesinghe": "ranil_manifest.txt",
        "Sajith Premadasa": "sajith_manifest.txt",
        "Anura Kumara Dissanayake": "anura_manifest.txt",
        "Namal Rajapaksa": "namal_manifest.txt",
        "Dilith Jayaweera": "dilith_manifest.txt"
    }
    
    vector_stores = {}
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    def process_manifest(candidate, file_name):
        vector_db_path = os.path.join(script_dir, "vector_DBs", f"{candidate.lower().replace(' ', '_')}_vector_db")
        
        if os.path.exists(vector_db_path):
            print(f"Vector store for {candidate} already exists. Loading from disk.")
            return FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
        
        try:
            file_path = os.path.join(script_dir,"Recources", file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            print(f"{candidate} manifest file read successfully")
            
            chunks = text_splitter.split_text(text)
            vector_store = FAISS.from_texts(chunks, embeddings)
            
            os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
            vector_store.save_local(vector_db_path)
            print(f"Vector store for {candidate} saved to {vector_db_path}")
            
            return vector_store
            
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError in {file_name}: {e}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
        return None
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_candidate = {executor.submit(process_manifest, candidate, file_name): candidate for candidate, file_name in manifests.items()}
        for future in concurrent.futures.as_completed(future_to_candidate):
            candidate = future_to_candidate[future]
            try:
                vector_stores[candidate] = future.result()
            except Exception as exc:
                print(f'{candidate} generated an exception: {exc}')
    
    return vector_stores

def create_election_instructions_vector_store():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    vector_db_path = os.path.join(script_dir, "vector_DBs", "election_instructions_vector_db")
    
    if os.path.exists(vector_db_path):
        print("Election instructions vector store already exists. Loading from disk.")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
    
    try:
        file_path = os.path.join(script_dir, "Recources", "Election Instructions.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("Election instructions file read successfully")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
    vector_store.save_local(vector_db_path)
    print(f"Election instructions vector store saved to {vector_db_path}")
    
    return vector_store

def create_political_parties_vector_store():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    vector_db_path = os.path.join(script_dir, "vector_DBs", "political_parties_vector_db")
    
    if os.path.exists(vector_db_path):
        print("Political parties vector store already exists. Loading from disk.")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
    
    try:
        file_path = os.path.join(script_dir, "Recources", "Sri lankan political parties.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("Political parties file read successfully")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
    vector_store.save_local(vector_db_path)
    print(f"Political parties vector store saved to {vector_db_path}")
    
    return vector_store

# Call the functions
general_vector_store = create_vector_db()
candidate_vector_stores = create_candidate_vector_stores()
election_instructions_vector_store = create_election_instructions_vector_store()
political_parties_vector_store = create_political_parties_vector_store()