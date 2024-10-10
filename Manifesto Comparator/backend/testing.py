from langchain_community.tools import DuckDuckGoSearchRun
import time

search = DuckDuckGoSearchRun()

max_retries = 3
retry_delay = 5

for attempt in range(max_retries):
    try:
        result = search.invoke("Obama's first name?")
        print(result)
        break
    except Exception as e:
        if "Ratelimit" in str(e):
            print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"An error occurred: {e}")
            break
else:
    print("Max retries reached. Unable to complete the search.")