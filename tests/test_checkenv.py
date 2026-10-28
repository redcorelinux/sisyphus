import pytest
import sisyphus.checkenv


@pytest.mark.parametrize('url', [
    'https://redcorelinux.org',
    'http://mirror.alpix.eu/redcorelinux/amd64/packages/',
    'https://example.com:8080/path',
])
def test_is_valid_url_accepts(url):
    assert sisyphus.checkenv.is_valid_url(url)


@pytest.mark.parametrize('url', [
    '',
    'redcorelinux.org',
    'ftp://redcorelinux.org',
    'https://localhost',
    'https://redcorelinux.org extra',
])
def test_is_valid_url_rejects(url):
    assert not sisyphus.checkenv.is_valid_url(url)
