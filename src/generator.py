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

    def _company_file_path(self, company_name):
        """ Return the expected output file path for a given company """
        safe_filename = "".join([char for char in company_name if char.isalnum() or char in (' ', '_', '-')]).strip()
        return os.path.join(self.output_dir, f"{safe_filename.replace(' ', '_')}_newsfeed.html")

    def report_exists(self, company_name):
        """ Check whether a report for ``company_name`` already exists on disk """
        return os.path.exists(self._company_file_path(company_name))

    def generate_company_report(self, company_name, enriched_clients, *, skip_if_exists: bool = False):
        """ Creates a single HTML file for a specific company

            'enriched_clients': list of dictionaries
            'skip_if_exists': when True and the target file already exists, the
            method will do nothing and return ``None``. This allows callers to
            ignore companies for which an output file has already been
            generated (e.g. when resumed from a previous run).
        """
        # Clean the company name for a valid filename
        safe_filename = "".join([char for char in company_name if char.isalnum() or char in (' ', '_', '-')]).strip()
        file_path = os.path.join(self.output_dir, f"{safe_filename.replace(' ', '_')}_newsfeed.html")

        # If requested, skip generation when the file is already present.
        if skip_if_exists and os.path.exists(file_path):
            return None

        # Render the template with data and save
        html_content = self.template.render(
            company_name=company_name,
            clients=enriched_clients,
            current_date=datetime.now().strftime("%d/%m/%Y")
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return file_path
