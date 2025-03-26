import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
# Configure Gemini API (Replace with your API key)
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")  # Get the API key from an environment variable

# Select the Gemini model
MODEL_NAME = "gemini-2.0-flash"  # or another appropriate model from the docs

def analyze_links_with_gemini(urls):
    """Analyzes a list of URLs using Gemini API to determine useful ones for a UTM chatbot."""

    prompt = """
Analyze the following list of URLs and identify the URLs that are likely to be useful resources for a chatbot designed for Universiti Teknologi Malaysia (UTM) students and staff.

Consider these factors for each URL:

* Relevance to academics, student life, research, administration, or services at UTM.
* Potential to answer common questions from students and staff.
* Likelihood of containing valuable information, not just being a login page, error page, or temporary notice.
* The URL should only contain links related to UTM staffs, students, and professors and should not contain a user directory of UTM staff.

Return ONLY the URLs that you deem to be useful, one URL per line. Do not include any additional text, explanations, or labels. If no URLs are deemed useful, return an empty string.

URLs:
""" + "\n".join(urls)

    client = genai.Client(api_key=GOOGLE_API_KEY)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    try:
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text

        useful_links_string = response_text.strip()
        useful_links = useful_links_string.split('\n') if useful_links_string else []

        return useful_links

    except Exception as e:
        print(f"Error analyzing URLs: {e}")
        return []


def filter_links_gemini(input_file, output_file, chunk_size=300):  # Changed chunk_size to 200
    """Filters links from input_file using Gemini in chunks, writes useful links to output_file."""

    try:
        with open(input_file, 'r') as infile:
            all_urls = [line.strip() for line in infile]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading the input file: {e}")
        return

    useful_links = []
    for i in range(0, len(all_urls), chunk_size):
        chunk_urls = all_urls[i:i + chunk_size]
        print(f"Analyzing URLs: {chunk_urls}")  # Debug line
        chunk_useful_links = analyze_links_with_gemini(chunk_urls)
        useful_links.extend(chunk_useful_links)
        print(f"Found useful links: {chunk_useful_links}") #Debug line

    try:
        with open(output_file, 'w') as outfile:
            for link in useful_links:
                outfile.write(link + '\n')
        print(f"Filtered links written to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")


if __name__ == "__main__":
    input_file = "filtered_links.txt"
    output_file = "useful_links_gemini.txt"
    filter_links_gemini(input_file, output_file)