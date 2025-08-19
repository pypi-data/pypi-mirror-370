import requests


def resolve_url(repo, source):
    """Construct the full URL from a repo namespace and source."""
    r = repo
    if not r.endswith(".git"):
        r += ".git"
    return "https://" + source.value + "/" + r

def download(url, into):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an error for bad responses
    with open(into, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
