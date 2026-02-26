from GoogleNews import GoogleNews
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional
import random


class NewsService:
    def __init__(self, period='30d'):
        self.gn = GoogleNews(lang='en', region='US', period=period)  # Period defines how far back to look
        
    def fetch_client_news(self, client_name, max_retries: int = 3, fetch_full: bool = False, max_content_chars: int = 2000):
        """ Searches for news, specifically targeting business growth or architectural triggers.

            The underlying GoogleNews library will occasionally return HTTP 429 responses
            when the service is hit too quickly.  We implement a simple retry loop with
            exponential backoff and a small fixed jitter so that a long list of clients
            does not immediately exhaust the quota.
        """
        self.gn.clear()  # Avoid mixing results from previous searches

        # Build a comprehensive search query targeting business opportunities for architects
        query = (
            f'"{client_name}" (expansion OR "new office" OR headquarters OR funding OR '  
            "investment OR acquisition OR merger OR partnership OR \"strategic alliance\" "
            "OR \"joint venture\" OR \"product launch\" OR \"new service\" OR IPO "
            "OR restructuring OR \"leadership change\" OR CEO OR CIO OR \"real estate\" "
            "OR \"office space\" OR relocation OR hiring OR \"talent acquisition\" "
            "OR award OR recognition OR enterprise OR infrastructure OR technology OR digital "
            "OR innovation OR \"business development\" OR contract OR government)"
        )

        attempt = 0
        while attempt < max_retries:
            try:
                self.gn.search(query)
                results = self.gn.results()

                # If no specific results, try a broader search for the client
                if not results:
                    self.gn.clear()
                    self.gn.search(f'"{client_name}"')
                    results = self.gn.results()

                # Optionally fetch full article text for each result (best-effort)
                if fetch_full and results:
                    for r in results:
                        link = r.get('link')
                        if link:
                            try:
                                text = self._fetch_full_text(link)
                                if text:
                                    r['content'] = text[:max_content_chars]
                            except Exception:
                                continue  # don't fail the entire flow if fetching a single article fails

                return self._clean_results(results)
            except Exception as e:
                message = str(e)
                if '429' in message or 'Too Many Requests' in message:
                    wait = (2 ** attempt) * 5  # 5, 10, 20 ... seconds
                    print(
                        f"Rate limited searching for {client_name} (attempt {attempt + 1}), "
                        f"sleeping {wait}s before retrying..."
                    )
                    time.sleep(wait)
                    attempt += 1
                    continue
                else:
                    print(f"Error searching for {client_name}: {e}")
                    return []

        # if we get here, retries exhausted
        print(
            f"Failed to retrieve news for {client_name} after {max_retries} "
            "retries due to rate limits."
        )
        return []

    def _clean_results(self, raw_results):
        """ Formats the library output into a cleaner dictionary for the LLM """
        formatted = []

        for item in raw_results[:5]: # Only keep top 5 news items to keep LLM tokens low
            formatted.append({
                "title": item.get('title'),
                "media": item.get('media'),  # Source/publisher
                "date": item.get('date'),
                "description": item.get('desc'),  # Snippet of article
                "content": item.get('content'),  # include any fetched full article content (trimmed) so downstream
                "link": item.get('link')
            })

        return formatted

    def _fetch_full_text(self, url: str, timeout: int = 10):
        """ Best-effort extractor for the main article text from a URL """
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ClientInsightBot/1.0; +https://example.com)"
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Prefer semantic article/main tags
        article_tag = soup.find('article') or soup.find('main')
        if article_tag:
            texts = [p.get_text(strip=True) for p in article_tag.find_all('p')]
            body = "\n\n".join([t for t in texts if t])
            if body:
                return body

        # Fallback: grab visible paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        body = "\n\n".join([t for t in paragraphs if t])
        return body or None


    def run_through_clients(self, clients):
        """ Main method to run through all clients and fetch news.

            Includes additional throttling logic so the script can process large
            lists without immediately triggering a 429 error from Google.
        """
        all_news = {}

        for idx, client in enumerate(clients, start=1):
            name = client['name']
            print(f"Fetching news for {name} ({idx}/{len(clients)})...")
            news = self.fetch_client_news(name)
            all_news[name] = news

            # Basic per-client pause with a small random jitter
            time.sleep(random.uniform(1, 3))

            # After every fifty queries pause for a fuller cooldown period
            if idx % 50 == 0:
                print("Reached 50 requests; taking a 60-second break to avoid rate limits.")
                time.sleep(60)

        return all_news
