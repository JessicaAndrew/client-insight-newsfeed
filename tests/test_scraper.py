import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.scraper import NewsService


def test_clean_results_formats_and_limits_items():
    svc = NewsService()

    # Build synthetic raw results with more than 5 items
    raw = []
    for i in range(8):
        raw.append({
            'title': f'Title {i}',
            'media': f'Source {i}',
            'date': f'2025-01-{i+1:02d}',
            'desc': f'Description {i}',
            'link': f'http://example.com/{i}'
        })

    formatted = svc._clean_results(raw)

    # Should only keep top 5
    assert len(formatted) == 5

    # Each item should have expected keys and map desc to description
    for item in formatted:
        assert 'title' in item
        assert 'media' in item
        assert 'date' in item
        assert 'description' in item
        assert 'link' in item
