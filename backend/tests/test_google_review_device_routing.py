from backend.app.services.device_detection import get_google_review_url


class BusinessStub:
    google_review_pc_url = "https://example.com/pc"
    google_review_mob_url = "https://example.com/mobile"


def test_desktop_returns_pc_url():
    url, device = get_google_review_url(BusinessStub(), "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140 Safari/537.36")
    assert url == "https://example.com/pc"
    assert device == "desktop"


def test_iphone_returns_mobile_url():
    url, device = get_google_review_url(BusinessStub(), "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1")
    assert url == "https://example.com/mobile"
    assert device == "mobile"


def test_android_tablet_returns_mobile_url():
    url, device = get_google_review_url(BusinessStub(), "Mozilla/5.0 (Linux; Android 14; SM-X800) AppleWebKit/537.36 Chrome/140 Safari/537.36")
    assert url == "https://example.com/mobile"
    assert device == "mobile"


def test_ipad_returns_mobile_url():
    url, device = get_google_review_url(BusinessStub(), "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1")
    assert url == "https://example.com/mobile"
    assert device == "mobile"


def test_unknown_defaults_to_mobile_url():
    url, device = get_google_review_url(BusinessStub(), None)
    assert url == "https://example.com/mobile"
    assert device == "mobile"
