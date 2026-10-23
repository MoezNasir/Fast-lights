import pymupdf
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any
from app.products import identify_product_metadata

def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return f"sha256:{hasher.hexdigest()}"

LABEL_EXPANSIONS = {
    "correlated color temperature": "Correlated Color Temperature (CCT):",
    "color rendering index": "Color Rendering Index (CRI):",
    "ingress protection code": "Ingress Protection (IP Rating):",
    "impact protection code": "Impact Protection (IK Rating):",
    "power consumption": "Power Consumption (Wattage):",
    "luminous flux": "Luminous Flux (Lumens):",
    "input voltage": "Input Voltage (Operating Voltage):",
    "beam angle": "Beam Angle (Optics / Degree):",
    "dimming": "Dimming & Controls (TRIAC / DALI / 0-10V):",
}

def _expand_label(label: str) -> str:
    lbl_clean = label.lower().strip().rstrip(":")
    for pattern, expanded in LABEL_EXPANSIONS.items():
        if pattern in lbl_clean:
            return expanded
    if not label.endswith(":"):
        return label + ":"
    return label

def _pair_column_blocks(col_blocks: list, x_split: float) -> list[str]:
    """
    Pairs label blocks (left of x_split) with their corresponding value blocks (right of x_split)
    based on vertical proximity.
    """
    labels = [b for b in col_blocks if b[0] < x_split]
    values = [b for b in col_blocks if b[0] >= x_split]
    
    pairs = []
    used_val_indices = set()
    
    for l in sorted(labels, key=lambda b: b[1]):
        l_text = l[4].strip().replace("\n", " ")
        if not l_text:
            continue
        
        # Find matching value with closest y-coordinate
        matching_val = None
        best_dy = 999
        best_idx = None
        
        for idx, v in enumerate(values):
            if idx in used_val_indices:
                continue
            dy = abs(v[1] - l[1])
            if dy < 16 and dy < best_dy:
                best_dy = dy
                matching_val = v
                best_idx = idx
                
        if matching_val:
            v_text = matching_val[4].strip().replace("\n", ", ")
            expanded_label = _expand_label(l_text)
            pairs.append(f"{expanded_label} {v_text}")
            used_val_indices.add(best_idx)
        else:
            pairs.append(l_text)
            
    # Include any un-paired values
    for idx, v in enumerate(values):
        if idx not in used_val_indices:
            v_text = v[4].strip().replace("\n", " ")
            if v_text and not any(v_text in p for p in pairs):
                pairs.append(v_text)
                
    return pairs

