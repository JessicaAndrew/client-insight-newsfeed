import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.generator import ReportGenerator


def test_generate_company_report_creates_file_and_renders_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal template directory and template file
        template_dir = os.path.join(tmpdir, 'templates')
        os.makedirs(template_dir, exist_ok=True)

        template_path = os.path.join(template_dir, 'newsfeed_template.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""
            <html>
            <body>
            <h1>{{ company_name }}</h1>
            {% for c in clients %}
              <div class="client">
                <h2>{{ c.name }}</h2>
                {% for ni in c.news_items %}
                  <p>{{ ni.title }}</p>
                {% endfor %}
              </div>
            {% endfor %}
            <footer>{{ current_date }}</footer>
            </body>
            </html>
            """)

        output_dir = os.path.join(tmpdir, 'output')

        gen = ReportGenerator(template_dir=template_dir, output_dir=output_dir)

        company_name = "ABC Corporation"
        enriched = [
            {"name": "Client A", "news_items": [{"title": "Big Launch", "summary": "..."}]}
        ]

        result_path = gen.generate_company_report(company_name, enriched)

        assert os.path.exists(result_path)

        with open(result_path, 'r', encoding='utf-8') as f:
            contents = f.read()

        assert "ABC Corporation" in contents
        assert "Big Launch" in contents
