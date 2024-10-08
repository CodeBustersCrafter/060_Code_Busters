# import os
# import asyncio
# import time
# from openai import AsyncOpenAI
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from dotenv import load_dotenv
# from tavily import Client as TavilyClient
# from langchain.memory import ConversationBufferMemory
# import google.generativeai as genai
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer
# import concurrent.futures
# from huggingface_hub import InferenceClient
# from openai import OpenAI

# load_dotenv()

# # Initialize SentenceTransformer for similarity
# similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# def initialize_clients():
#     LLAMA_api_key = os.getenv("LLAMA_API_KEY")
#     if not LLAMA_api_key:
#         raise ValueError("LLAMA is not set in the environment variables.")
#     LLAMA_client = AsyncOpenAI(
#         base_url="https://integrate.api.nvidia.com/v1",
#         api_key=LLAMA_api_key
#     )
    
#     tavily_api_key = os.getenv("TAVILY_API_KEY")
#     if not tavily_api_key:
#         raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
#     tavily_client = TavilyClient(tavily_api_key)
    
#     gemini_api_key = os.getenv("GEMINI_API_KEY")
#     if not gemini_api_key:
#         raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
#     genai.configure(api_key=gemini_api_key)
    
#     generation_config = {
#         "temperature": 0.7,
#         "top_p": 0.9,
#         "top_k": 40,
#         "max_output_tokens": 4096,
#         "response_mime_type": "text/plain",
#     }
    
#     gemini_model = genai.GenerativeModel(
#         model_name="gemini-1.5-flash",
#         generation_config=generation_config,
#     )    

#     openai_client = OpenAI(
#         api_key= os.getenv("OPENAI_API_KEY"),
#         base_url="https://api.aimlapi.com",
#     )
#     memory = ConversationBufferMemory(return_messages=True)
    
#     return LLAMA_client, tavily_client, memory, gemini_model, openai_client

# async def retrieve_context(query, vector_store, top_k=5):
#     results = vector_store.similarity_search_with_score(query, k=top_k)
#     weighted_context = ""
#     for doc, score in results:
#         weighted_context += f"{doc.page_content} (relevance: {score})\n\n"
#     return weighted_context

# def compute_similarity(text1, text2):
#     embeddings = similarity_model.encode([text1, text2])
#     similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
#     return similarity

# def check_consistency(response1, response2, response3, threshold=0.75):
#     similarity12 = compute_similarity(response1, response2)
#     similarity13 = compute_similarity(response1, response3)
#     similarity23 = compute_similarity(response2, response3)
    
#     avg_similarity = (similarity12 + similarity13 + similarity23) / 3
#     return avg_similarity >= threshold

# def aggregate_responses(response1, response2, response3, is_consistent):
#     if is_consistent:
#         aggregated = f"{response1}\n\nAdditionally, {response2}\n\nFurthermore, {response3}"
#     else:
#         # Choose the longest response
#         aggregated = max(response1, response2, response3, key=len)
#     return aggregated

# async def fact_check_response(response,prompt, tavily_client):
#     fact_check_prompt = f"Fact-check the following statement: {response}"
#     try:
#         fact_check_results = tavily_client.search(query=fact_check_prompt)
#         return fact_check_results
#     except Exception as e:
#         updated_fact_check_prompt = f"Fact-check the following statement: '{prompt}'."
#         fact_check_results = tavily_client.search(query=updated_fact_check_prompt)
#         return fact_check_results

# async def combine_responses(response1, response2, response3, tavily_client,prompt):
#     is_consistent = check_consistency(response1, response2, response3)
    
#     aggregated_response = aggregate_responses(response1, response2, response3, is_consistent)
    
#     fact_check_results = await fact_check_response(aggregated_response,prompt, tavily_client)
    
#     combine_responses = f"query\n{aggregated_response}\n\n Fact-Check Results:\n{fact_check_results}\n\n"
    
#     return combine_responses

# async def generate_response(prompt, LLAMA_client, tavily_client, vector_store, memory, type, gemini_model, openai_client):

#     async def get_LLAMA_response(prompt):
#         try:
#             completion = await LLAMA_client.chat.completions.create(
#                 model="meta/llama-3.1-70b-instruct",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant that provides information about Sri Lankan Elections 2024."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.5,
#                 top_p=0.7,
#                 max_tokens=2048
#             )
#             return completion.choices[0].message.content
#         except AttributeError:
#             # Handle the case where the response is a string instead of an object
#             return completion
#         except Exception as e:
#             print(f"Error in get_LLAMA_response: {e}")
#             return "An error occurred while processing your request. Try again later."
        
