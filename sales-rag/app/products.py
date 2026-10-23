from typing import Dict, Any, Optional, List, Tuple
import re

# ---------------------------------------------------------------------------
# Comprehensive Product catalog built from the 13 approved datasheets.
# ---------------------------------------------------------------------------
PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "brightspace": {
        "family": "BrightSpace",
        "category": "downlight",
        "subcategory": "architectural",
        "aliases": [
            "brightspace", "bright space", "brightspace downlight",
            "bs-series", "bs series"
        ],
        "source_files": ["BrightSpace.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["5W", "10W", "20W"],
        "cct": ["2700K", "3000K", "3500K", "4000K"],
        "cri": ">90",
        "beam_angle": ["15°", "24°", "36°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "50,000 hours @ L70",
        "warranty": "Lifetime*",
    },
    "eco_downlight": {
        "family": "Eco Downlight",
        "category": "downlight",
        "subcategory": "commercial",
        "aliases": [
            "eco downlight", "eco-downlight", "eco dl", "eco down light",
            "ecodownlight", "ed-12"
        ],
        "source_files": ["Eco-Downlight.pdf"],
        "operating_voltage_max": 265,
        "input_voltage": "AC105-265V (7W), AC135-265V (12W), AC155-265V (18W)",
        "dimming": [],
        "power_consumption": ["7W", "12W", "18W"],
        "cct": ["3000K", "4000K", "6500K"],
        "cri": ">80",
        "beam_angle": ["100°"],
        "ip": "IP20",
        "lifespan": "30,000 hours @ L70",
        "warranty": "2 Year",
    },
    "eco_spotlight": {
        "family": "Eco Spotlight",
        "category": "spotlight",
        "subcategory": "commercial",
        "aliases": [
            "eco spotlight", "eco spot", "eco-spotlight", "ecospotlight",
            "eco spot light"
        ],
        "source_files": ["Eco-Spotlight.pdf"],
        "operating_voltage_max": 265,
        "input_voltage": "AC85-265V",
        "dimming": [],
        "power_consumption": ["7W", "12W", "18W"],
        "cct": ["3000K", "4000K", "6500K"],
        "cri": ">80",
        "beam_angle": ["38°"],
        "ip": "IP20",
        "lifespan": "30,000 hours @ L70",
        "warranty": "2 Year",
    },
    "ecobright_downlight": {
        "family": "EcoBright Downlight",
        "category": "downlight",
        "subcategory": "residential",
        "aliases": [
            "ecobright downlight", "eco bright downlight", "ecobright dl",
            "ecobright-downlight", "eco bright dl"
        ],
        "source_files": ["EcoBright-Downlight.pdf"],
        "operating_voltage_max": 265,
        "input_voltage": "AC85-265V",
        "dimming": [],
        "power_consumption": ["7W"],
        "cct": ["3000K", "4000K", "6500K"],
        "cri": ">80",
        "beam_angle": ["120°"],
        "ip": "IP20",
        "lifespan": "25,000 hours @ L70",
        "warranty": "1 Year",
    },
    "ecobright_spotlight": {
        "family": "EcoBright Spotlight",
        "category": "spotlight",
        "subcategory": "residential",
        "aliases": [
            "ecobright spotlight", "eco bright spotlight", "ecobright spot",
            "ecobright-spotlight", "eco bright spot"
        ],
        "source_files": ["EcoBright-Spotlight.pdf"],
        "operating_voltage_max": 265,
        "input_voltage": "AC85-265V",
        "dimming": [],
        "power_consumption": ["3W"],
        "cct": ["3000K", "4000K"],
        "cri": ">80",
        "beam_angle": ["50°"],
        "ip": "IP20",
        "lifespan": "20,000 hours @ L70",
        "warranty": "1 Year",
    },
    "laserline": {
        "family": "LaserLine",
        "category": "downlight",
        "subcategory": "linear",
        "aliases": [
            "laserline", "laser line", "laserline downlight",
            "laser line downlight"
        ],
        "source_files": ["LaserLine.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["12W", "24W"],
        "cct": ["2700K", "3000K", "4000K"],
        "cri": ">90",
        "beam_angle": ["15°", "30°", "45°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "50,000 hours @ L70",
        "warranty": "Lifetime*",
    },
    "laserlux": {
        "family": "LaserLux",
        "category": "downlight",
        "subcategory": "linear",
        "aliases": [
            "laserlux", "laser lux", "laserux", "laserlux downlight",
            "laser lux downlight"
        ],
        "source_files": ["LaserLux.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["10W", "20W", "30W"],
        "cct": ["2700K", "3000K", "4000K"],
        "cri": ">90",
        "beam_angle": ["15°", "30°", "45°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "30,000 hours @ L70",
        "warranty": "3 Year",
    },
    "luxarc": {
        "family": "LuxArc",
        "category": "downlight",
        "subcategory": "multi-head",
        "aliases": ["luxarc", "lux arc", "luxarc downlight"],
        "source_files": ["LuxArc.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["12W", "2x12W", "3x12W", "4x12W"],
        "cct": ["2700K", "3000K", "3500K", "4000K"],
        "cri": ">90",
        "beam_angle": ["15°", "24°", "36°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "50,000 hours @ L70",
        "warranty": "Lifetime*",
    },
    "luxspace": {
        "family": "LuxSpace",
        "category": "downlight",
        "subcategory": "architectural",
        "aliases": ["luxspace", "lux space", "luxspace downlight"],
        "source_files": ["LuxSpace.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["5W", "10W", "25W"],
        "cct": ["2700K", "3000K", "3500K", "4000K", "5700K", "6500K"],
        "cri": ">90",
        "beam_angle": ["15°", "24°", "36°", "60°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "50,000 hours @ L70",
        "warranty": "Lifetime*",
    },
    "nanolux": {
        "family": "NanoLux",
        "category": "downlight",
        "subcategory": "compact",
        "aliases": [
            "nanolux", "nano lux", "nanlux", "nanolux downlight",
            "nano lux downlight"
        ],
        "source_files": ["NanoLux.pdf"],
        "operating_voltage_max": 277,
        "input_voltage": "AC100-277V for Non-dimmable, AC220-240V for Dimmable",
        "dimming": ["TRIAC", "DALI", "0-10V"],
        "power_consumption": ["1W", "3W"],
        "cct": ["2700K", "3000K", "3500K", "4000K"],
        "cri": ">90",
        "beam_angle": ["15°", "24°", "36°"],
        "ip": "IP20",
        "ik": "IK02",
        "lifespan": "50,000 hours @ L70",
        "warranty": "5 Year",
    },
    "value_downlight_pro": {
        "family": "Value Downlight Pro",
        "category": "downlight",
        "subcategory": "commercial",
        "aliases": [
            "value downlight pro", "downlight pro", "value dl pro",
            "value-downlight-pro", "value down light pro"
        ],
        "source_files": ["Value-Downlight-Pro.pdf"],
        "operating_voltage_max": 240,
        "input_voltage": "AC220-240V",
        "dimming": ["TRIAC"],
        "power_consumption": ["10W", "20W"],
        "cct": ["3CCT (3000K, 4000K, 5700K)"],
        "cri": ">80",
        "beam_angle": ["90°"],
        "ip": "IP40",
        "lifespan": "40,000 hours @ L70",
        "warranty": "Up to 3 Year",
    },
    "value_grille_spot": {
        "family": "Value Grille Spot",
        "category": "spotlight",
        "subcategory": "grille",
        "aliases": [
            "value grille spot", "grille spot", "grill spot",
            "value grill spot", "value-grille-spot", "grille spotlight"
        ],
        "source_files": ["Value-Grille-Spot.pdf"],
        "operating_voltage_max": 240,
        "input_voltage": "AC200-240V",
        "dimming": ["TRIAC"],
        "power_consumption": ["12W", "24W", "36W"],
        "cct": ["3000K", "4000K", "5700K", "6500K"],
        "cri": ">80",
        "beam_angle": ["24°", "36°", "60°"],
        "ip": "IP20",
        "lifespan": "40,000 hours @ L70",
        "warranty": "Up to 3 Year",
    },
    "value_smd_spot": {
        "family": "Value SMD Spot",
        "category": "spotlight",
        "subcategory": "smd",
        "aliases": [
            "value smd spot", "smd spot", "value smd", "smd-spot",
            "value-smd-spot"
        ],
        "source_files": ["Value-SMD-Spot.pdf"],
        "operating_voltage_max": 240,
        "input_voltage": "AC220-240V",
        "dimming": ["TRIAC"],
        "power_consumption": ["8W"],
        "cct": ["3CCT (3000K, 4000K, 5700K)"],
        "cri": ">80",
        "beam_angle": ["38°"],
        "ip": "IP20",
        "lifespan": "50,000 hours @ L70",
        "warranty": "Up to 3 Year",
    },
}

def _normalize(value: str) -> str:
    """Lowercase, replace non-alphanumeric with spaces, and collapse whitespace."""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def identify_product_metadata(filename: str = "", text_content: str = "") -> Dict[str, Any]:
    """
    Identifies matched product family, category, and metadata from filename or query text.
    Uses regex word boundaries to avoid false substring matching.
    """
    norm_filename = _normalize(filename)
    norm_text = f" {_normalize(text_content)} "

    best_key: Optional[str] = None
    best_meta: Optional[Dict[str, Any]] = None
    best_score = 0
    best_matches: List[str] = []

    for key, meta in PRODUCT_CATALOG.items():
        score = 0
        matched = []

        # Exact filename match
        for sf in meta.get("source_files", []):
            norm_sf = _normalize(sf)
            if norm_sf and norm_sf in norm_filename:
                score += 300
                matched.append(sf)

        # Alias match with word boundary check
        for alias in meta.get("aliases", []):
            norm_alias = _normalize(alias)
            if not norm_alias:
                continue
            # Regex match with word boundary in query
            if re.search(rf"\b{re.escape(norm_alias)}\b", norm_text):
                # Prefer longer aliases
                match_weight = 50 + len(norm_alias) * 5
                score += match_weight
                matched.append(alias)
            elif norm_filename and norm_alias in norm_filename:
                score += 150 + len(norm_alias)
                matched.append(alias)

        if score > best_score:
            best_score = score
            best_key = key
            best_meta = meta
            best_matches = matched

    if best_meta is None or best_score < 40:
        return {
            "product_family": None,
            "category": "lighting",
            "subcategory": None,
            "voltage_max": None,
            "operating_voltage_max": None,
            "product_key": None,
            "confidence": 0.0,
            "matched_aliases": [],
        }

    result: Dict[str, Any] = {
        "product_family": best_meta["family"],
        "category": best_meta["category"],
        "subcategory": best_meta.get("subcategory"),
        "voltage_max": best_meta.get("operating_voltage_max"),
        "operating_voltage_max": best_meta.get("operating_voltage_max"),
        "product_key": best_key,
        "confidence": min(best_score / 200.0, 1.0),
        "matched_aliases": sorted(set(best_matches)),
    }

    for field in [
        "source_files",
        "input_voltage",
        "dimming",
        "power_consumption",
        "cct",
        "cri",
        "beam_angle",
        "ip",
        "ik",
        "lifespan",
        "warranty",
    ]:
        if field in best_meta:
            result[field] = best_meta[field]

    return result