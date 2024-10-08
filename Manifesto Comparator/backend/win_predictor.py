import os
import asyncio
import json
import pandas as pd
import numpy as np
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from tavily import Client as TavilyClient

load_dotenv()

def initialize_clients_2():
    openai_api_key = os.getenv("LLAMA_API_KEY")
    if not openai_api_key:
        raise ValueError("LLAMA_API_KEY is not set in the environment variables.")
    LLAMA_client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=openai_api_key
    )
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    tavily_client = TavilyClient(tavily_api_key)
    
    return LLAMA_client, tavily_client

def load_polling_data(filepath):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, 'data', filepath)
        with open(full_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading polling data: {str(e)}")
        return None
    
def extract_data_from_urls(urls):
    all_data = []
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from the main content of the page
            for script in soup(["script", "style"]):
                script.decompose()
            
            main_content = soup.get_text(separator=' ', strip=True)
            main_content = ' '.join(main_content.split())
            all_data.append(main_content)
        except Exception as e:
            print(f"Error extracting data from {url}: {str(e)}")
    
    return " ".join(all_data)

class PollingAnalyzer:
    def __init__(self, polling_data):
        self.polling_data = polling_data

    def analyze(self):
        results = {}
        for poll in self.polling_data:
            org = poll['organization']
            candidates = poll['results']
            results[org] = candidates
        
        # Calculate average across all polls
        all_candidates = set()
        for poll in results.values():
            all_candidates.update(poll.keys())
        
        averages = {candidate: [] for candidate in all_candidates}
        for poll in results.values():
            for candidate in all_candidates:
                if candidate in poll:
                    averages[candidate].append(poll[candidate])
        
        final_averages = {candidate: np.mean(scores) for candidate, scores in averages.items()}
        
        return {
            "individual_polls": results,
            "average_poll": final_averages
        }

class ConfidenceEstimator:
    def estimate(self, polling_results):
        # Simple confidence estimation based on standard deviation of poll results
        std_devs = {}
        for candidate in polling_results['average_poll'].keys():
            scores = [poll[candidate] for poll in polling_results['individual_polls'].values() if candidate in poll]
            std_devs[candidate] = np.std(scores) if len(scores) > 1 else 0
        
        max_std = max(std_devs.values()) if std_devs else 1
        confidence_levels = {candidate: 1 - (std / max_std) for candidate, std in std_devs.items()}
        
        return confidence_levels

async def analyze_content(polling_data, web_scraped_content, LLAMA_client, tavily_client):
    analyzer = PollingAnalyzer(polling_data)
    polling_results = analyzer.analyze()
    
    confidence_estimator = ConfidenceEstimator()
    confidence_levels = confidence_estimator.estimate(polling_results)
    
    tavily_context = tavily_client.search(query="Latest trends and factors influencing Sri Lankan presidential election")
    
    prompt = f"""Analyze the following polling data, web-scraped content, and provide a detailed election outcome prediction with confidence levels:

    Polling Results: {json.dumps(polling_results, indent=2)}
    Confidence Levels: {json.dumps(confidence_levels, indent=2)}
    Web-scraped Content: {web_scraped_content}
    Additional Context: {tavily_context}

    Based on this information:
    1. Predict the likely winner and runners-up.
    2. Provide probability estimates for each candidate's chances of winning.
    3. Discuss the confidence levels and potential factors influencing the predictions.
    4. Identify any trends or significant differences between polls.
    5. Analyze insights from the web-scraped content.

    Format your response as follows:

    1. Top 5 candidates based on the analysis:
    [List the top 5 candidates here]
    Detailed analysis:
    - predicted_winner: [Candidate Name]
    - probability_estimates(All total should be 1):
        - [Candidate1]: 0.XX
        - [Candidate2]: 0.YY
        - [Candidate3]: 0.ZZ
    - confidence_analysis: [Detailed analysis of confidence levels for each candidate]
    - trends_and_differences: 
        - [Analysis of trends across different polls]
        - [Identification of significant differences between polls]
    - key_factors:
        - [Factor 1 influencing the election]
        - [Factor 2 influencing the election]
    - regional_variations: [Analysis of support variations across different regions]
    - demographic_insights: [Insights on how different demographics are likely to vote]
    - potential_swing_factors: [Factors that could potentially swing the election]
    - additional_insights: [Any other relevant insights or observations]
    
        
    2. Organize the data for plotting various graphs(One of data analysis should be based on provinces and the graph should be a map).
    Use {web_scraped_content} for this.
    These graphs are prefered Candidate Support(bar), Province-level Support(stacked_bar), Voter Sentiment Over Time(line), support by age groups(stacked_bar), support by education level(stacked_bar), support by income level(stacked_bar), support by religion(stacked_bar)
    Your response for the 2nd point should be in JSON format following Streamlit library syntax. For each graph, include a key-value pair where the key is the graph name, and the value is an object containing the data and the type of the graph. (Include alll candidates)

    - Do not include any descriptive text in the response.
    - The response should be a string that can be directly converted into a JSON object in Python without additional symbols.
    - Include a minimum of 5 graphs and a maximum of 7 graphs.
    - Ensure each graph name is meaningful and descriptive.
    """
    
    completion = await LLAMA_client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=0.7,
        max_tokens=5120
    )
    return completion.choices[0].message.content

# async def main():
#     LLAMA_client, tavily_client = initialize_clients_2()
#     polling_data = load_polling_data("polling_data.json")
    
#     urls = [
#         "https://numbers.lk/analysis/akd-maintains-lead-in-numbers-lk-s-2nd-pre-election-poll-ranil-surges-to-second-place",
#         "https://www.ihp.lk/press-releases/ak-dissanayake-and-sajith-premadasa-led-august-voting-intent-amongst-all-adults"
#     ]
#     web_scraped_content = extract_data_from_urls(urls)
    
#     if polling_data:
#         analysis = await analyze_content(polling_data, web_scraped_content, LLAMA_client, tavily_client)
        
#         # Split the response into three parts
#         parts = analysis.split("\n\n")
#         candidates = parts[0].strip()
#         detailed_analysis_json = parts[1].strip()
#         graph_data_json = parts[2].strip()
        
#         # Parse the JSON strings
#         try:
#             detailed_analysis = json.loads(detailed_analysis_json)
#             graph_data = json.loads(graph_data_json)
#         except json.JSONDecodeError as e:
#             print(f"Error parsing JSON: {str(e)}")
#             detailed_analysis = {}
#             graph_data = {}
        
#         # Print the results
#         print("Top 5 Candidates:")
#         print(candidates)
#         print("\nDetailed Analysis:")
#         print(json.dumps(detailed_analysis, indent=2))
#         print("\nGraph Data:")
#         print(json.dumps(graph_data, indent=2))
#     else:
#         print("Failed to load polling data.")

# if __name__ == "__main__":
#     asyncio.run(main())