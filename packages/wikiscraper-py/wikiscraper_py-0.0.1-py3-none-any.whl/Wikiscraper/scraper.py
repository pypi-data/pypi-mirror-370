"""
WikiScraper: Professional Python library to scrape Wikipedia articles.

Features:
- Scrape a single Wikipedia page or all linked articles recursively.
- Supports .txt and .csv output.
- Optionally add titles to scraped content.
- Logging options for file saves and all actions.
- Append all scraped articles into a single file or save separately.
- Handles multiple languages and errors gracefully.
"""

import os
import re
import time
import csv
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Set

class WikiScraper:
    """
    Wikipedia scraping utility.

    Parameters:
    -----------
    file_type : str
        Output file type: 'txt' or 'csv'. Default: 'txt'.
    add_title : bool
        Add article title at top of content. Default: False.
    log_saving : bool
        Log only file saving. Default: True.
    log_all : bool
        Log all actions, errors, and skips. Default: False.
    polite_time : int
        Delay between requests in seconds. Default: 3.
    all_on_one_file : bool
        Append all scraped articles into one file if scraping multiple pages. Default: True.
    """

    def __init__(self, file_type="txt", add_title=False, log_saving=True, log_all=False,
                 polite_time=3, all_on_one_file=True):
        self.file_type = file_type.lower()
        self.add_title = add_title
        self.log_saving = log_saving
        self.log_all = log_all
        self.polite_time = polite_time
        self.all_on_one_file = all_on_one_file

        if self.file_type not in ["txt", "csv"]:
            raise ValueError("file_type must be 'txt' or 'csv'")

        self.links: List[str] = []
        self.scraped_sites: Set[str] = set()
        self.invalid_links: List[str] = []
        self.base_dir = "data"
        os.makedirs(self.base_dir, exist_ok=True)

        if self.all_on_one_file:
            self.one_file_path = os.path.join(self.base_dir, f"wikipedia_all.{self.file_type}")
            if os.path.exists(self.one_file_path):
                os.remove(self.one_file_path)  # start fresh

    def _log(self, msg: str, force=False):
        if self.log_all or force:
            print(msg)

    def _get_language(self, url: str):
        """Detect language from URL using regex"""
        match = re.search(r"https://([a-z]{2})\.wikipedia\.org", url)
        return match.group(1) if match else "en"

    def _append_links(self, soup: BeautifulSoup, lang: str):
        """Append all valid Wikipedia links from page"""
        base_url = f"https://{lang}.wikipedia.org"
        skip_substrings = ["wiki/category", "wiki/special", "wiki/user", "wiki/talk", "wiki/help", "w/index.php"]

        for tag in soup.find_all("span", class_="mw-editsection"):
            tag.decompose()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            href_lower = href.lower()
            if any(skip in href_lower for skip in skip_substrings):
                continue
            if href.startswith("/wiki/"):
                full_url = base_url + href
            elif href.startswith("http") and f"{lang}.wikipedia.org" in href:
                full_url = href
            else:
                continue
            if full_url not in self.scraped_sites and full_url not in self.links:
                self.links.append(full_url)
                self._log(f"✅ Link added: {full_url}")

    def _clean_soup(self, soup: BeautifulSoup):
        """Remove unwanted tags and return clean text"""
        for tag in soup.find_all(["footer", "header", "title"]):
            tag.decompose()
        for tag in soup.find_all("div", class_=["printfooter", "pre-content heading-holder"]):
            tag.decompose()
        for tag in soup.find_all("span", class_="mw-editsection"):
            tag.decompose()
        for tag in soup.find_all("a", href="#bodyContent"):
            if "mw-jump-link" in tag.get("class", []):
                tag.decompose()
        for container_id in ["vector-toc-pinned-container", "vector-appearance", "vector-main-menu"]:
            container = soup.find("div", id=container_id)
            if container:
                container.decompose()
        for container_class in ["vector-page-toolbar-container", "vector-page-tools-pinnable-header"]:
            container = soup.find("div", class_=container_class)
            if container:
                container.decompose()
        site_sub = soup.find("div", id="siteSub")
        if site_sub:
            site_sub.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text)

    def _save_file(self, title: str, text: str):
        """Save article text to file(s) with improved logging and CSV handling"""
        safe_title = title.replace("/", "_").replace(" ", "-")
        
        if self.all_on_one_file:
            filepath = self.one_file_path
            display_name = title  # show title in log
        else:
            filepath = os.path.join(self.base_dir, f"{safe_title}.{self.file_type}")
            display_name = os.path.basename(filepath)  # show file name in log

        try:
            if self.file_type == "txt":
                mode = "a" if os.path.exists(filepath) else "w"
                with open(filepath, mode, encoding="utf-8") as f:
                    if self.add_title and not self.all_on_one_file:
                        f.write(f"{title}\n\n")
                    elif self.add_title and self.all_on_one_file:
                        f.write(f"{title}\n\n")
                    f.write(text + "\n\n")
            elif self.file_type == "csv":
                mode = "a" if os.path.exists(filepath) else "w"
                with open(filepath, mode, newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if self.add_title:
                        writer.writerow([title, text])
                    else:
                        writer.writerow([text])
            if self.log_saving:
                self._log(f"📄 Saved: {display_name}", force=True)
        except Exception as e:
            self._log(f"❌ Error saving {display_name}: {e}", force=True)

    def scrape_one(self, url: str):
        """Scrape a single Wikipedia page"""
        if not url.startswith("https://") or "wikipedia.org" not in url:
            self._log(f"❌ Invalid Wikipedia URL: {url}", force=True)
            return

        lang = self._get_language(url)
        try:
            self._log(f"Scraping: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self._log(f"❌ Failed to fetch {url}: {e}", force=True)
            self.invalid_links.append(url)
            return

        self._append_links(soup, lang)
        title_tag = soup.find("span", class_="mw-page-title-main")
        if not title_tag:
            self._log("❌ Title not found", force=True)
            return
        title = title_tag.text.strip()
        text = self._clean_soup(soup)
        self._save_file(title, text)
        self.scraped_sites.add(url)
        time.sleep(self.polite_time)

    def scrape_all(self, start_url: str):
        """Scrape starting page and recursively all linked articles"""
        self.links = [start_url]
        while self.links:
            url = self.links.pop(0)
            if url in self.scraped_sites:
                continue
            self.scrape_one(url)
