from collections import defaultdict
from urllib.parse import urlparse

# Read links from file
with open("all_links.txt", "r") as file:
    links = [line.strip() for line in file if line.strip()]

# Dictionary to store depth levels
depth_count = defaultdict(int)
# Set to store unique domains
domains = set()

for link in links:
    parsed_url = urlparse(link)
    domain = parsed_url.netloc
    path_depth = link.count("/") - 2  # Subtract 'https://' and domain slash

    domains.add(domain)
    depth_count[path_depth] += 1

# Print stats
print(f"Total unique domains: {len(domains)}")
print("Links per depth level:")
for depth, count in sorted(depth_count.items()):
    print(f"Depth {depth}: {count} links")
