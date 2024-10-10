import os
import google.generativeai as genai
from dotenv import load_dotenv
from tavily import TavilyClient
from huggingface_hub import InferenceClient

load_dotenv()

def initialize_clients_4():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    genai.configure(api_key=gemini_api_key)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 4096,
        "response_mime_type": "text/plain",
    }
    
    gemini_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )    

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    tavily_client = TavilyClient(tavily_api_key)

    SLM = InferenceClient(
        "mistralai/Mistral-7B-Instruct-v0.1",
        token=os.getenv("HuggingFace_API_KEY"),
    )

    return gemini_model, tavily_client, SLM

# List of recommended websites for fact-checking
recommended_sites = [
    "https://english.newsfirst.lk/",
    "https://www.adaderana.lk/",
    "https://www.hirunews.lk/english/"
]

# Function to decompose the main claim into subclaims
def is_complex_question(claim, SLM):
    SLM_prompt = f"""Determine if the following statement is a complex question that requires further decomposition into subclaims.
    Statement: '{claim}'
    Return True if it is a complex question, otherwise return False."""
    SLM_response = ""
    for message in SLM.chat_completion(
            messages=[{"role": "user", "content": SLM_prompt}],
            max_tokens=256,
            stream=True,
        ):
            content = message.choices[0].delta.content
            if content:
                SLM_response += content
    return SLM_response


# Function to decompose the main claim into subclaims
def decompose_claim(claim, SLM):
    SLM_prompt = f"""Decompose the following claim into separate meaningful subclaims, listing them as:
1.
2.
3.

Claim: '{claim}'
If no need to decompose, just return the same claim as it is. Only decompose if the claim is a compound one with multiple questions.
"""
    SLM_response = ""
    for message in SLM.chat_completion(
            messages=[{"role": "user", "content": SLM_prompt}],
            max_tokens=256,
            stream=True,
        ):
            content = message.choices[0].delta.content
            if content:
                SLM_response += content
    return SLM_response

# Function to verify each subclaim using an LLM-based QA and Tavily search
def verify_subclaim(subclaim, gemini_model, tavily_client):
    # Perform a Tavily search for the subclaim, including recommended sites
    tavily_context = tavily_client.search(query=subclaim + " Sri Lanka", search_depth="advanced", include_domains=recommended_sites)

    fast_check_results = []
    for result in tavily_context['results']:
        if 'title' in result and 'content' in result:
            fast_check_results.append({
                    'title': result['title'],
                    'content': result['content']
                })
    print(fast_check_results)

    chat_session = gemini_model.start_chat()
    final_prompt = f"""Verify the following subclaim: '{subclaim}'. 
    Consider these search results: {fast_check_results}
    Answer in terms of true, false, or partially true, and provide a brief reason."""
    response = chat_session.send_message(final_prompt)
    return response.text

# Function to handle claim decomposition, verification, and final prediction
def verify_claim_hiss(claim, gemini_model, tavily_client, SLM):

    # is_complex = is_complex_question(claim, SLM)
    # print(is_complex)

    # if "true" in str(is_complex).lower():
    #     subclaims_text = decompose_claim(claim, SLM)
    #     subclaims = subclaims_text.strip().split('\n')
    # else:
    #     subclaims = [claim]
    subclaims = [claim]
    print(subclaims)
    
    # Step 2: Verify each subclaim
    verifications = []
    for subclaim in subclaims:
        if subclaim.strip():  # Check if subclaim is not empty
            subclaim_text = subclaim.split('. ', 1)[1] if '. ' in subclaim else subclaim
            print("-"*100)
            print(subclaim_text)
            print("-"*100)
            verification = verify_subclaim(subclaim_text, gemini_model, tavily_client)
            print(verification)
            verifications.append({
                'subclaim': subclaim_text,
                'verification': verification
            })
    
    # Step 3: Provide a final verdict
    final_prediction = "Based on the verifications, this is - "
    truth_levels = [v['verification'].lower() for v in verifications]
    
    if all('true' in t for t in truth_levels):
        final_prediction += "true."
    elif all('false' in t for t in truth_levels):
        final_prediction += "false."
    else:
        final_prediction += "partially true."
    
    return final_prediction, verifications

# Main function
if __name__ == "__main__":
    claim = "Anura Kumara is a good cricketer"
    gemini, tavily, Mistral = initialize_clients_4()
    final_prediction, verifications = verify_claim_hiss(claim, gemini, tavily, Mistral)
    
    print("\n--- Final Prediction ---")
    print(final_prediction)
    
    print("\n--- Detailed Subclaim Verifications ---")
    for verification in verifications:
        print(f"{verification['subclaim']}: {verification['verification']}")
