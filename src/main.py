from setup import read_json_file, group_by_company_id
from scraper import NewsService
from generator import ReportGenerator
import os


if __name__ == "__main__":
    # Get the path to clients.json
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clients.json')

    # Read in the file and group the clients by company ID
    clients = read_json_file(json_file_path)
    company_jobs = group_by_company_id(clients)

    service = NewsService()
    gen = ReportGenerator()

    for company_id, jobs in company_jobs.items():
        print(f"Company ID: {company_id}")
        data = []

        for job in jobs:
            news = service.fetch_client_news(job['name']) #TODO still need to add to news_items
            print(news)

            data.append({
                "name": job['name'],
                "website": job['website'],
                "address": job['address'],
                "news_items": [
                    {
                        "title": "Patagonia opens new regional hub",
                        "link": "https://example.com",
                        "summary": "Expanding physical footprint in the Pacific Northwest.",
                        "why_it_matters": "They will likely need sustainable interior design consulting.",
                        "angle": "Have you considered how your new hub reflects your Net Zero goals?"
                    }
                ]
            })

        gen.generate_company_report(company_id, data)
