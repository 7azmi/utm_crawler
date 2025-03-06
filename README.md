# UTM Crawler

A specialized web crawler for mapping and organizing links from Universiti Teknologi Malaysia (UTM) websites.

## Project Overview

UTM Crawler is designed to discover, crawl, and organize the web ecosystem of Universiti Teknologi Malaysia. It systematically maps subdomains, extracts links, and organizes them into a hierarchical structure for analysis and reference.

## Features

- **Subdomain Discovery**: Automatically finds UTM subdomains by crawling from the main website
- **Link Extraction**: Collects all links within specific subdomains
- **Hierarchical Organization**: Organizes links in a structured JSON format
- **Concurrent Processing**: Uses multi-threading for efficient crawling
- **Error Handling**: Implements retries and proper error management

## Components

### Python Scripts

- `subdomain_finder.py`: Discovers subdomains within the utm.my domain
- `subdomain_link_finder.py`: Crawls a specific subdomain to collect all links
- `link_organizer.py`: Processes and organizes collected links into hierarchical JSON structures

### Data

- `data_unstructured/`: Contains raw URL data in text files
- `domains/`: Stores processed links in JSON format, organized by subdomain

## Usage

### Finding Subdomains

```python
# Discover UTM subdomains
python subdomain_finder.py
```

### Crawling a Specific Subdomain

```python
# Edit the URL in the script before running
python subdomain_link_finder.py
```

### Organizing Links

```python
# Process links from text files into JSON structures
python link_organizer.py
```

## Requirements

- Python 3.6+
- Beautiful Soup 4
- Requests

Install dependencies:
```
pip install -r requirements.txt
```

## Notes

- The crawler respects server load by using appropriate timeouts and retry mechanisms
- Some domains may have access restrictions or performance issues as noted in the process notes
