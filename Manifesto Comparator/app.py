from fastapi import FastAPI
from pydantic import BaseModel
from main import initialize_client, generate_response

app = FastAPI()

client = initialize_client()

class Query(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generate")
async def generate(query: Query):
    response = await generate_response(query.prompt, client)
    return {"response": response}