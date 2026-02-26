from openai import OpenAI
from pydantic import BaseModel
from typing import List


# Define the structure the LLM must follow
class NewsInsight(BaseModel):
    title: str
    link: str
    summary: str
    why_it_matters: str
    angle: str


class ClientAnalysis(BaseModel):
    news_items: List[NewsInsight]


class EnrichmentEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def analyze_news(self, client_name, news_list):
        if not news_list:
            return []

        # Prepare the news for the prompt
        news_items = []
        
        for n in news_list:
            item = f"- {n['title']}: {n['description']}"

            if n.get('date'):
                item += f" [Date: {n['date']}]"
            
            if n.get('media'):
                item += f" [Source: {n['media']}]"
            
            news_items.append(item)
        
        news_context = "\n".join(news_items)

        prompt = f"""
        Analyze the following news for the company '{client_name}'. 
        Identify business opportunities for an architect.
        
        News:
        {news_context}
        """

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Keeps your $20 budget safe
            messages=[
                {"role": "system", "content": "You are a Business Development expert for architects. Spot growth, relocations, or sustainability needs."},
                {"role": "user", "content": prompt}
            ],
            response_format=ClientAnalysis,
        )

        # Return the parsed Pydantic objects as dicts
        return [item.model_dump() for item in completion.choices[0].message.parsed.news_items]
