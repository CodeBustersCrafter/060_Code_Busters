from openai import AsyncOpenAI

def initialize_client():
    return AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

async def generate_response(prompt, client):
    completion = await client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=0.7,
        max_tokens=1024
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    import asyncio
    
    async def main():
        client = initialize_client()
        prompt = "What are the key insights from the text?"
        response = await generate_response(prompt, client)
        print(response)

    asyncio.run(main())