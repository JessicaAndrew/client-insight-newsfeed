from openai import OpenAI
from pydantic import BaseModel
from typing import List
from math import ceil


# Define the structure the LLM must follow
class NewsInsight(BaseModel):
    """ Structured news insight extracted and analysed by the LLM
    
        Attributes:
            title (str): Headline of the news article
            link (str): URL to the original article
            summary (str): Brief summary of the news
            why_it_matters (str): Business relevance for architects
            angle (str): Specific opportunity angle
    """
    title: str
    link: str
    summary: str
    why_it_matters: str
    angle: str


class ClientAnalysis(BaseModel):
    """ Container for analysed news items for a client company
    
        Attributes:
            news_items (List[NewsInsight]): List of enriched news insights
    """
    news_items: List[NewsInsight]


class EnrichmentEngine:
    """ Enriches raw news articles with AI-powered business analysis
        
        Uses an OpenAI's model to analyze news articles and extract
        business opportunities relevant to architects.
    """
    
    def __init__(self, api_key):
        """Initialise the EnrichmentEngine with OpenAI API credentials.
        
        Args:
            api_key (str): OpenAI API key for authentication.
        """
        self.client = OpenAI(api_key=api_key)

    def analyze_news(self, client_name, news_list):
        """ Analyse a list of news articles and extract business insights.
        
            Uses OpenAI API with automatic chunking to handle token limits.
            Reduces chunk size on length errors and processes articles individually
            as a fallback.
            
            Args:
                client_name (str): Name of the company/client for contextual analysis.
                news_list (list): List of news dictionaries with title, description, content, date, media, and link.
                    
            Returns:
                list: List of dictionaries with analysed news insights.
        """
        if not news_list:
            return []

        def build_context(items):
            """ Build formatted context string from news items for the LLM """
            parts = []

            for n in items:
                item = f"- {n.get('title','(no title)')}: {n.get('description') or ''}"
                if n.get('content'):
                    excerpt = n['content'][:1200]
                    item += f"\nFull article excerpt: {excerpt}"
                if n.get('date'):
                    item += f" [Date: {n['date']}]"
                if n.get('media'):
                    item += f" [Source: {n['media']}]"
                parts.append(item)

            return "\n".join(parts)

        def call_llm_for_chunk(chunk):
            """ Call OpenAI API to analyse a chunk of news items
            
                Args:
                    chunk (list): Subset of news items to analyse
                    
                Returns:
                    list: Parsed news insights from LLM response
            """
            news_context = build_context(chunk)
            prompt = f"""
            Analyze the following news for the company '{client_name}'.
            Identify business opportunities for an architect.

            News:
            {news_context}
            """

            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Business Development expert for architects. Spot growth, relocations, or sustainability needs."},
                    {"role": "user", "content": prompt}
                ],
                response_format=ClientAnalysis,
            )

            # parsed pydantic model -> list of dicts
            if completion and getattr(completion, 'choices', None):
                parsed = completion.choices[0].message.parsed
                return [item.model_dump() for item in parsed.news_items]
            return []

        # Chunking strategy: try a reasonably large batch, shrink on length errors
        max_chunk_size = 20
        aggregated = []
        current_chunk = max_chunk_size

        def chunks(lst, n):
            """ Generator to yield successive chunks of n items from a list
            
                Args:
                    lst (list): List to chunk
                    n (int): Size of each chunk
                    
                Returns:
                    list: Successive chunks of size n
            """
            for i in range(0, len(lst), n):
                yield lst[i:i+n]

        while True:
            try:
                for ch in chunks(news_list, current_chunk):
                    aggregated.extend(call_llm_for_chunk(ch))
                break
            except Exception as e:
                # Detect token/length finish reason from the library error class or message
                name = e.__class__.__name__
                msg = str(e).lower()
                if 'lengthfinishreasonerror' in name.lower() or 'length' in msg or 'limit' in msg:
                    if current_chunk <= 1:
                        # As a last resort call the LLM per article
                        aggregated = []
                        for item in news_list:
                            try:
                                aggregated.extend(call_llm_for_chunk([item]))
                            except Exception:
                                # If even single article fails, skip it
                                continue
                        break
                    # halve chunk size and retry
                    current_chunk = max(1, current_chunk // 2)
                    continue

        return aggregated
