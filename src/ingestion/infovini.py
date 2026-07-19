import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.infovini.com"
REGIONS_PAGE = f"{BASE_URL}/pagina.php?codNode=18012"
GRAPES_PAGE = f"{BASE_URL}/pagina.php?codNode=18017"
AJAX_CASTA = f"{BASE_URL}/ajax/castas.php"


def _get_soup(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        logger.warning("Failed to fetch Infovini page: %s", url, exc_info=True)
        return None


def fetch_wine_regions() -> list[dict]:
    soup = _get_soup(REGIONS_PAGE)
    if not soup:
        return []

    menu = soup.find("ul", id="menuLateral")
    if not menu:
        logger.warning("Could not find region menu on Infovini regions page")
        return []

    regions: list[dict] = []
    region_links: list[tuple[str, str]] = []

    active_item = menu.find("li", class_="activo")
    if active_item:
        parent_ul = active_item.find_parent("ul")
        if parent_ul:
            for li in parent_ul.find_all("li", recursive=False):
                link = li.find("a")
                if link and link.get("href"):
                    title = link.get("title", "")
                    href = link["href"]
                    cod_match = re.search(r"codNode=(\d+)", href)
                    if cod_match and title:
                        region_links.append((title, cod_match.group(1)))

    for name, cod_node in region_links:
        url = f"{BASE_URL}/pagina.php?codNode={cod_node}"
        region_soup = _get_soup(url)
        if not region_soup:
            regions.append({"name": name, "description": ""})
            continue

        content_div = region_soup.find("div", id="colconteudo")
        if content_div:
            description = content_div.get_text(separator="\n", strip=True)
        else:
            description = ""

        regions.append({"name": name, "description": description})
        logger.info("Fetched Infovini region: %s", name)

    return regions


def fetch_grape_varieties() -> list[dict]:
    soup = _get_soup(GRAPES_PAGE)
    if not soup:
        return []

    varieties: list[dict] = []
    seen: set[str] = set()

    for tab_panel in soup.find_all("div", class_="mootabs_panel"):
        panel_title = tab_panel.get("id", "")
        grape_type = "white" if "branc" in panel_title.lower() else "red"

        for link in tab_panel.find_all("a", href="#"):
            onclick = link.get("onclick", "")
            cod_match = re.search(r"x_getCasta\((\d+)", onclick)
            if not cod_match:
                continue

            name = link.get_text(strip=True)
            if not name or name in seen:
                continue
            seen.add(name)

            description = _fetch_grape_description(cod_match.group(1))
            varieties.append({
                "name": name,
                "description": description,
                "color": grape_type,
            })

    logger.info("Fetched %d grape varieties from Infovini", len(varieties))
    return varieties


def _fetch_grape_description(cod_casta: str) -> str:
    try:
        headers = {"Referer": GRAPES_PAGE}
        resp = requests.get(
            AJAX_CASTA,
            params={"codCasta": cod_casta},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        if not resp.text.strip():
            return ""

        xml_soup = BeautifulSoup(resp.text, "xml")
        casta = xml_soup.find("casta")
        if casta and casta.string:
            return casta.string.strip()
        return ""
    except requests.RequestException:
        logger.debug("Failed to fetch description for grape casta %s", cod_casta)
        return ""
    except Exception:
        logger.debug("Failed to parse description for grape casta %s", cod_casta)
        return ""


def fetch_all_infovini() -> list[dict]:
    documents: list[dict] = []

    regions = fetch_wine_regions()
    for region in regions:
        text = region.get("description", "")
        name = region.get("name", "Unknown")
        if not text:
            text = name

        documents.append({
            "id": f"infovini_region_{name.lower().replace(' ', '_').replace('ç', 'c')}",
            "text": text,
            "metadata": {
                "source": "infovini",
                "title": f"Wine Region: {name}",
                "language": "pt",
                "url": f"{BASE_URL}/pagina.php?codNode=18012",
                "region": name,
            },
        })

    varieties = fetch_grape_varieties()
    for variety in varieties:
        name = variety.get("name", "Unknown")
        description = variety.get("description", "")
        text = f"{name}: {description}" if description else name

        documents.append({
            "id": f"infovini_casta_{name.lower().replace(' ', '_').replace('ç', 'c')}",
            "text": text,
            "metadata": {
                "source": "infovini",
                "title": f"Grape: {name}",
                "language": "pt",
                "url": f"{BASE_URL}/pagina.php?codNode=18017",
            },
        })

    return documents
