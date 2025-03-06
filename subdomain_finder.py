import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import threading
from queue import Queue

class DomainMapper:
    def __init__(self, base_url, max_depth=3, max_workers=10):
        self.base_url = base_url.rstrip("/")
        self.max_depth = max_depth  # Limit how deep we crawl
        self.visited = {}  # Track visited URLs with their depth
        self.subdomains = set()
        self.lock = threading.Lock()
        self.queue = Queue()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def get_links(self, url):
        """Fetch and parse links from a given URL."""
        try:
            response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except requests.RequestException:
            return set()

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, a_tag["href"])
            parsed_url = urlparse(full_url)

            # Ensure the link belongs to the same domain and is not already visited
            if parsed_url.netloc.endswith("utm.my") and full_url not in self.visited:
                links.add(full_url)

        return links

    def crawl(self):
        """Worker function for crawling URLs."""
        while True:
            item = self.queue.get()  # Get the next (URL, depth) from the queue
            if item is None:
                break

            url, depth = item
            if depth > self.max_depth:
                self.queue.task_done()
                continue

            with self.lock:
                if url in self.visited and self.visited[url] <= depth:
                    self.queue.task_done()
                    continue
                print(f"Visiting (Depth {depth}): {url}")
                self.visited[url] = depth

            links = self.get_links(url)

            # Add new links to the queue with increased depth
            with self.lock:
                for link in links:
                    if link not in self.visited:
                        self.queue.put((link, depth + 1))

            # Extract subdomains
            parsed_url = urlparse(url)
            if parsed_url.netloc.endswith("utm.my"):
                subdomain = parsed_url.netloc.split(".")[0]
                self.subdomains.add(subdomain)

            self.queue.task_done()

    def start_crawling(self):
        """Entry point for crawling."""
        self.queue.put((self.base_url, 0))  # Start with depth 0

        # Start worker threads
        workers = [self.executor.submit(self.crawl) for _ in range(self.executor._max_workers)]

        self.queue.join()  # Wait for the queue to be empty

        # Stop workers
        for _ in range(self.executor._max_workers):
            self.queue.put(None)
        self.executor.shutdown(wait=True)

# Usage
mapper = DomainMapper("https://www.utm.my/", max_depth=2, max_workers=200) # 2 as depth is best for subdomain finding
mapper.start_crawling()

# Print collected subdomains
print("\nAll subdomains found:")
for subdomain in sorted(mapper.subdomains):
    print(f"{subdomain}.utm.my")
