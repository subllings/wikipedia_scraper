"""Unit tests for the WikipediaScraper class.

This module tests API interactions, data enrichment, and file export functionalities.
"""

from unittest.mock import Mock, patch

import pytest

from src.leaders_scraper import WikipediaScraper

"""
===============================================
Get get_countries method from WikipediaScraper
===============================================
"""


@patch("requests.Session.get")
def test_get_countries(mock_get: Mock):
    """Test that get_countries returns a list containing expected country codes."""
    # First call: for cookie
    mock_cookie_response = Mock()
    mock_cookie_response.cookies = {"session": "fake-cookie"}

    # Second call: for country list
    mock_country_response = Mock()
    mock_country_response.json.return_value = ["fr", "us", "de"]

    # Mock sequence of responses
    mock_get.side_effect = [mock_cookie_response, mock_country_response]

    # Run test
    scraper = WikipediaScraper()
    result = scraper.get_countries()

    assert isinstance(result, list)
    assert "fr" in result


"""
===============================================
get_leaders(country) method from WikipediaScraper
===============================================
"""


@patch("src.leaders_scraper.requests.Session.get")
def test_get_leaders_valid_country(mock_get: Mock):
    """Test that get_leaders returns a list of leaders for a valid country code."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {"first_name": "John", "last_name": "Doe", "wikipedia_url": "https://..."}
    ]
    mock_get.return_value = mock_response

    scraper = WikipediaScraper()
    leaders = scraper.get_leaders("fr")
    assert isinstance(leaders, list)
    assert leaders[0]["first_name"] == "John"


@patch("src.leaders_scraper.requests.Session.get")
def test_get_leaders_empty_list(mock_get: Mock):
    """Test that get_leaders returns an empty list for an unknown country code."""
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    scraper = WikipediaScraper()
    leaders = scraper.get_leaders("xx")
    assert leaders == []


@patch("src.leaders_scraper.requests.Session.get")
def test_get_leaders_invalid_json(mock_get: Mock):
    """Test that get_leaders raises ValueError when the response JSON is invalid."""
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

    scraper = WikipediaScraper()
    with pytest.raises(ValueError):
        scraper.get_leaders("fr")


"""
===============================================
get_first_paragraph(url) method from WikipediaScraper
===============================================
"""


@patch("requests.Session.get")
def test_get_first_paragraph_ignores_short(mock_get: Mock):
    """Test that get_first_paragraph returns an empty string for short paragraphs."""
    mock_get.return_value.text = "<html><p>Short.</p></html>"
    scraper = WikipediaScraper()
    paragraph = scraper.get_first_paragraph("http://fake.url")
    assert paragraph == ""


@patch("requests.Session.get")
def test_get_first_paragraph_strips_references(mock_get: Mock):
    """Test that get_first_paragraph removes reference markers from the paragraph."""
    html = "<html><p>This is a paragraph with [1] and [2].</p></html>"
    mock_get.return_value.text = html
    scraper = WikipediaScraper()
    paragraph = scraper.get_first_paragraph("http://fake.url")
    assert "[" not in paragraph


@patch("requests.Session.get")
def test_get_first_paragraph_empty_page(mock_get: Mock):
    """Test that get_first_paragraph returns an empty string when the page is empty."""
    mock_get.return_value.text = "<html></html>"
    scraper = WikipediaScraper()
    paragraph = scraper.get_first_paragraph("http://fake.url")
    assert paragraph == ""


"""
===============================================
enrich_leader method from WikipediaScraper
===============================================
"""


@patch.object(WikipediaScraper, "get_first_paragraph")
def test_enrich_leader_adds_summary(mock_get_para: Mock):
    """
    Test that enrich_leader adds a summary to the leader dictionary when a
    Wikipedia URL is present.

    This ensures the summary is properly parsed and attached to the dictionary.
    """
    mock_get_para.return_value = "A long summary about someone important."
    scraper = WikipediaScraper()
    leader = {"wikipedia_url": "http://wiki"}
    result = scraper.enrich_leader(leader)
    assert "summary" in result
    assert result["summary"].startswith("A long")


def test_enrich_leader_missing_url():
    """
    Test that enrich_leader does not add a summary when the Wikipedia URL is
    missing.
    """
    scraper = WikipediaScraper()
    leader = {"first_name": "NoURL"}
    result = scraper.enrich_leader(leader)
    assert "summary" not in result


@patch.object(WikipediaScraper, "get_first_paragraph")
def test_enrich_leader_empty_page(mock_get_para: Mock):
    """
    Test that enrich_leader sets an empty summary when get_first_paragraph
    returns an empty string.
    """
    mock_get_para.return_value = ""
    scraper = WikipediaScraper()
    leader = {"wikipedia_url": "http://wiki"}
    result = scraper.enrich_leader(leader)
    assert result["summary"] == ""


"""
===============================================
fetch_leaders() method test (replaces scrape_all)
===============================================
"""


@patch.object(WikipediaScraper, "get_countries", return_value=["fr"])
@patch.object(
    WikipediaScraper,
    "get_leaders",
    return_value=[{"wikipedia_url": "http://wiki"}],
)
@patch.object(
    WikipediaScraper,
    "enrich_all_leaders",
    return_value=[{"wikipedia_url": "http://wiki", "summary": "bio"}],
)
def test_fetch_leaders_basic(
    mock_enrich_all: Mock, mock_get_leaders: Mock, mock_get_countries: Mock
):
    """
    Test that fetch_leaders returns a dictionary with country codes as keys and
    enriched leader data.
    """
    scraper = WikipediaScraper()
    result = scraper.fetch_leaders(limit_per_country=1, verbose=False)
    assert "fr" in result
    assert "summary" in result["fr"][0]
