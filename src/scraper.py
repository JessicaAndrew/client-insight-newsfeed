from GoogleNews import GoogleNews
import time


class NewsService:
    def __init__(self, period='30d'):
        self.gn = GoogleNews(lang='en', region='US', period=period)  # Period defines how far back to look
        
    def fetch_client_news(self, client_name):
        """ Searches for news, specifically targeting business growth or architectural triggers """
        self.gn.clear()  # Avoid mixing results from previous searches
        
        query = f'"{client_name}" (expansion OR "new office" OR "headquarters")'  # Build a targeted search query ## TODO expand this
        
        try:
            self.gn.search(query)
            results = self.gn.results()
            
            # If no specific results, try a broader search for the client
            if not results:
                self.gn.clear()
                self.gn.search(f'"{client_name}"')
                results = self.gn.results()

            return self._clean_results(results)
        except Exception as e:
            print(f"Error searching for {client_name}: {e}")
            return []

    def _clean_results(self, raw_results):
        """ Formats the library output into a cleaner dictionary for the LLM """
        formatted = []

        for item in raw_results[:5]: # Only keep top 5 news items to keep LLM tokens low
            formatted.append({
                "title": item.get('title'),
                "media": item.get('media'), # Source/publisher
                "date": item.get('date'),
                "description": item.get('desc'),  # Snippet of article
                "link": item.get('link')
            })

        return formatted

    def run_through_clients(self, clients):
        """ Main method to run through all clients and fetch news """
        all_news = {}

        for client in clients:
            name = client['name']
            print(f"Fetching news for {name}...")
            news = self.fetch_client_news(name)
            all_news[name] = news
            time.sleep(1)  # Sleep to avoid hitting rate limits

        return all_news
