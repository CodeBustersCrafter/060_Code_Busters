import os
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()

def initialize_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    return AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

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

async def analyze_content(content, client):
    prompt = f"""Analyze the following content and provide a detailed description of the election predictions and trends:\n\n{content}. 
    In addition of that arrange the data in order to plot some graphs. Your response should be in json format but it should follow streamlit lib syntax for each
    graph each element in the response json should be a key value pair (graph_name,list of data and the type of the graph). Please do not include the description in the response and just give me a
    string which can be directly covert in to a json object in python. Do not add additional symbols to it. Minimum count of graphs = 5, maximum count of graphs = 10, make sure to give suitable meanningful graph name
    """
    
    completion = await client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=0.7,
        max_tokens=1024
    )
    return completion.choices[0].message.content

async def main():
    client = initialize_client()
    urls = [
        "https://numbers.lk/analysis/akd-maintains-lead-in-numbers-lk-s-2nd-pre-election-poll-ranil-surges-to-second-place",
        "https://www.ihp.lk/press-releases/ak-dissanayake-and-sajith-premadasa-led-august-voting-intent-amongst-all-adults"
    ]
    
    extracted_content = extract_data_from_urls(urls)
    analysis = await analyze_content(extracted_content, client)
    print(analysis)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
