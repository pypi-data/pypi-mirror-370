from urllib.parse import urljoin


def safe_join_url(base_url, path):
    return urljoin(base_url, path)
