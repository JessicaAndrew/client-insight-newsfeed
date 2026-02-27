import json
import os
from collections import defaultdict


def read_json_file(file_path):
    """ Read and parse a JSON file
    
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            dict or list: Parsed JSON data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


def group_by_company_id(clients):
    """ Group client records by their company ID
    
        Removes the companyId and companyRank fields from each entry
        
        Args:
            clients (list): List of client dictionaries, each with a 'companyId' field
            
        Returns:
            dict: Dictionary mapping company IDs to lists of client details
    """
    company_jobs = defaultdict(list)

    for client in clients:  # Parse all clients by companyId
        company_id = client['companyId']
        job_details = {key: value for key, value in client.items() if key != 'companyId' or key != 'companyRank'}
        company_jobs[company_id].append(job_details)

    company_jobs = dict(company_jobs)  # Convert back to a standard dict
    
    return company_jobs
