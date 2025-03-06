import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import threading
from queue import Queue
import re

class DomainMapper:
    def __init__(self, base_url, max_workers=10):
        self.base_url = base_url.rstrip("/")
        self.visited = set()
        self.subdomains = set()  # Store unique subdomains
        self.lock = threading.Lock()
        self.queue = Queue()  # Use a queue for BFS-style crawling
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def get_links(self, url):
        """Fetch and parse links from a given URL."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return set()

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(self.base_url, a_tag["href"])
            parsed_url = urlparse(full_url)

            # Ensure the link belongs to the same domain and is not already visited
            if parsed_url.netloc.endswith("utm.my"):  # Focus on UTM subdomains
                links.add(full_url)

        return links

    def crawl(self):
        """Worker function for crawling URLs."""
        while True:
            url = self.queue.get()  # Get the next URL from the queue
            if url is None:  # Sentinel value to stop the worker
                break

            with self.lock:
                if url in self.visited:
                    self.queue.task_done()
                    continue
                print(f"Visiting: {url}")
                self.visited.add(url)

            links = self.get_links(url)

            # Add unvisited links to the queue
            with self.lock:
                for link in links:
                    if link not in self.visited:
                        self.queue.put(link)

            # Extract subdomains from the current URL
            parsed_url = urlparse(url)
            if parsed_url.netloc.endswith("utm.my"):
                subdomain = parsed_url.netloc.split(".")[0]  # Extract subdomain (e.g., "civil" from "civil.utm.my")
                self.subdomains.add(subdomain)

            self.queue.task_done()

    def start_crawling(self):
        """Entry point for crawling."""
        self.queue.put(self.base_url)  # Start with the base URL

        # Start worker threads
        workers = [
            self.executor.submit(self.crawl)
            for _ in range(self.executor._max_workers)
        ]

        self.queue.join()  # Wait for the queue to be empty

        # Stop workers by sending sentinel values
        for _ in range(self.executor._max_workers):
            self.queue.put(None)

        self.executor.shutdown(wait=True)

# Usage
mapper = DomainMapper("https://utmspace.edu.my/", max_workers=300)
mapper.start_crawling()

# Print all collected subdomains
print("\nAll subdomains found:")
for subdomain in sorted(mapper.subdomains):
    print(f"{subdomain}.utm.my")