#     async def get_gemini_response(prompt):
#         chat_session = gemini_model.start_chat()
#         final_prompt = f""" 
#         role: system, content: You are a helpful assistant that provides information about Sri Lankan Elections 2024.
#         role: user, content: {prompt}"""
#         response = chat_session.send_message(final_prompt)
#         return response.text
    
#     async def get_openai_response(prompt):
#         response = openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an AI assistant who knows everything.",
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 },
#             ],
#         )
#         return response.choices[0].message.content
    
#     if not is_election_or_politics_related(prompt):
#         print("Not election or politics related")
#         response = await get_gemini_response(prompt)
    
#         if type == 1:
#             history = memory.load_memory_variables({})
#             history_context = "\n".join([f"{m.type}: {m.content}" for m in history.get("history", [])])
#             memory.save_context({"input": prompt}, {"output": response})
#         return response

#     context = await retrieve_context(prompt, vector_store)    

#     if type == 1:
#         history = memory.load_memory_variables({})
#         history_context = "\n".join([f"{m.type}: {m.content}" for m in history.get("history", [])])
#         context = f"Conversation History:\n{history_context}\n\nContext: {context}\n\n"
#         try:
#             tavily_context = tavily_client.search(query=prompt)
#             context += f"Additional Context: {tavily_context}\n\n"
#             print(context)
#         except Exception as e:
#             print(f"Error fetching Tavily context: {e}")
#             context += "Additional Context: No additional context available.\n\n"

#     full_prompt = f"""
#     Question: {prompt}

#     Instructions:
#         Use the provided Context and Additional Context to inform your response.

#     {context}

#     Answer:
#     """
    
#     if type == 1:
#         LLAMA_response_task = asyncio.create_task(get_LLAMA_response(full_prompt))
#         gemini_response_task = asyncio.create_task(get_gemini_response(full_prompt))
#         openai_response_task = asyncio.create_task(get_openai_response(full_prompt))
        
#         LLAMA_response, gemini_response, openai_response = await asyncio.gather(
#             LLAMA_response_task,
#             gemini_response_task,
#             openai_response_task
#         )
#         print("LLAMA_response")
#         print(LLAMA_response)
#         print("gemini_response")
#         print(gemini_response)
#         print("openai_response")
#         print(openai_response)

#         combined_response = await combine_responses(LLAMA_response, gemini_response, openai_response, tavily_client,prompt)
#         print(combined_response)
#         final_prompt = f"""You are an AI assistant tasked with validating and summarizing information about the Sri Lankan Elections 2024. Please review the following aggregated response, fact-check the information, and provide a concise, accurate summary that a user would find informative and easy to understand.
#         If the fact-check results are not available, please provide a summary of the information.
#         Here's an aggregated response about the Sri Lankan Elections 2024. Please validate this information, correct any inaccuracies, and present a clear, factual summary for the end user:
#         If there was any inacurate information don't tell about it in the summary only add the correct information.
#         Make sure you Don't add any markdown syntax to the topic of the response(It is a must)
#         {combined_response}"""
        
#         final_response = await get_gemini_response(final_prompt)
#         memory.save_context({"input": prompt}, {"output": final_response})
#         return final_response    
#     else:
#         return await get_gemini_response(full_prompt)

# def is_election_or_politics_related(prompt):
#     # Creating SLM client
#     SLM = InferenceClient(
#         "mistralai/Mistral-7B-Instruct-v0.1",
#         token=os.getenv("HuggingFace_API_KEY"),
#     )

#     SLM_prompt = f"""
#     Determine if the following prompt is related to elections or politics in Sri Lanka.
#     Respond with 'Yes' if it is, and 'No' if it is not.
    
#     Prompt: {prompt}
#     """
        
#     start_time = time.time()
        
#     SLM_response = ""
#     for message in SLM.chat_completion(
#             messages=[{"role": "user", "content": SLM_prompt}],
#             max_tokens=10,
#             stream=True,
#         ):
#             content = message.choices[0].delta.content
#             if content:
#                 print(content, end="")
#                 SLM_response += content 

#     end_time = time.time()
#     process_time = end_time - start_time
        
#     print(f"\nSLM_response: {SLM_response.strip()}")
#     print(f"Process time: {process_time:.2f} seconds")

#     if "yes" in SLM_response.strip().lower():
#         return True
#     elif "no" in SLM_response.strip().lower():
#         return False
#     else:
#         print(f"Unexpected SLM response: {SLM_response}")
#         return False

# async def compare_candidates(candidates, LLAMA_client, tavily_client, candidate_vector_stores):
#     if candidate_vector_stores is None:
#         print("Failed to create or retrieve candidate vector stores.")
#         return

#     async def get_candidate_response(candidate, prompt):
#         if candidate not in candidate_vector_stores:
#             return f"No data available for {candidate}."
        
