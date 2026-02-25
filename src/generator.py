from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, template_dir='templates', output_dir='output'):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template('newsfeed_template.html')
        self.output_dir = output_dir
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_company_report(self, company_name, enriched_clients):
        """ Creates a single HTML file for a specific company

            'enriched_clients': list of dictionaries
        """
        # Clean the company name for a valid filename
        safe_filename = "".join([char for char in company_name if char.isalnum() or char in (' ', '_', '-')]).strip()
        file_path = os.path.join(self.output_dir, f"{safe_filename.replace(' ', '_')}_newsfeed.html")

        # Render the template with data and save
        html_content = self.template.render(
            company_name=company_name,
            clients=enriched_clients,
            current_date=datetime.now().strftime("%d/%m/%Y")
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return file_path
