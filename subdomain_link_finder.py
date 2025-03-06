import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import threading
from queue import Queue, Empty
import time


class DomainMapper:
    def __init__(self, base_url, max_workers=10):
        self.base_url = base_url.rstrip("/")  # Fix base URL
        self.visited = set()
        self.lock = threading.Lock()
        self.queue = Queue()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.stop_event = threading.Event()  # Stop signal for workers

    def should_skip_url(self, url):
        """Check if the URL points to a file type that should be skipped (e.g., PDFs, images)."""
        skip_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".zip", ".doc", ".docx", ".xls", ".xlsx"]
        return any(url.lower().endswith(ext) for ext in skip_extensions)

    def get_links(self, url, max_retries=1):
        """Fetch and parse links from a given URL with retries."""
        # Skip URLs that point to non-HTML resources
        if self.should_skip_url(url):
            print(f"[SKIP] Skipping non-HTML resource: {url}")
            return set()

        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                print(f"[DEBUG] {url} -> Status Code: {response.status_code}")  # Debugging

                if response.status_code != 200:
                    return set()  # Skip non-200 responses

                # Check Content-Type to ensure it's HTML
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type:
                    print(f"[SKIP] Skipping non-HTML content: {url} (Content-Type: {content_type})")
                    return set()

                response.raise_for_status()
                break  # Success, exit retry loop
            except requests.RequestException as e:
                print(f"[ERROR] Failed to fetch {url} (Attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2)  # Small delay before retrying
        else:
            return set()  # If max retries exceeded, return empty set

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
        while not self.stop_event.is_set():
            try:
                url = self.queue.get(timeout=10)  # Timeout to prevent infinite wait
            except Empty:
                break  # No more tasks, exit thread

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
        workers = []
        for _ in range(self.executor._max_workers):
            thread = threading.Thread(target=self.crawl, daemon=True)  # Daemon threads
            workers.append(thread)
            thread.start()

        # Wait for all workers
        for thread in workers:
            thread.join()

        self.executor.shutdown(wait=True)


# Fixed usage
corrected_url = "https://mech.utm.my/"  # Replace with the domain you want
mapper = DomainMapper(corrected_url, max_workers=20)  # Reduce max_workers to avoid server overload
mapper.start_crawling()

# Print collected links
print("\nAll links found:")
for link in sorted(mapper.visited):
    print(link)