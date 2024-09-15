from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import initialize_clients, generate_response, create_vector_db, create_candidate_vector_stores, compare_candidates
import os
import logging

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
    openai_client,tavily_client,memory = initialize_clients()
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

class ComparisonQuery(BaseModel):
    candidate1: str
    candidate2: str

@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World"}

@app.post("/generate")
async def generate(query: Query):
    logger.info(f"Received prompt: {query.prompt}")
    if vector_store is None:
        logger.error("Vector store is not initialized.")
        return {"error": "Vector store is not initialized."}
    try:
        response = await generate_response(query.prompt, openai_client,tavily_client, vector_store,memory,1)
        logger.info(f"Generated response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {"error": "Failed to generate response."}

@app.post("/compare")
async def compare(query: ComparisonQuery):
    logger.info(f"Received comparison request for {query.candidate1} and {query.candidate2}")
    if candidate_vector_stores is None:
        logger.error("Candidate vector stores are not initialized.")
        return {"error": "Candidate vector stores are not initialized."}
    try:
        comparison = await compare_candidates(query.candidate1, query.candidate2, openai_client,tavily_client, candidate_vector_stores)
        logger.info(f"Generated comparison: {comparison}")
        return {"comparison": comparison}
    except Exception as e:
        logger.error(f"Error generating comparison: {e}")
        return {"error": "Failed to generate comparison."}

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