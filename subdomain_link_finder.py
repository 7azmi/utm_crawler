import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import threading
from queue import Queue

class DomainMapper:
    def __init__(self, base_url, max_workers=10):
        self.base_url = base_url.rstrip("/")  # Fix base URL
        self.visited = set()
        self.lock = threading.Lock()
        self.queue = Queue()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def get_links(self, url):
        """Fetch and parse links from a given URL."""
        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            print(f"[DEBUG] {url} -> Status Code: {response.status_code}")  # Debug
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")  # Show error
            return set()

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, a_tag["href"])  # Fix URL joining
            parsed_url = urlparse(full_url)

            # Ensure link belongs to the same domain
            if parsed_url.netloc == urlparse(self.base_url).netloc:
                links.add(full_url)

        return links

    def crawl(self):
        """Worker function for crawling URLs."""
        while True:
            url = self.queue.get()
            if url is None:
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

            self.queue.task_done()

    def start_crawling(self):
        """Entry point for crawling."""
        self.queue.put(self.base_url)

        # Start worker threads
        workers = [self.executor.submit(self.crawl) for _ in range(self.executor._max_workers)]

        self.queue.join()

        # Stop workers
        for _ in range(self.executor._max_workers):
            self.queue.put(None)

        self.executor.shutdown(wait=True)

# Fixed usage
corrected_url = "https://digital.utm.my/"  # Remove extra "https://"
mapper = DomainMapper(corrected_url, max_workers=100)
mapper.start_crawling()

# Print collected links
print("\nAll links found:")
for link in sorted(mapper.visited):
    print(link)
