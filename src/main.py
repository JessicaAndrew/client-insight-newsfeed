import os
import time
import random
import json
import yaml

from setup import read_json_file, group_by_company_id
from scraper import NewsService
from processor import EnrichmentEngine
from generator import ReportGenerator


def load_config():
    # Construct path to config.yaml
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def main():
    # Setup paths and services
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clients.json')

    # Load configuration
    config = load_config()

    # Initialise your API key and generator (services will be created per-company
    # so that we can skip the heavy work entirely if a report already exists
    # for that company).
    OPENAI_API_KEY = config['openai']['api_key']
    gen = ReportGenerator()
    
    # Load Data
    clients = read_json_file(json_file_path)
    company_jobs = group_by_company_id(clients)  # Group the clients by company ID

    for company_id, jobs in company_jobs.items():
        print(f"\n--- Processing Company ID: {company_id} ---")

        # if we've already generated a report for this company, skip all work
        if gen.report_exists(company_id):
            print(f"Skipping {company_id}: output already exists")
            continue

        # services are only created when we actually start doing work for a
        # company. this prevents unnecessary HTTP connections or API client
        # initialisation when a report is already on disk.
        service = NewsService()
        enricher = EnrichmentEngine(api_key=OPENAI_API_KEY)

        company_feed_data = []

        for job in jobs:
            client_name = job['name']
            raw_news = []

            print(f"  Scrape Fetching news for {client_name}...")
            try:
                # Fetch full article text to give the LLM richer context (best-effort)
                raw_news = service.fetch_client_news(client_name, fetch_full=True)
                
                # Random delay: wait 3 to 10 seconds to avoid Google blocks
                time.sleep(random.uniform(3, 10)) 
            except Exception as e:
                print(f"  Error: Could not fetch news for {client_name}: {e}")
                if "429" in str(e):
                    print("Rate Limited: sleeping for 60 seconds")
                    time.sleep(60)
            
            # Enrich news using LLM if we found any
            if raw_news:
                print(f"  AI Analysing news for {client_name}...")
                enriched_news = enricher.analyze_news(client_name, raw_news)
                
                entry = {
                    "name": client_name,
                    "news_items": enriched_news
                }

                website = job.get('website') or job.get('Website')
                if website:
                    entry["website"] = website
                
                address = job.get('address') or job.get('Address')
                if address:
                    entry["address"] = address
                
                company_feed_data.append(entry)

        # Generate report for the company if they have news
        if company_feed_data:
            gen.generate_company_report(company_id, company_feed_data)
            print(f"Report generated for {company_id}")


if __name__ == "__main__":
    main()
