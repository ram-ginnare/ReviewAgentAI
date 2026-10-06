import re


def get_google_review_url(business, user_agent: str | None) -> tuple[str, str]:
    """Return (url, device_type). Unknown devices default to mobile."""
    ua = (user_agent or "").lower()

    # Tablets must use the mobile URL. iPadOS may identify itself as Mac.
    is_tablet = (
        "ipad" in ua
        or "tablet" in ua
        or ("macintosh" in ua and "mobile" in ua)
        or ("android" in ua and "mobile" not in ua)
    )
    is_mobile = bool(re.search(r"iphone|ipod|android.*mobile|windows phone|blackberry|bb10|opera mini|opera mobi", ua))

    if is_tablet or is_mobile:
        return business.google_review_mob_url, "mobile"

    is_desktop = bool(re.search(r"windows nt|macintosh|linux x86_64|x11|cros", ua))
    if is_desktop:
        return business.google_review_pc_url, "desktop"

    return business.google_review_mob_url, "mobile"
