from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from main import initialize_clients, generate_response, create_vector_db, create_candidate_vector_stores, compare_candidates
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize client and vector stores
try:
    openai_client,tavily_client,memory,gemini_model = initialize_clients()
    vector_store = create_vector_db()
    candidate_vector_stores = create_candidate_vector_stores()
    if vector_store is None or candidate_vector_stores is None:
        logger.error("Vector store or candidate vector stores are not initialized.")
except Exception as e:
    logger.error(f"Initialization error: {e}")
    vector_store = None
    candidate_vector_stores = None

class Query(BaseModel):
    prompt: str
    language: str = Field(default="English", description="Language of the prompt and response")

class ComparisonQuery(BaseModel):
    candidates: list[str]

AZURE_TRANSLATE_ENDPOINT = os.getenv("AZURE_TRANSLATE_ENDPOINT")
AZURE_TRANSLATE_KEY = os.getenv("AZURE_TRANSLATE_KEY")

def translate_text(text, from_lang, to_lang):
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATE_KEY,
        'Ocp-Apim-Subscription-Region': 'southeastasia', 
        'Content-type': 'application/json'
    }
    params = {
        'api-version': '3.0',
        'from': from_lang,
        'to': to_lang
    }
    body = [
        {'Text': text}
    ]
    response = requests.post(
        AZURE_TRANSLATE_ENDPOINT,
        params=params,
        headers=headers,
        json=body
    )
    response.raise_for_status()
    return response.json()[0]['translations'][0]['text']


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World"}

@app.post("/generate")
async def generate(query: Query):
    logger.info(f"Received prompt: {query.prompt} in language: {query.language}")
    if vector_store is None:
        logger.error("Vector store is not initialized.")
        return {"error": "Vector store is not initialized."}
    try:
        # Translate prompt to English if necessary
        if query.language.lower() == "english":
            translated_prompt = query.prompt
        elif query.language.lower() == "sinhala":
            translated_prompt = translate_text(query.prompt, "si", "en")
            print(translated_prompt)
        elif query.language.lower() == "tamil":
            translated_prompt = translate_text(query.prompt, "ta", "en")
        else:
            return {"error": "Unsupported language selected."}

        response = await generate_response(translated_prompt, openai_client, tavily_client, vector_store, memory, 1,gemini_model)

        # Translate response back to the selected language if necessary
        if query.language.lower() == "english":
            translated_response = response
        elif query.language.lower() == "sinhala":
            translated_response = translate_text(response, "en", "si")
        elif query.language.lower() == "tamil":
            translated_response = translate_text(response, "en", "ta")
        else:
            translated_response = response  # Fallback

        logger.info(f"Generated response: {translated_response}")
        return {"response": translated_response}
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        return {"error": "Failed to generate response."}

@app.post("/compare")
async def compare(query: ComparisonQuery):
    logger.info(f"Received comparison request for {', '.join(query.candidates)}")
    if candidate_vector_stores is None:
        logger.error("Candidate vector stores are not initialized.")
        return {"error": "Candidate vector stores are not initialized."}
    try:
        # Use the relevant candidate vector stores for comparison
        relevant_vector_stores = {candidate: candidate_vector_stores[candidate] for candidate in query.candidates if candidate in candidate_vector_stores}
        
        # Check if any of the relevant vector stores is None
        if any(store is None for store in relevant_vector_stores.values()):
            logger.error("One or more candidate vector stores are None.")
            return {"error": "One or more candidate vector stores are not initialized."}
        
        comparison = await compare_candidates(query.candidates, openai_client, tavily_client, relevant_vector_stores)
        logger.info(f"Generated comparison: {comparison}")
        return {"comparison": comparison}
    except Exception as e:
        logger.error(f"Error generating comparison: {e}", exc_info=True)
        return {"error": f"Failed to generate comparison: {str(e)}"}

from win_predictor import extract_data_from_urls, analyze_content, initialize_clients_2

@app.get("/win_predictor")
async def win_predictor():
    openai_client,tavily_client = initialize_clients_2()
    logger.info("Win predictor endpoint accessed.")
    try:
        urls = [
            "https://numbers.lk/analysis/akd-maintains-lead-in-numbers-lk-s-2nd-pre-election-poll-ranil-surges-to-second-place",
            "https://www.ihp.lk/press-releases/ak-dissanayake-and-sajith-premadasa-led-august-voting-intent-amongst-all-adults"
        ]
        extracted_content = extract_data_from_urls(urls)
        analysis = await analyze_content(extracted_content, openai_client, tavily_client)
        logger.info(f"Generated win predictor analysis: {analysis}")
        return {"data": analysis}
    except Exception as e:
        logger.error(f"Error in win predictor: {e}")
        return {"error": "Failed to generate win predictor analysis."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)