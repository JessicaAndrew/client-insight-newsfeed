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

def test_generate_company_report_skips_existing_file():
    # when skip_if_exists is True, an existing output file should not be overwritten and the method should return None
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = os.path.join(tmpdir, 'templates')
        os.makedirs(template_dir, exist_ok=True)
        template_path = os.path.join(template_dir, 'newsfeed_template.html')

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("<html><body>{{ company_name }}</body></html>")

        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(output_dir, exist_ok=True)

        company_name = "Existing Co"
        safe_filename = company_name.replace(' ', '_') + '_newsfeed.html'
        existing_path = os.path.join(output_dir, safe_filename)

        # create a dummy file to represent prior output
        with open(existing_path, 'w', encoding='utf-8') as f:
            f.write("original content")

        gen = ReportGenerator(template_dir=template_dir, output_dir=output_dir)
        returned = gen.generate_company_report(company_name, [], skip_if_exists=True)

        # nothing should have been written and result should be None
        assert returned is None
        with open(existing_path, 'r', encoding='utf-8') as f:
            assert f.read() == "original content"


def test_company_file_path_and_exists(tmp_path):
    """ New helper methods should compute path and detect existence correctly """
    template_dir = tmp_path / 'templates'
    template_dir.mkdir()
    (template_dir / 'newsfeed_template.html').write_text("<html></html>")
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    gen = ReportGenerator(template_dir=str(template_dir), output_dir=str(output_dir))
    company = "My Cool Co"

    # Construct expected filename manually
    expected = os.path.join(str(output_dir), "My_Cool_Co_newsfeed.html")
    assert gen._company_file_path(company) == expected
    
    # Doesn't exist yet
    assert not gen.report_exists(company)

    # Create the file and check again
    open(expected, 'w', encoding='utf-8').write("foo")
    assert gen.report_exists(company)