#         sections = [
#             "Economic Policy and Growth Strategies",
#             "Education Reform and Innovation",
#             "Energy and Sustainability",
#             "Healthcare System and Public Health",
#             "National Security and Defense",
#             "Legal Framework and Judicial Reform",
#             "Transportation and Mobility",
#             "Infrastructure Development and Modernization",
#             "Foreign Policy and International Relations"
#         ]
        
#         async def get_section_context(section):
#             return await retrieve_context(f"{section} {prompt}", candidate_vector_stores[candidate], top_k=10)
        
#         section_contexts = await asyncio.gather(*[get_section_context(section) for section in sections])
#         context = "\n".join(f"{section}:\n{context}\n" for section, context in zip(sections, section_contexts))

#         full_prompt = f"""Context (from {candidate}'s manifesto): {context}

#         Question: {prompt}

#         Instructions:
#         1. Analyze the provided context for each section extracted from {candidate}'s manifesto.
#         2. Summarize the specific policies and approaches mentioned for each section.
#         3. If a section is not addressed, state "No specific information available".
#         4. Provide a concise answer, focusing on key points.
#         5. Include important numerical data, targets, or timelines if mentioned.
#         6. Highlight any unique or standout policies."""
        
#         completion = await LLAMA_client.chat.completions.create(
#             model="meta/llama-3.1-405b-instruct",
#             messages=[{"role": "user", "content": full_prompt}],
#             temperature=0.3,
#             top_p=0.4,
#             max_tokens=4096
#         )
#         return completion.choices[0].message.content

#     prompt = """Summarize the key policies and approaches in the manifesto for this candidate
#     on the following sections:
#     1. Economic Policy and Growth Strategies
#     2. Education Reform and Innovation
#     3. Energy and Sustainability
#     4. Healthcare System and Public Health
#     5. National Security and Defense
#     6. Legal Framework and Judicial Reform
#     7. Transportation and Mobility
#     8. Infrastructure Development and Modernization
#     9. Foreign Policy and International Relations
#     Provide a brief overview for each policy area, focusing on main points and any unique initiatives."""
    
#     responses = await asyncio.gather(*[get_candidate_response(candidate, prompt) for candidate in candidates])
#     responses = dict(zip(candidates, responses))

#     policies_string = "".join(f"{candidate}'s policies:\n{response}\n\n" for candidate, response in responses.items())

#     comparison_prompt = f"""
#     Compare the following policies and approaches from {', '.join(candidates)}:

#     {policies_string}

#     Instructions:
#     1. Provide a concise comparison in a table format, highlighting key differences and similarities.
#     2. Include all nine policy areas for each candidate.
#     3. Use 'No data available' for missing information.
#     4. Add a brief section for common policies among all candidates.
#     5. Highlight unique or innovative policies for each candidate.
#     6. Include a short analysis of each candidate's overall focus and priorities.
#     7. Keep the comparison focused on the most important points from the provided responses.

#     Comparison should cover these sections:
#     1. Economic Policy and Growth Strategies
#     2. Education Reform and Innovation
#     3. Energy and Sustainability
#     4. Healthcare System and Public Health
#     5. National Security and Defense
#     6. Legal Framework and Judicial Reform
#     7. Transportation and Mobility
#     8. Infrastructure Development and Modernization
#     9. Foreign Policy and International Relations
#     """
    
#     comparison = await generate_response(comparison_prompt, LLAMA_client, tavily_client, candidate_vector_stores[candidates[0]], None, 0, None, None)
#     return comparison

# # if __name__ == "__main__":
# #     import asyncio
    
# #     async def main():
# #         LLAMA_client, tavily_client, memory, gemini_model, openai_client = initialize_clients()
# #         vector_store = create_vector_db()
# #         if vector_store is None:
# #             print("Failed to create vector store.")
# #             return
# #         prompt = "When is the next election in Sri Lanka?"
# #         response = await generate_response(prompt, LLAMA_client, tavily_client, vector_store, memory, 1, gemini_model, openai_client)
# #         print(response)
        
# #         # candidate_vector_stores = create_candidate_vector_stores()
# #         # candidates = ["Sajith", "Ranil", "Anura", "Namal", "Dilith"]
# #         # comparison = await compare_candidates(candidates, LLAMA_client, tavily_client, candidate_vector_stores)
# #         # print("\nComparison of candidates' manifestos:")
# #         # print(comparison)
        
# #         # Debug information
# #         # print("\nDebug Information:")
# #         # for candidate, store in candidate_vector_stores.items():
# #         #     if store:
# #         #         print(f"{candidate}: Vector store created with {len(store.index_to_docstore_id)} documents")
# #         #     else:
# #         #         print(f"{candidate}: No vector store created")
    
# #     asyncio.run(main())