def parse_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Parses a commercial lighting product datasheet PDF using layout-aware spatial block extraction.
    Extracts structured technical specifications, descriptions, benefits, dimensions, and compliance.
    """
    chunks = []
    file_hash = get_file_hash(pdf_path)
    doc_name = pdf_path.name
    meta = identify_product_metadata(filename=doc_name, text_content="")
    prod_name = meta.get("product_family", pdf_path.stem)
    category = meta.get("category", "lighting")

    doc = pymupdf.open(pdf_path)

    full_doc_specs = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        blocks = [b for b in blocks if b[4].strip()]
        
        content_blocks = []
        for b in blocks:
            text = b[4].strip()
            if "www.fast-cables.com" in text or "UAN: 111-000-343" in text:
                continue
            if "PRODUCT SPECIFICATION" in text:
                continue
            if re.match(r"^MRK/PM/PS/[A-Z0-9/]+$", text):
                continue
            content_blocks.append(b)

        left_blocks = [b for b in content_blocks if b[0] < 290]
        right_blocks = [b for b in content_blocks if b[0] >= 290]

        left_items = _pair_column_blocks(left_blocks, 135)
        right_items = _pair_column_blocks(right_blocks, 420)

        if page_num == 1:
            desc_lines = []
            benefits_lines = []
            apps_lines = []
            tech_specs_lines = []
            elec_specs_lines = []

            for item in left_items:
                if any(hdr in item for hdr in ["Description", "The ", "is a ", "features a "]) and not any(k in item for k in ["Driver Included", "Lifespan", "Warranty", "Power Consumption", "Beam Angle", "CRI", "CCT"]):
                    desc_lines.append(item)
                elif any(hdr in item for hdr in ["Product Beneﬁt", "Product Benefit", "Sleek", "Energy Eﬃcient", "Energy Efficient", "Customizable", "Complies", "Long Lifespan", "High Visual"]):
                    benefits_lines.append(item)
                else:
                    tech_specs_lines.append(item)

            for item in right_items:
                if any(hdr in item for hdr in ["Application Area", "Luxury", "Retail", "Residential", "Hotels", "Galleries", "Museums", "Restaurants", "Oﬃces", "Offices", "Supermarkets", "Shopping", "Hospitals", "Banks"]):
                    apps_lines.append(item)
                else:
                    elec_specs_lines.append(item)

            overview_text = f"Product: {prod_name}\nCategory: {category}\nDocument: {doc_name} (Page 1)\n\n"
            if desc_lines:
                overview_text += "Overview & Description:\n" + "\n".join(desc_lines) + "\n\n"
            if benefits_lines:
                overview_text += "Key Benefits:\n" + "\n".join(benefits_lines) + "\n\n"
            if apps_lines:
                overview_text += "Recommended Application Areas:\n" + "\n".join(apps_lines)

            chunks.append({
                "chunk_id": f"{pdf_path.stem}_p1_overview",
                "document": doc_name,
                "page": 1,
                "type": "overview",
                "text": overview_text.strip(),
                "source_file_hash": file_hash,
                "product_family": prod_name,
                "category": category,
                "product_key": meta.get("product_key")
            })

            specs_text = f"Product: {prod_name}\nCategory: {category}\nDocument: {doc_name} (Page 1)\n\n"
            specs_text += "General Information & Luminaire Performance Specifications:\n"
            specs_text += "\n".join(tech_specs_lines)
            if elec_specs_lines:
                specs_text += "\n\nElectrical, Temperature & Dimming Specifications:\n"
                specs_text += "\n".join(elec_specs_lines)

            full_doc_specs.extend(tech_specs_lines)
            full_doc_specs.extend(elec_specs_lines)

            chunks.append({
                "chunk_id": f"{pdf_path.stem}_p1_specs",
                "document": doc_name,
                "page": 1,
                "type": "specifications",
                "text": specs_text.strip(),
                "source_file_hash": file_hash,
                "product_family": prod_name,
                "category": category,
                "product_key": meta.get("product_key")
            })

        elif page_num == 2:
            mech_lines = []
            dims_lines = []
            certs_lines = []

            for item in left_items:
                if any(k in item for k in ["Housing", "Trim", "Optic", "Finishing", "Installation", "Material", "Cover"]):
                    mech_lines.append(item)
                elif any(k in item for k in ["Dimension", "C, DxH", "Cutout", "5W", "7W", "10W", "12W", "18W", "20W", "24W", "25W", "30W", "36W", "mm", "64x75", "83x94", "104x110"]):
                    dims_lines.append(item)
                elif "Head Oﬃce" in item or "Sales Oﬃce" in item or "Head Office" in item:
                    continue
                else:
                    mech_lines.append(item)

            for item in right_items:
                if any(k in item for k in ["Ingress Protection", "IP", "Impact Protection", "IK", "Protection Class", "Safety Class", "CB", "CE", "IEC", "EMC", "RoHS", "Certiﬁcations", "Certifications", "Approval"]):
                    certs_lines.append(item)
                elif any(k in item for k in ["Dimension", "mm", "x", "Cutout", "10W", "20W", "30W", "36W"]):
                    dims_lines.append(item)
                else:
                    certs_lines.append(item)

            full_doc_specs.extend(mech_lines)
            full_doc_specs.extend(certs_lines)
            full_doc_specs.extend(dims_lines)

            mech_text = f"Product: {prod_name}\nCategory: {category}\nDocument: {doc_name} (Page 2)\n\n"
            mech_text += "Mechanical, Housing & Installation Specifications:\n"
            mech_text += "\n".join(mech_lines) + "\n\n"
            mech_text += "Compliance, Certifications & Protection Ratings (IP/IK):\n"
            mech_text += "\n".join(certs_lines)

            chunks.append({
                "chunk_id": f"{pdf_path.stem}_p2_mechanical_certs",
                "document": doc_name,
                "page": 2,
                "type": "mechanical_compliance",
                "text": mech_text.strip(),
                "source_file_hash": file_hash,
                "product_family": prod_name,
                "category": category,
                "product_key": meta.get("product_key")
            })

            if dims_lines:
                dims_text = f"Product: {prod_name}\nCategory: {category}\nDocument: {doc_name} (Page 2)\n\n"
                dims_text += "Physical Dimensions, Cutout Sizes & Model Variants:\n"
                dims_text += "\n".join(dims_lines)

                chunks.append({
                    "chunk_id": f"{pdf_path.stem}_p2_dimensions",
                    "document": doc_name,
                    "page": 2,
                    "type": "dimensions",
                    "text": dims_text.strip(),
                    "source_file_hash": file_hash,
                    "product_family": prod_name,
                    "category": category,
                    "product_key": meta.get("product_key")
                })

    master_specs_text = f"Product Family: {prod_name}\nCategory: {category}\nSource Datasheet: {doc_name}\n\n"
    master_specs_text += f"Comprehensive Technical Specification Sheet for {prod_name}:\n"
    for line in full_doc_specs:
        if line.strip() and not line.endswith(":"):
            master_specs_text += f"- {line.strip()}\n"

    chunks.append({
        "chunk_id": f"{pdf_path.stem}_master_datasheet",
        "document": doc_name,
        "page": 1,
        "type": "master_datasheet",
        "text": master_specs_text.strip(),
        "source_file_hash": file_hash,
        "product_family": prod_name,
        "category": category,
        "product_key": meta.get("product_key")
    })

    doc.close()
    return chunks