import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.processor import EnrichmentEngine


def test_analyze_news_returns_empty_for_no_news():
    """ Test that analyze_news returns an empty list when given no news items
        
        Mock the OpenAI client to avoid requiring a real API key
    """
    with patch('src.processor.OpenAI'):
        engine = EnrichmentEngine(api_key="test-key")
        result = engine.analyze_news("Any Company", [])
        assert result == []
