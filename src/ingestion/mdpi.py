import logging
import os
import re
import zipfile

import pandas as pd

logger = logging.getLogger(__name__)

ZIP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "data-03-00009-s001.zip")
CSV_INSIDE_ZIP = "Supplementary files round#2/Supplem#1_round#2.csv"
MDPI_URL = "https://www.mdpi.com/2306-5729/3/1/9"

REGION_MAP = {
    "AÇOR": "Açores",
    "ALEN": "Alentejo",
    "ALGA": "Algarve",
    "TMAD": "Trás-os-Montes e Alto Douro",
    "MADE": "Madeira",
    "ESTR": "Estremadura",
    "RIBA": "Ribatejo",
    "BALT": "Beira Alta",
    "BBAI": "Beira Baixa",
    "BLIT": "Beira Litoral",
    "EDMI": "Entre Douro e Minho",
}


def _parse_ingredient_name(col_name: str) -> str:
    col_name = col_name.strip()
    m = re.match(r"I\d{3}\s+(.+)", col_name)
    if m:
        name = m.group(1)
        name = re.sub(r"\s*\(.*?\).*$", "", name).strip()
        return name
    return col_name


def fetch_mdpi_recipes() -> list[dict]:
    if not os.path.isfile(ZIP_PATH):
        logger.warning("MDPI zip not found at %s", ZIP_PATH)
        return []

    try:
        zf = zipfile.ZipFile(ZIP_PATH)
        fh = zf.open(CSV_INSIDE_ZIP)
        df = pd.read_csv(fh, encoding="latin1", low_memory=False)
        fh.close()
    except Exception:
        logger.exception("Failed to read MDPI CSV from zip")
        return []

    ingredient_cols = [c for c in df.columns[5:] if str(c).startswith(" I")]
    ingredient_names = [_parse_ingredient_name(c) for c in ingredient_cols]

    documents: list[dict] = []
    skipped = 0

    for idx, row in df.iterrows():
        code = str(row.iloc[0]).strip()
        name_pt = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""

        if not name_pt or name_pt == "nan":
            skipped += 1
            continue

        region = ""
        for prefix, region_name in REGION_MAP.items():
            if code.upper().startswith(prefix):
                region = region_name
                break

        used_ingredients = []
        for col_idx in range(len(ingredient_cols)):
            val = row.iloc[5 + col_idx]
            try:
                if float(val) == 1.0:
                    used_ingredients.append(ingredient_names[col_idx])
            except (ValueError, TypeError):
                pass

        text_parts = [f"Recipe: {name_pt}"]
        if region:
            text_parts.append(f"Region: {region}")
        if used_ingredients:
            text_parts.append("Ingredients: " + ", ".join(used_ingredients))

        text = "\n".join(text_parts)

        documents.append({
            "id": f"mdpi_{idx:04d}",
            "text": text,
            "metadata": {
                "source": "mdpi",
                "title": name_pt,
                "language": "pt",
                "url": MDPI_URL,
                "region": region,
                "recipe_name": name_pt,
            },
        })

    logger.info("Parsed %d recipes from MDPI dataset (skipped %d non-recipe rows)", len(documents), skipped)
    return documents
