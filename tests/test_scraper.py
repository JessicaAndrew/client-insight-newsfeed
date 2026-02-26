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


def test_fetch_client_news_rate_limit_retries(monkeypatch, capsys):
    svc = NewsService()

    # simulate GoogleNews.search always raising a 429-related exception
    def fake_search(query):
        raise Exception("HTTP Error 429: Too Many Requests")

    monkeypatch.setattr(svc.gn, 'search', fake_search)
    monkeypatch.setattr('time.sleep', lambda _s: None)  # avoid real sleeping

    result = svc.fetch_client_news("TestCorp", max_retries=2)
    assert result == []

    logged = capsys.readouterr().out
    assert "Rate limited searching for TestCorp" in logged
    assert "Failed to retrieve news for TestCorp" in logged


def test_run_through_clients_applies_throttling(monkeypatch):
    svc = NewsService()
    clients = [{'name': f'Client{i}'} for i in range(1, 4)]

    monkeypatch.setattr(svc, 'fetch_client_news', lambda name: [name])  # make fetch_client_news a no-op that returns a list

    sleeps = []

    def fake_sleep(sec):
        sleeps.append(sec)
    
    monkeypatch.setattr('time.sleep', fake_sleep)

    news = svc.run_through_clients(clients)
    assert news == {c['name']: [c['name']] for c in clients}
    assert len(sleeps) >= len(clients)  # we expect at least one uniform pause per client + maybe 60s at multiples of 50
