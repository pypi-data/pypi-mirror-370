import pytest
from unittest.mock import Mock
from liveramp_automation.utils.playwright import PlaywrightUtils


@pytest.fixture
def mock_playwright_page():
    mock_page = Mock()
    mock_page.url = 'https://liveramp.com/careers/'
    mock_page.title = 'Liveramp'
    return mock_page


def test_save_screenshot(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.save_screenshot('test_screenshot')
    assert mock_playwright_page.screenshot.called


def test_navigate_to_url(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.navigate_to_url(scheme='https', host_name='example.com', path='/test', query='param=value')
    assert mock_playwright_page.goto.called
    mock_playwright_page.goto.assert_called_with('https://example.com/test?param=value')


def test_close_page_banner(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.close_popup_banner()
