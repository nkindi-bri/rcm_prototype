import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

# ---------------------------
# 1) Input
# ---------------------------

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items

# ---------------------------
# 2) Note sentence helper
# ---------------------------

def sentence_pairs(note_sentences: List[str]) -> List[Tuple[str, str]]:
    """Return [(sentence_id, text_without_id), ...]."""
    out = []
    for s in note_sentences:
        m = re.match(r"^(S\\d+)\\.\\s*(.*)$", s.strip())
        if m:
            out.append((m.group(1), m.group(2)))
        else:
            out.append(("", s.strip()))
    return out

# ---------------------------
# 3) Fact extraction (diagnoses, services, tests, imaging, drugs, treatments, modifiers)
# ---------------------------

def map_visit_level(visit_type: str, minutes: int) -> str:
    """Rough time-based visit level (demo)."""
    vt = (visit_type or "").lower()
    if vt.startswith("new"):
        if minutes < 20: return "LEVEL_2"
        if minutes < 30: return "LEVEL_3"
        if minutes < 45: return "LEVEL_4"
        return "LEVEL_5"
    else:
        if minutes < 20: return "LEVEL_2"
        if minutes < 30: return "LEVEL_3"
        if minutes < 40: return "LEVEL_4"
        return "LEVEL_5"

def extract_facts(note_sentences: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
    sents = sentence_pairs(note_sentences)
    extracted = {
        "diagnoses": [], "services": [], "tests": [], "imaging": [], "treatments": [], "drugs": [], "modifiers": []
    }

    def add(bucket: str, obj: Dict[str, Any], sid: str, span: str):
        o = dict(obj); o["evidence"] = {"sentence_id": sid, "text": span}
        extracted[bucket].append(o)

    # Diagnoses (pattern-based demo only)
    diag_patterns = [
        (r"pharyngitis|sore throat", "DX_ACUTE_PHARYNGITIS", "Acute pharyngitis"),
        (r"right knee sprain", "DX_ACUTE_RIGHT_KNEE_SPRAIN", "Acute right knee sprain"),
        (r"type 2 diabetes.*without complications", "DX_T2DM_NO_COMPLICATIONS", "Type 2 diabetes without complications"),
        (r"mixed hyperlipidemia", "DX_MIXED_HYPERLIPIDEMIA", "Mixed hyperlipidemia"),
        (r"high blood pressure|hypertension", "DX_ESSENTIAL_HYPERTENSION", "Essential hypertension"),
        (r"asthma exacerbation", "DX_ASTHMA_EXACERBATION", "Mild asthma exacerbation"),
        (r"migraine", "DX_MIGRAINE", "Migraine without warning signs"),
        (r"urinary tract infection|UTI", "DX_UTI_UNCOMPLICATED", "Uncomplicated urinary tract infection"),
        (r"allergic contact dermatitis|contact dermatitis", "DX_ALLERGIC_CONTACT_DERMATITIS", "Allergic contact dermatitis"),
        (r"low back pain.*nerve root|lower back pain.*nerve root", "DX_ACUTE_LOWBACK_WITH_RADIATION", "Acute low back pain with probable radicular symptoms"),
        (r"early intrauterine pregnancy|early pregnancy", "DX_EARLY_PREGNANCY", "Early intrauterine pregnancy"),
    ]
    for sid, txt in sents:
        low = txt.lower()
        for pat, code, label in diag_patterns:
            if re.search(pat, low):
                add("diagnoses", {"code": code, "label": label}, sid, txt)

    # Visit service (time-based)
    level = map_visit_level(context.get("visit_type",""), int(context.get("time_with_patient_min", 0)))
    ev_sid, ev_txt = sents[0] if sents else ("STRUCTURED:context", context.get("reason_for_visit",""))
    add("services", {
        "code": f"SVC_VISIT_{'NEW' if context.get('visit_type','').startswith('New') else 'EST'}_{level}",
        "label": f"Outpatient visit ({context.get('visit_type','')} , {level.replace('_',' ').title()})",
        "units": 1
    }, ev_sid, ev_txt)

    # Tests
    test_patterns = [
        (r"rapid streptococcal|rapid strep", {"code":"TEST_RAPID_STREP","label":"Rapid streptococcal antigen test","units":1}),
        (r"electrocardiogram|ecg", {"code":"TEST_ECG","label":"Resting electrocardiogram with interpretation","units":1}),
        (r"urinalysis", {"code":"TEST_URINALYSIS","label":"Urinalysis with microscopy","units":1}),
        (r"urine culture", {"code":"TEST_URINE_CULTURE","label":"Urine culture","units":1}),
        (r"hbA1c|glycated hemoglobin", {"code":"TEST_HBA1C","label":"Glycated hemoglobin","units":1}),
        (r"fasting lipid", {"code":"TEST_LIPID_PANEL","label":"Fasting lipid profile","units":1}),
        (r"urine microalbumin", {"code":"TEST_MICROALB","label":"Urine microalbumin","units":1}),
        (r"prenatal.*panel", {"code":"TEST_PRENATAL_PANEL","label":"Prenatal laboratory panel","units":1}),
    ]
    for sid, txt in sents:
        lw = txt.lower()
        for pat, obj in test_patterns:
            if re.search(pat, lw):
                add("tests", obj, sid, txt)

    # Imaging
    imaging_patterns = [
        (r"two[- ]view.*right knee|right knee.*two[- ]view", {"code":"IMG_KNEE_XR_2V_RIGHT","label":"Knee X-ray, right, two views","units":1,"side":"Right","views":2}),
        (r"magnetic resonance imaging|\\bmri\\b", {"code":"IMG_BRAIN_MRI_WO","label":"Head MRI without contrast","units":1}),
        (r"ultrasound.*pregnan", {"code":"IMG_OB_EARLY_US","label":"Early pregnancy ultrasound, transabdominal","units":1}),
        (r"lumbar spine.*radiograph|radiographs.*lumbar spine", {"code":"IMG_LUMBAR_XR_2V","label":"Lumbar spine X-ray, two or three views","units":1}),
    ]
    for sid, txt in sents:
        lw = txt.lower()
        for pat, obj in imaging_patterns:
            if re.search(pat, lw):
                add("imaging", obj, sid, txt)

    # Treatments
    for sid, txt in sents:
        if re.search(r"nebulized bronchodilator", txt.lower()):
            add("treatments", {"code":"TRT_NEBULIZER","label":"Nebulized bronchodilator treatment","units":1}, sid, txt)

    # Drugs (demo)
    drug_patterns = [
        (r"paracetamol", {"name":"Paracetamol"}),
        (r"metformin", {"name":"Metformin"}),
        (r"atorvastatin", {"name":"Atorvastatin"}),
        (r"amlodipine", {"name":"Amlodipine"}),
        (r"triptan", {"name":"Triptan"}),
        (r"antibiotic", {"name":"Antibiotic (unspecified)"}),
        (r"prenatal vitamin", {"name":"Prenatal vitamins"}),
        (r"antihistamine", {"name":"Oral antihistamine"}),
        (r"topical steroid", {"name":"Topical steroid cream"}),
        (r"NSAID|anti-inflammatory", {"name":"Non-steroidal anti-inflammatory drug"}),
        (r"inhaler|controller inhaler|reliever", {"name":"Inhaler medication"}),
    ]
    for sid, txt in sents:
        lw = txt.lower()
        for pat, obj in drug_patterns:
            if re.search(pat, lw):
                add("drugs", obj, sid, txt)

    # Laterality modifier (only if present)
    for sid, txt in sents:
        lw = txt.lower()
        if " right " in f" {lw} ":
            add("modifiers", {"type":"LATERALITY","value":"Right"}, sid, txt)
            break
        if " left " in f" {lw} ":
            add("modifiers", {"type":"LATERALITY","value":"Left"}, sid, txt)
            break

    return extracted

# ---------------------------
# 4) Structured cross-check
# ---------------------------

def _ensure_item(extracted_bucket: List[Dict[str,Any]], cand: Dict[str,Any], key_fields: List[str]) -> None:
    for ex in extracted_bucket:
        if all(k in ex and k in cand and ex[k]==cand[k] for k in key_fields):
            return
    c = dict(cand); c["evidence"] = {"sentence_id":"STRUCTURED:orders","text":"From structured orders"}
    extracted_bucket.append(c)

def cross_check_structured(extracted: Dict[str,Any], structured: Dict[str,Any]) -> None:
    orders = structured.get("orders", {})

    # Labs
    lab_map = {
        "Rapid streptococcal antigen": {"code":"TEST_RAPID_STREP","label":"Rapid streptococcal antigen test"},
        "HbA1c": {"code":"TEST_HBA1C","label":"Glycated hemoglobin"},
        "Fasting lipid profile": {"code":"TEST_LIPID_PANEL","label":"Fasting lipid profile"},
        "Urine microalbumin": {"code":"TEST_MICROALB","label":"Urine microalbumin"},
        "Prenatal panel": {"code":"TEST_PRENATAL_PANEL","label":"Prenatal laboratory panel"},
        "Urinalysis with microscopy": {"code":"TEST_URINALYSIS","label":"Urinalysis with microscopy"},
        "Urine culture": {"code":"TEST_URINE_CULTURE","label":"Urine culture"},
    }
    for lab in orders.get("lab_tests", []):
        meta = lab_map.get(lab.get("name"))
        if meta:
            cand = {**meta, "units": lab.get("units", 1)}
            _ensure_item(extracted["tests"], cand, ["code"])

    # Tests
    for t in orders.get("tests", []):
        if str(t.get("name","")).lower().startswith("resting electrocardiogram"):
            _ensure_item(extracted["tests"], {"code":"TEST_ECG","label":"Resting electrocardiogram with interpretation","units": t.get("units",1)}, ["code"])

    # Imaging performed
    for img in orders.get("imaging", []):
        nm = str(img.get("name","")).lower()
        if "knee" in nm:
            _ensure_item(extracted["imaging"], {"code":"IMG_KNEE_XR_2V_RIGHT","label":"Knee X-ray, right, two views","units":1,"side":img.get("side"),"views":img.get("views")}, ["code"])

    # Imaging orders
    for io in orders.get("imaging_orders", []):
        nm = str(io.get("name","")).lower()
        if "mri" in nm and "head" in nm:
            _ensure_item(extracted["imaging"], {"code":"IMG_BRAIN_MRI_WO","label":"Head MRI without contrast","units": io.get("units",1),"authorization_required": io.get("authorization_required", False),"status": io.get("status")}, ["code"])
        if "lumbar spine" in nm and "x-ray" in nm:
            _ensure_item(extracted["imaging"], {"code":"IMG_LUMBAR_XR_2V","label":"Lumbar spine X-ray, two or three views","units":1}, ["code"])
        if "ultrasound" in nm and "pregnancy" in nm:
            _ensure_item(extracted["imaging"], {"code":"IMG_OB_EARLY_US","label":"Early pregnancy ultrasound, transabdominal","units": io.get("units",1)}, ["code"])

    # In-clinic treatments
    for tr in orders.get("in_clinic_treatments", []):
        if "nebulized" in str(tr.get("name","")).lower():
            _ensure_item(extracted["treatments"], {"code":"TRT_NEBULIZER","label":"Nebulized bronchodilator treatment","units": tr.get("units",1)}, ["code"])

# ---------------------------
# 5) Policy checks (very small rules layer)
# ---------------------------

def apply_policy_checks(extracted: Dict[str,Any], context: Dict[str,Any]) -> Dict[str, List[str]]:
    """
    Returns dict: {item_code: [warnings...]}
    Demo rules:
      - Imaging knee X-ray requires laterality and views >= 2.
      - Units must be positive integers.
      - MRI 'authorization_required' -> warn if status is not 'Approved' (demo).
    """
    warnings: Dict[str, List[str]] = {}

    def warn(code: str, msg: str):
        warnings.setdefault(code, []).append(msg)

    # Units check
    for bucket in ("tests","imaging","treatments","services"):
        for item in extracted[bucket]:
            units = int(item.get("units", 1) or 0)
            if units <= 0:
                warn(item.get("code","?"), "Units must be a positive integer.")

    # Knee X-ray checks
    for im in extracted["imaging"]:
        if im.get("code") == "IMG_KNEE_XR_2V_RIGHT":
            if im.get("side") not in ("Right","Left"):
                warn(im["code"], "Laterality (right/left) should be specified.")
            if int(im.get("views", 0) or 0) < 2:
                warn(im["code"], "Knee radiograph should include at least two views.")

    # MRI authorization
    for im in extracted["imaging"]:
        if im.get("code") == "IMG_BRAIN_MRI_WO" and im.get("authorization_required"):
            if im.get("status") != "Approved":
                warn(im["code"], f"MRI requires authorization; current status is '{im.get('status')}'.")

    return warnings

# ---------------------------
# 6) Charge capture
# ---------------------------

PRICE = {
    "SVC_VISIT_NEW_LEVEL_2": 60, "SVC_VISIT_NEW_LEVEL_3": 90, "SVC_VISIT_NEW_LEVEL_4": 140, "SVC_VISIT_NEW_LEVEL_5": 220,
    "SVC_VISIT_EST_LEVEL_2": 40, "SVC_VISIT_EST_LEVEL_3": 70, "SVC_VISIT_EST_LEVEL_4": 110, "SVC_VISIT_EST_LEVEL_5": 180,
    "TEST_RAPID_STREP": 25, "TEST_ECG": 45, "TEST_URINALYSIS": 20, "TEST_URINE_CULTURE": 35, "TEST_HBA1C": 30,
    "TEST_LIPID_PANEL": 35, "TEST_MICROALB": 25, "TEST_PRENATAL_PANEL": 85,
    "IMG_KNEE_XR_2V_RIGHT": 60, "IMG_BRAIN_MRI_WO": 400, "IMG_OB_EARLY_US": 120, "IMG_LUMBAR_XR_2V": 70,
    "TRT_NEBULIZER": 30,
}

def compose_charges(extracted: Dict[str,Any], diagnoses: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    dx = diagnoses or [{"code":"DX_UNSPECIFIED","label":"Unspecified diagnosis","evidence":{"sentence_id":"N/A","text":"No diagnosis found"}}]
    charges = []

    def add_line(item: Dict[str,Any]):
        code = item.get("code","UNKNOWN")
        units = int(item.get("units",1))
        price = PRICE.get(code, 50)
        charges.append({
            "description": item.get("label", code),
            "code": code,
            "units": units,
            "unit_price": price,
            "total": price * units,
            "supported_by_diagnosis": [dx[0]["code"]],
            "evidence": item.get("evidence", {}),
        })

    for b in ("services","tests","imaging","treatments"):
        for it in extracted[b]:
            add_line(it)

    return charges

# ---------------------------
# 7) Orchestrate + Save
# ---------------------------

def process_encounter(enc: Dict[str,Any]) -> Dict[str,Any]:
    facts = extract_facts(enc["note_sentences"], enc["context"])
    cross_check_structured(facts, enc["structured"])
    warnings = apply_policy_checks(facts, enc["context"])
    charges = compose_charges(facts, facts["diagnoses"])
    return {
        "encounter_id": enc["encounter_id"],
        "identity": enc["identity"],
        "context": enc["context"],
        "structured": enc["structured"],
        "note_sentences": enc["note_sentences"],
        "extracted": facts,
        "policy_warnings": warnings,
        "charges": charges,
    }

def save_outputs(results: List[Dict[str,Any]], out_dir: str) -> Dict[str,str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Detailed JSONL
    detailed = out / "rcm_parsed_output.jsonl"
    with detailed.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # CSV summary
    headers = ["Encounter","Patient","Visit type","Diagnoses","Services","Tests","Imaging","Charge total (mock currency)","Warnings"]
    csvp = out / "rcm_parsed_summary.csv"
    def labels(lst, key="label"):
        return ", ".join(sorted({x.get(key, x.get("code","")) for x in lst})) if lst else "—"

    with csvp.open("w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for r in results:
            dx = labels(r["extracted"]["diagnoses"])
            svc = labels(r["extracted"]["services"])
            tests = labels(r["extracted"]["tests"])
            img = labels(r["extracted"]["imaging"])
            total = sum(c["total"] for c in r["charges"])
            warn = "; ".join(f"{k}: {' | '.join(v)}" for k,v in r["policy_warnings"].items()) or "—"
            row = [
                r["encounter_id"],
                r["identity"]["name"],
                r["context"]["visit_type"],
                dx.replace(",",";"),
                svc.replace(",",";"),
                tests.replace(",",";"),
                img.replace(",",";"),
                str(total),
                warn.replace(",",";"),
            ]
            f.write(",".join(row) + "\n")

    return {"jsonl": str(detailed), "csv": str(csvp)}

def main(input_path: str = "data/rcm_demo_input.jsonl", out_dir: str = "data"):
    data = load_jsonl(input_path)
    results = [process_encounter(enc) for enc in data]
    paths = save_outputs(results, out_dir)
    print(paths["jsonl"])
    print(paths["csv"])

if __name__ == "__main__":
    main()
