import json
import os
from collections import defaultdict

def flatten_hierarchical_data(data, base_url):
    """Recursively flatten hierarchical data into a list of URLs."""
    urls = []
    for key, value in data.items():
        current_url = f"{base_url}/{key}" if base_url else key
        urls.append(current_url)
        if value:  # If there are nested paths, recurse
            urls.extend(flatten_hierarchical_data(value, current_url))
    return urls

def json_to_links(input_dir, output_file):
    """Convert JSON files in the input directory to a single text file of links."""
    if not os.path.exists(input_dir):
        print(f"❌ Directory '{input_dir}' does not exist.")
        return

    all_links = set()  # Use a set to avoid duplicate links

    # Iterate over all JSON files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            print(f"📂 Processing file: {file_path}")

            # Load JSON data
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Could not decode JSON file {file_path}")
                    continue

            # Extract domain from filename (e.g., "utmscholar_utm_my.json" -> "utmscholar.utm.my")
            domain = filename.replace("_", ".").replace(".json", "")

            # Flatten the hierarchical data into URLs
            urls = flatten_hierarchical_data(data, f"https://{domain}")
            all_links.update(urls)  # Add URLs to the set

    # Write all links to the output file
    with open(output_file, "w") as f:
        for link in sorted(all_links):  # Sort links alphabetically
            f.write(link + "\n")

    print(f"💾 Links saved to {output_file}")
    print(f"📊 Total links extracted: {len(all_links)}")

# Example usage
if __name__ == "__main__":
    input_dir = "domains"  # Directory containing JSON files
    output_file = "all_links.txt"  # Output text file
    json_to_links(input_dir, output_file)