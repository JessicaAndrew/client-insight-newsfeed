from setup import read_json_file, group_by_company_id
from scraper import NewsService
import os


if __name__ == "__main__":
    # Get the path to clients.json
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clients.json')

    # Read in the file and group the clients by company ID
    clients = read_json_file(json_file_path)
    company_jobs = group_by_company_id(clients)

    service = NewsService()

    for company_id, jobs in company_jobs.items():
        print(f"Company ID: {company_id}")

        for job in jobs:
            print(f"  Job Name: {job['name']}")
            print(f"  website: {job['Website']}")
            print(f"  Address: {job['address']}")
            print(f"  News: {service.fetch_client_news(job['name'])}")
            print()
