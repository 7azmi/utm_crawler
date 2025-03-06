import json
import os
from urllib.parse import urlparse
from collections import defaultdict

class LinkOrganizer:
    def __init__(self, txt_files, output_dir="output"):
        self.txt_files = txt_files
        self.output_dir = output_dir
        self.hierarchical_data = defaultdict(lambda: defaultdict(dict))  # Store links hierarchically
        self.existing_data = {}  # Store existing JSON data for comparison

    def is_valid_url(self, url):
        """Check if the URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def normalize_url(self, url):
        """Normalize the URL by removing fragments and trailing slashes."""
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rstrip('/')}"

    def load_existing_json(self, domain_key):
        """Load existing JSON data if the file exists."""
        file_path = os.path.join(self.output_dir, f"{domain_key}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON file {file_path}")
        return {}

    def process_links(self):
        """Process links from the text files and organize them hierarchically."""
        for txt_file in self.txt_files:
            with open(txt_file, "r") as file:
                for line in file:
                    url = line.strip()
                    if not self.is_valid_url(url):
                        print(f"Skipping invalid URL: {url}")
                        continue  # Skip invalid URLs

                    normalized_url = self.normalize_url(url)
                    parsed_url = urlparse(normalized_url)
                    domain = parsed_url.netloc  # Extract domain (e.g., "utmscholar.utm.my")
                    path_parts = parsed_url.path.strip("/").split("/")  # Extract path parts

                    domain_key = domain.replace(".", "_")  # Convert domain to filename format
                    if domain_key not in self.existing_data:
                        self.existing_data[domain_key] = self.load_existing_json(domain_key)

                    # Build hierarchical structure
                    current_level = self.existing_data[domain_key]
                    new_entry = False
                    for part in path_parts:
                        if part not in current_level:
                            current_level[part] = {}
                            new_entry = True
                        current_level = current_level[part]

                    if new_entry:
                        print(f"Added new URL: {normalized_url}")
                    else:
                        print(f"Skipped (already exists): {normalized_url}")

    def save_to_json(self):
        """Save the hierarchical data to JSON files."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for domain_key, data in self.existing_data.items():
            output_file = os.path.join(self.output_dir, f"{domain_key}.json")
            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {output_file}")


# Example usage
if __name__ == "__main__":
    txt_files = ["data_unstructured/utmscholar.utm.my.txt"]
    organizer = LinkOrganizer(txt_files)
    organizer.process_links()
    organizer.save_to_json()
