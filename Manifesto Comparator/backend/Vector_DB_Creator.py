import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import concurrent.futures

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
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
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
        try:
            file_path = os.path.join(script_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            print(f"{candidate} manifest file read successfully")
            
            chunks = text_splitter.split_text(text)
            return FAISS.from_texts(chunks, embeddings)
            
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
