#!/usr/bin/env python3
"""
Daloopa Documentation Crawler
Crawls docs.daloopa.com and downloads all documentation pages in markdown format.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import json
from pathlib import Path
import html2text
import re

class DaloopaCrawler:
    def __init__(self, base_url="https://docs.daloopa.com", output_dir="daloopa_docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.to_visit = set()
        self.pages = []

        # Setup markdown converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap text

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.delay = 1  # seconds between requests

    def is_valid_docs_url(self, url):
        """Check if URL is a valid documentation page"""
        parsed = urlparse(url)

        # Must be from docs.daloopa.com
        if parsed.netloc != "docs.daloopa.com":
            return False

        # Skip non-documentation URLs
        skip_patterns = [
            '/discuss/',
            '/page/',
            '/changelog',
            '/suggest',
            '/reference/api',  # Skip auto-generated API reference for now
            '#'  # Skip anchor links
        ]

        for pattern in skip_patterns:
            if pattern in url:
                return False

        return True

    def get_page_content(self, url):
        """Fetch and parse a page"""
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, html, current_url):
        """Extract all documentation links from a page"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        # Find all links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(current_url, href)

            # Clean up URL (remove fragments)
            full_url = full_url.split('#')[0]

            if self.is_valid_docs_url(full_url):
                links.add(full_url)

        return links

    def extract_content(self, html, url):
        """Extract main content from a documentation page"""
        soup = BeautifulSoup(html, 'html.parser')

        # Find the main content area (ReadMe typically uses specific classes)
        main_content = (
            soup.find('article') or
            soup.find('main') or
            soup.find(class_=re.compile(r'content|markdown|documentation', re.I)) or
            soup.find('div', {'role': 'main'})
        )

        if not main_content:
            # Fallback: try to find body content
            main_content = soup.find('body')

        # Extract title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Convert to markdown
        if main_content:
            html_content = str(main_content)
            markdown_content = self.html_converter.handle(html_content)
        else:
            markdown_content = "No content found"

        # Extract metadata
        metadata = {
            'url': url,
            'title': title,
            'path': urlparse(url).path
        }

        return markdown_content, metadata

    def save_page(self, content, metadata):
        """Save a page to disk"""
        # Create a clean filename from the URL path
        path = metadata['path'].strip('/')
        if not path:
            path = 'index'

        # Replace slashes with underscores for filename
        filename = path.replace('/', '_') + '.md'
        filepath = os.path.join(self.output_dir, filename)

        # Prepare content with metadata header
        full_content = f"""---
title: {metadata['title']}
url: {metadata['url']}
path: {metadata['path']}
---

# {metadata['title']}

{content}
"""

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        print(f"Saved: {filepath}")

        return filepath

    def crawl(self, start_url=None):
        """Main crawling function"""
        if start_url is None:
            start_url = self.base_url

        self.to_visit.add(start_url)

        while self.to_visit:
            url = self.to_visit.pop()

            # Skip if already visited
            if url in self.visited_urls:
                continue

            # Mark as visited
            self.visited_urls.add(url)

            # Fetch page
            html = self.get_page_content(url)
            if not html:
                continue

            # Extract content
            content, metadata = self.extract_content(html, url)

            # Save page
            filepath = self.save_page(content, metadata)

            # Store page info
            self.pages.append({
                'url': url,
                'title': metadata['title'],
                'filepath': filepath,
                'path': metadata['path']
            })

            # Extract and queue new links
            links = self.extract_links(html, url)
            for link in links:
                if link not in self.visited_urls:
                    self.to_visit.add(link)

            # Rate limiting
            time.sleep(self.delay)

        # Save index
        self.save_index()

        print(f"\nCrawling complete! Downloaded {len(self.pages)} pages.")
        print(f"Output directory: {self.output_dir}")

    def save_index(self):
        """Save an index of all crawled pages"""
        index_file = os.path.join(self.output_dir, '_index.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages, f, indent=2)

        # Also create a human-readable markdown index
        md_index_file = os.path.join(self.output_dir, '_index.md')
        with open(md_index_file, 'w', encoding='utf-8') as f:
            f.write("# Daloopa Documentation Index\n\n")
            f.write(f"Total pages: {len(self.pages)}\n\n")

            # Group by section
            sections = {}
            for page in self.pages:
                path_parts = page['path'].strip('/').split('/')
                section = path_parts[0] if path_parts else 'root'
                if section not in sections:
                    sections[section] = []
                sections[section].append(page)

            for section, pages in sorted(sections.items()):
                f.write(f"## {section.title()}\n\n")
                for page in sorted(pages, key=lambda p: p['path']):
                    f.write(f"- [{page['title']}]({page['url']}) → {page['filepath']}\n")
                f.write("\n")

        print(f"Saved index: {md_index_file}")


def main():
    print("Daloopa Documentation Crawler")
    print("=" * 50)

    crawler = DaloopaCrawler()
    crawler.crawl()


if __name__ == "__main__":
    main()
