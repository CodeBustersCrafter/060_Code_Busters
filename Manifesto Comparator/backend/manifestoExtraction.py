import os
import asyncio
from main import initialize_client, create_vector_db, generate_response

# Start Generation Here
async def generate_comparison_manifesto():
    try:
        client = initialize_client()
        vector_store = create_vector_db()
        if vector_store is None:
            print("Failed to create vector store.")
            return

        manifest_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "manifest.txt")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_text = f.read()

        # Split the manifest_text by 'Candidate: ' to separate each candidate's manifesto
        sections = manifest_text.split("Candidate: ")
        candidates = []

        for section in sections:
            if section.strip() == "":
                continue
            lines = section.strip().split("\n")
            candidate_name = lines[0].strip()
            manifesto = "\n".join(lines[1:]).strip()
            candidates.append((candidate_name, manifesto))

        comparison_data = ""
        MAX_CHAR_LIMIT = 10000  # Adjust based on approximate token limit

        for candidate_name, manifesto in candidates:
            # Split manifesto into chunks if it exceeds the character limit
            manifesto_chunks = [manifesto[i:i + MAX_CHAR_LIMIT] for i in range(0, len(manifesto), MAX_CHAR_LIMIT)]
            candidate_comparison = ""

            for chunk in manifesto_chunks:
                prompt = f"Analyze the following manifesto segment and extract the main policies and their details:\n\n{chunk}"
                try:
                    response = await generate_response(prompt, client, vector_store)
                    candidate_comparison += f"{response}\n"
                except Exception as e:
                    print(f"An error occurred while processing {candidate_name}: {e}")
                    continue  # Skip to the next chunk or candidate as appropriate

            comparison_data += f"=== {candidate_name} ===\n{candidate_comparison.strip()}\n\n"

        compared_manifesto_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "compared_manifesto.txt")
        with open(compared_manifesto_path, "w", encoding="utf-8") as f:
            f.write(comparison_data)

        print("compared_manifesto.txt has been generated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(generate_comparison_manifesto())

