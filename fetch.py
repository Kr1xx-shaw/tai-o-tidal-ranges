# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Save the HKO reply unchanged once. Run with: uv run fetch.py."""
from pathlib import Path
from urllib.request import Request, urlopen

URL = (
    "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php"
    "?dataType=HHOT&station=TAO&year=2026&rformat=json"
)
FILE = "tides-TAO-2026.json"
DATA = Path(__file__).resolve().parent / "data"


def fetch():
    """Use the saved reply if present; otherwise preserve the response bytes."""
    path = DATA / FILE
    if path.exists():
        print(f"Using saved {path.name} ({path.stat().st_size:,} bytes); no request made.")
        return path
    request = Request(URL, headers={"User-Agent": "SD5913 student data visualisation"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    if not content:
        raise ValueError("HKO returned an empty reply; no file was saved.")
    DATA.mkdir(exist_ok=True)
    path.write_bytes(content)
    print(f"Saved raw reply to {path} ({len(content):,} bytes).")
    return path


if __name__ == "__main__":
    fetch()
