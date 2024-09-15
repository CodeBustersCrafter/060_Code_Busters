import os
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from tavily import Client as TavilyClient

load_dotenv()

def initialize_clients_2():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    openai_client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=openai_api_key
    )
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    tavily_client = TavilyClient(tavily_api_key)
    
    return openai_client, tavily_client

def extract_data_from_urls(urls):
    all_data = []
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from the main content of the page
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text from all remaining elements
            main_content = soup.get_text(separator=' ', strip=True)
            
            # Remove extra whitespace and join lines
            main_content = ' '.join(main_content.split())
            
            all_data.append(main_content)
        except Exception as e:
            print(f"Error extracting data from {url}: {str(e)}")
    
    # Join all extracted data into one string
    return " ".join(all_data)

async def analyze_content(content, openai_client,tavily_client):

    tavily_context = tavily_client.search(query="Provide accurate and up-to-date predictions for the Sri Lanka election, including current polling data and trends.")
    prompt = f"""Analyze the following content and provide a detailed description of the election predictions and trends:

    Main Content: {content}
    Additional Context: {tavily_context}

    1. List the top 5 candidates based on the analysis.
    2. Organize the data for plotting various graphs(One of data analysis should be based on provinces and the graph should be a map).

    Your response for the 2nd point should be in JSON format following Streamlit library syntax. For each graph, include a key-value pair where the key is the graph name, and the value is an object containing the data and the type of the graph.

    - Do not include any descriptive text in the response.
    - The response should be a string that can be directly converted into a JSON object in Python without additional symbols.
    - Include a minimum of 5 graphs and a maximum of 7 graphs.
    - Ensure each graph name is meaningful and descriptive.
    """
    
    completion = await openai_client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=0.7,
        max_tokens=5120
    )
    return completion.choices[0].message.content

async def main():
    openai_client,tavily_client = initialize_clients_2()
    urls = [
        "https://numbers.lk/analysis/akd-maintains-lead-in-numbers-lk-s-2nd-pre-election-poll-ranil-surges-to-second-place",
        "https://www.ihp.lk/press-releases/ak-dissanayake-and-sajith-premadasa-led-august-voting-intent-amongst-all-adults"
    ]
    
    extracted_content = extract_data_from_urls(urls)
    analysis = await analyze_content(extracted_content, openai_client,tavily_client)
    print(analysis)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
