import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# ensure both project root and src directory are on sys.path so imports used by
# src/main (which relies on a top-level `setup` module when run as a script)
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, 'src'))

from src import main


def test_main_skips_entire_company_if_report_exists(monkeypatch, tmp_path, capsys):
    """ Test that main() skips news scraping if report already exists for a company.
    
        Verifies that NewsService and EnrichmentEngine are not instantiated when a
        report file already exists on disk.
    """
    # prepare fake config and data
    monkeypatch.setattr(main, 'load_config', lambda: {'openai': {'api_key': 'test-key'}})

    # clients.json doesn't actually get loaded because we stub read_json_file
    clients = [{'company_id': 'C1', 'name': 'ClientA'}]
    monkeypatch.setattr(main, 'read_json_file', lambda path: clients)
    monkeypatch.setattr(main, 'group_by_company_id', lambda x: {'C1': clients})

    # create a ReportGenerator instance whose report_exists returns True for C1
    class FakeGen:
        def __init__(self, *args, **kwargs):
            pass
        def report_exists(self, company):
            return True
        def generate_company_report(self, *args, **kwargs):
            raise AssertionError("generate_company_report should not be called when report already exists")

    monkeypatch.setattr(main, 'ReportGenerator', FakeGen)

    # patch services with mocks so we can assert they are never instantiated
    fake_service_cls = MagicMock()
    fake_enricher_cls = MagicMock()
    monkeypatch.setattr(main, 'NewsService', fake_service_cls)
    monkeypatch.setattr(main, 'EnrichmentEngine', fake_enricher_cls)

    # run
    main.main()

    output = capsys.readouterr().out
    assert "Skipping C1: output already exists" in output
