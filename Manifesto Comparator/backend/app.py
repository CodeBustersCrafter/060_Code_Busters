from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import initialize_client, generate_response, create_vector_db
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

# Initialize client and vector store
try:
    client = initialize_client()
    vector_store = create_vector_db()
    if vector_store is None:
        logger.error("Vector store is not initialized.")
except Exception as e:
    logger.error(f"Initialization error: {e}")
    vector_store = None

class Query(BaseModel):
    prompt: str

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
        response = await generate_response(query.prompt, client, vector_store)
        logger.info(f"Generated response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {"error": "Failed to generate response."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)