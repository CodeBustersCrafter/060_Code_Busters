from fastapi import FastAPI
from pydantic import BaseModel
from main import initialize_client, generate_response, create_vector_db

app = FastAPI()

client = initialize_client()
vector_store = create_vector_db()

class Query(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generate")
async def generate(query: Query):
    if vector_store is None:
        return {"error": "Vector store is not initialized."}
    response = await generate_response(query.prompt, client, vector_store)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)