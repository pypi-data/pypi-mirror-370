import pytest
from unittest.mock import Mock, patch, AsyncMock
from rust_crate_pipeline.scraping.unified_scraper import (
    UnifiedScraper,
    ScrapingResult,
)


@pytest.fixture
def mock_crawler():
    """Provides a mock crawler object for testing."""
    crawler = AsyncMock()
    crawler.arun.return_value = Mock(success=True, markdown="test markdown", extracted_content={})
    return crawler


@patch("rust_crate_pipeline.scraping.unified_scraper.AsyncWebCrawler")
def test_unified_scraper_initialization(mock_async_web_crawler):
    """Tests that the UnifiedScraper class initializes correctly."""
    scraper = UnifiedScraper()
    assert scraper.crawler is not None


@pytest.mark.asyncio
@patch("rust_crate_pipeline.scraping.unified_scraper.AsyncWebCrawler")
async def test_scrape_url(mock_async_web_crawler, mock_crawler):
    """Tests the scrape_url method."""
    mock_async_web_crawler.return_value = mock_crawler
    scraper = UnifiedScraper()
    result = await scraper.scrape_url("http://test.com")

    assert isinstance(result, ScrapingResult)
    assert result.content == "test markdown"


@pytest.mark.asyncio
@patch("rust_crate_pipeline.scraping.unified_scraper.AsyncWebCrawler")
async def test_scrape_crate_documentation(mock_async_web_crawler, mock_crawler):
    """Tests the scrape_crate_documentation method."""
    mock_async_web_crawler.return_value = mock_crawler
    scraper = UnifiedScraper()
    results = await scraper.scrape_crate_documentation("test-crate")

    assert isinstance(results, dict)
    assert "crates_io" in results
    assert "docs_rs" in results
    assert "lib_rs" in results
