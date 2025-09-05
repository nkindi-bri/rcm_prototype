import json
import csv
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from pathlib import Path

@dataclass
class Identity:
    name: str
    date_of_birth: str
    sex: str
    government_id: str
    insurance_plan: str
    member_id: str
    eligibility_status: str
    copayment: str
    coinsurance: str
    deductible_remaining: str

@dataclass
class Context:
    date_time: str
    location: str
    clinician_role: str
    visit_type: str
    place_of_service: str
    time_with_patient_min: int
    reason_for_visit: str

@dataclass
class Structured:
    vitals: Dict[str, Any]
    orders: Dict[str, Any]
    meds: List[Dict[str, Any]]
    attachments: List[str]

@dataclass
class Encounter:
    encounter_id: str
    identity: Identity
    context: Context
    structured: Structured
    note_sentences: List[str]

def _mk(encounter_id, identity, context, structured, note_sentences) -> Encounter:
    return Encounter(
        encounter_id=encounter_id,
        identity=Identity(**identity),
        context=Context(**context),
        structured=Structured(**structured),
        note_sentences=note_sentences,
    )

def make_encounters() -> List[Encounter]:
    encs: List[Encounter] = []

    encs.append(_mk(
        "ENC-001",
        dict(
            name="Amal Rahman",
            date_of_birth="1995-04-03",
            sex="Female",
            government_id="Emirates ID 784-1995-1234567-1",
            insurance_plan="Oasis Health Silver Care",
            member_id="020045611",
            eligibility_status="Active",
            copayment="60 AED",
            coinsurance="10% after deductible",
            deductible_remaining="400 AED",
        ),
        dict(
            date_time="2025-09-04 10:15",
            location="City Clinic, General Medicine",
            clinician_role="Family physician",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=22,
            reason_for_visit="Sore throat and fever",
        ),
        dict(
            vitals=dict(temperature_c=38.2, bp_mmHg="112/72", hr_bpm=96, spo2_pct=98, weight_kg=63, height_cm=165),
            orders=dict(lab_tests=[{"name": "Rapid streptococcal antigen", "units": 1, "specimen": "Throat swab"}]),
            meds=[{"name": "Paracetamol", "dose": "500 mg", "qty": "2 tablets in clinic"}],
            attachments=["ID_front.png", "Insurance_front.png"],
        ),
        [
            "S1. The patient reports three days of sore throat, fever, and painful swallowing.",
            "S2. Examination shows a red throat without exudate; no swollen lymph nodes; lungs are clear.",
            "S3. A rapid streptococcal antigen test was performed on a throat swab.",
            "S4. The assessment is acute pharyngitis.",
            "S5. Plan: symptomatic care, fluids, and antipyretic medication; return if symptoms worsen.",
        ],
    ))

    encs.append(_mk(
        "ENC-002",
        dict(
            name="Muhammad Al-Harthy",
            date_of_birth="1988-11-12",
            sex="Male",
            government_id="National ID OM-19881112-4452",
            insurance_plan="Gulf Shield Essential",
            member_id="GS-88112",
            eligibility_status="Active",
            copayment="50 SAR",
            coinsurance="20%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 11:40",
            location="Lakeside Clinic, Orthopedics",
            clinician_role="Orthopedic specialist",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=25,
            reason_for_visit="Knee pain after a fall",
        ),
        dict(
            vitals=dict(temperature_c=36.8, bp_mmHg="118/76", hr_bpm=78, spo2_pct=99, weight_kg=78, height_cm=178),
            orders=dict(
                imaging=[{"name": "Knee radiograph", "side": "Right", "views": 2, "performed_same_day": True}],
                devices=[{"name": "Elastic knee sleeve", "use": "home"}],
            ),
            meds=[],
            attachments=["ID_front.png", "Insurance_front.png", "ImagingConsent.pdf"],
        ),
        [
            "S1. The patient slipped on stairs yesterday and has right knee pain with difficulty bearing weight.",
            "S2. Examination shows swelling over the right knee and tenderness at the patella; range of motion is limited by pain.",
            "S3. A two-view radiograph of the right knee was performed and shows no fracture.",
            "S4. The assessment is acute right knee sprain.",
            "S5. Plan: rest, ice, compression sleeve, elevation, and pain control; return if locking or worsening instability.",
        ],
    ))

    encs.append(_mk(
        "ENC-003",
        dict(
            name="Sara Al Naimi",
            date_of_birth="1976-02-19",
            sex="Female",
            government_id="Qatar ID QA-01976-8821",
            insurance_plan="Hamad Private Comprehensive",
            member_id="HP-22631",
            eligibility_status="Active",
            copayment="0",
            coinsurance="0%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 09:10",
            location="Downtown Family Practice",
            clinician_role="Family physician",
            visit_type="Established patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=28,
            reason_for_visit="Diabetes review and medication refill",
        ),
        dict(
            vitals=dict(temperature_c=36.7, bp_mmHg="138/84", hr_bpm=74, spo2_pct=98, weight_kg=82, height_cm=160),
            orders=dict(
                lab_tests=[
                    {"name": "HbA1c", "units": 1},
                    {"name": "Fasting lipid profile", "units": 1},
                    {"name": "Urine microalbumin", "units": 1},
                ],
                exams=[{"name": "Foot exam with monofilament"}],
            ),
            meds=[
                {"name": "Metformin", "dose": "1000 mg bid", "days": 30},
                {"name": "Atorvastatin", "dose": "20 mg nightly", "days": 30},
            ],
            attachments=["LabTrend.pdf", "MedRec.txt"],
        ),
        [
            "S1. The patient returns for type 2 diabetes review and requests medication refills.",
            "S2. The patient reports good adherence and no episodes of low blood sugar.",
            "S3. Examination shows intact foot sensation by monofilament and no ulcers.",
            "S4. The assessment is type 2 diabetes without complications and mixed hyperlipidemia.",
            "S5. Plan: order glycated hemoglobin, fasting lipids, and urine microalbumin; continue current medicines; reinforce diet and walking.",
        ],
    ))

    encs.append(_mk(
        "ENC-004",
        dict(
            name="Faisal Khan",
            date_of_birth="1969-06-07",
            sex="Male",
            government_id="Pakistan passport P-AA1234567",
            insurance_plan="Desert Care Standard",
            member_id="DC-9067",
            eligibility_status="Active",
            copayment="30 AED",
            coinsurance="10%",
            deductible_remaining="200 AED",
        ),
        dict(
            date_time="2025-09-04 13:20",
            location="Marina Internal Medicine",
            clinician_role="Internist",
            visit_type="Established patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=20,
            reason_for_visit="Blood pressure check and medication refill",
        ),
        dict(
            vitals=dict(temperature_c=36.6, bp_mmHg="156/92", hr_bpm=72, spo2_pct=98, weight_kg=90, height_cm=175),
            orders=dict(tests=[{"name": "Resting electrocardiogram", "units": 1, "interpreted": True}]),
            meds=[{"name": "Amlodipine", "dose": "10 mg daily", "days": 30}],
            attachments=["ECG_Tracing.xml"],
        ),
        [
            "S1. The patient reports missed doses last week and mild ankle swelling.",
            "S2. Examination shows elevated blood pressure and no chest pain or shortness of breath.",
            "S3. A resting electrocardiogram was performed and shows normal rhythm with no acute changes.",
            "S4. The assessment is essential high blood pressure with suboptimal control.",
            "S5. Plan: increase amlodipine dose, monitor swelling, and recheck in four weeks.",
        ],
    ))

    encs.append(_mk(
        "ENC-005",
        dict(
            name="Leila Haddad",
            date_of_birth="2003-12-28",
            sex="Female",
            government_id="Lebanon ID LB-2003-55291",
            insurance_plan="Cedar Health Basic",
            member_id="CH-55291",
            eligibility_status="Active",
            copayment="20 USD",
            coinsurance="10%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 15:00",
            location="Palm Family Clinic",
            clinician_role="Family physician",
            visit_type="Established patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=24,
            reason_for_visit="Wheeze and cough after dust exposure",
        ),
        dict(
            vitals=dict(temperature_c=36.9, bp_mmHg="110/68", hr_bpm=102, spo2_pct=95, weight_kg=55, height_cm=162),
            orders=dict(in_clinic_treatments=[{"name": "Nebulized bronchodilator", "units": 1, "pre_spo2": 95, "post_spo2": 98}]),
            meds=[
                {"name": "ICS/LABA inhaler", "dose": "per label", "qty": 1},
                {"name": "Short-acting reliever", "dose": "per label", "qty": 1},
                {"name": "Spacer device", "qty": 1},
            ],
            attachments=["TreatmentConsent.pdf", "DeviceTeachingChecklist.pdf"],
        ),
        [
            "S1. The patient reports two days of cough and wheeze after a dust storm.",
            "S2. Examination shows diffuse wheeze and prolonged exhalation; oxygen saturation is 95 percent at rest.",
            "S3. Nebulized bronchodilator treatment was given with improvement to 98 percent saturation.",
            "S4. The assessment is mild asthma exacerbation triggered by dust exposure.",
            "S5. Plan: start daily controller inhaler, continue reliever as needed, provide spacer, and advise dust avoidance.",
        ],
    ))

    encs.append(_mk(
        "ENC-006",
        dict(
            name="Omar Saleh",
            date_of_birth="1992-01-30",
            sex="Male",
            government_id="Jordan ID JO-19920130-3399",
            insurance_plan="Sand Dunes Plus",
            member_id="SD-3399",
            eligibility_status="Active",
            copayment="40 JOD",
            coinsurance="20%",
            deductible_remaining="300 JOD",
        ),
        dict(
            date_time="2025-09-04 16:10",
            location="Neuro Clinic",
            clinician_role="Neurologist",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=35,
            reason_for_visit="Recurrent severe headache with light sensitivity",
        ),
        dict(
            vitals=dict(temperature_c=36.7, bp_mmHg="122/74", hr_bpm=70, spo2_pct=99, weight_kg=70, height_cm=173),
            orders=dict(imaging_orders=[{"name": "Head MRI without contrast", "units": 1, "authorization_required": True, "status": "Pending"}]),
            meds=[{"name": "Triptan", "use": "acute attacks"}, {"name": "Anti-nausea medication", "use": "as needed"}],
            attachments=["HeadacheDiary.pdf"],
        ),
        [
            "S1. The patient reports six weeks of episodic severe headache with nausea and light sensitivity.",
            "S2. Examination is normal with no weakness, no vision loss, and no neck stiffness.",
            "S3. The assessment is probable migraine without warning signs.",
            "S4. Plan: prescribe an acute treatment and request magnetic resonance imaging due to new onset in an adult; authorization request submitted.",
        ],
    ))

    encs.append(_mk(
        "ENC-007",
        dict(
            name="Hanan Yusuf",
            date_of_birth="1999-09-14",
            sex="Female",
            government_id="Bahrain CPR BH-990914-223",
            insurance_plan="Pearl Care Standard",
            member_id="PC-7723",
            eligibility_status="Active",
            copayment="5 BHD",
            coinsurance="10%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 12:05",
            location="Women’s Health Clinic",
            clinician_role="Family physician",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=18,
            reason_for_visit="Painful urination and urgency",
        ),
        dict(
            vitals=dict(temperature_c=37.6, bp_mmHg="114/70", hr_bpm=88, spo2_pct=99, weight_kg=60, height_cm=160),
            orders=dict(lab_tests=[{"name": "Urinalysis with microscopy", "units": 1}, {"name": "Urine culture", "units": 1}]),
            meds=[{"name": "Antibiotic", "days": 3}],
            attachments=[],
        ),
        [
            "S1. The patient reports two days of burning with urination, frequency, and urgency, without fever or back pain.",
            "S2. Examination shows mild lower abdominal tenderness without costovertebral angle tenderness.",
            "S3. Urinalysis shows positive white blood cells and nitrites; urine culture sent.",
            "S4. The assessment is uncomplicated urinary tract infection.",
            "S5. Plan: start a three-day antibiotic, increase fluids, and return if fever or flank pain occurs.",
        ],
    ))

    encs.append(_mk(
        "ENC-008",
        dict(
            name="Noura Al-Maktoum",
            date_of_birth="1985-08-08",
            sex="Female",
            government_id="Emirates ID 784-1985-7654321-9",
            insurance_plan="Desert Care Gold",
            member_id="DC-88001",
            eligibility_status="Active",
            copayment="0",
            coinsurance="0%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 09:45",
            location="Dermatology Clinic",
            clinician_role="Dermatologist",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=17,
            reason_for_visit="Itchy red rash on forearms after using a new lotion",
        ),
        dict(
            vitals=dict(temperature_c=36.5, bp_mmHg="108/66", hr_bpm=72, spo2_pct=100, weight_kg=58, height_cm=168),
            orders=dict(counseling=[{"name": "Allergen avoidance instructions"}]),
            meds=[{"name": "Topical steroid cream", "strength": "medium", "days": 7}, {"name": "Oral antihistamine", "use": "as needed"}],
            attachments=["RashPhoto_day1.jpg"],
        ),
        [
            "S1. The patient reports an itchy red rash on both forearms appearing one day after starting a new scented lotion.",
            "S2. Examination shows scattered red patches with scratch marks on both forearms without infection.",
            "S3. The assessment is allergic contact dermatitis.",
            "S4. Plan: stop the lotion, start topical steroid, and use an oral antihistamine if needed.",
        ],
    ))

    encs.append(_mk(
        "ENC-009",
        dict(
            name="Karim Haddad",
            date_of_birth="1981-03-02",
            sex="Male",
            government_id="Lebanon passport RL-7712345",
            insurance_plan="Cedar Health Plus",
            member_id="CH-88012",
            eligibility_status="Active",
            copayment="15 USD",
            coinsurance="10%",
            deductible_remaining="100 USD",
        ),
        dict(
            date_time="2025-09-04 14:30",
            location="Spine Clinic",
            clinician_role="Physical medicine and rehabilitation physician",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=30,
            reason_for_visit="Low back pain with right-leg tingling for two weeks",
        ),
        dict(
            vitals=dict(temperature_c=36.6, bp_mmHg="120/78", hr_bpm=76, spo2_pct=99, weight_kg=85, height_cm=180),
            orders=dict(
                referrals=[{"name": "Physical therapy evaluation and program", "sessions": 12}],
                imaging_orders=[{"name": "Lumbar spine X-ray", "views": 2}],
            ),
            meds=[{"name": "NSAID", "days": 7}],
            attachments=["PT_Referral.pdf"],
        ),
        [
            "S1. The patient reports two weeks of low back pain with tingling down the right leg after lifting boxes.",
            "S2. Examination shows limited forward bend and a positive straight-leg raise on the right.",
            "S3. The assessment is acute low back pain with probable right-sided nerve root irritation.",
            "S4. Plan: start physical therapy, short course of anti-inflammatory medication, and obtain lumbar spine radiographs.",
        ],
    ))

    encs.append(_mk(
        "ENC-010",
        dict(
            name="Aisha Al-Saud",
            date_of_birth="1998-05-17",
            sex="Female",
            government_id="Saudi ID SA-980517-4411",
            insurance_plan="Palm Health Maternity",
            member_id="PH-4411",
            eligibility_status="Active",
            copayment="0",
            coinsurance="0%",
            deductible_remaining="0",
        ),
        dict(
            date_time="2025-09-04 10:30",
            location="Women and Children Clinic",
            clinician_role="Obstetrician",
            visit_type="New patient",
            place_of_service="Clinic outpatient",
            time_with_patient_min=32,
            reason_for_visit="Missed period and positive home pregnancy test",
        ),
        dict(
            vitals=dict(temperature_c=36.6, bp_mmHg="106/64", hr_bpm=80, spo2_pct=100, weight_kg=62, height_cm=164),
            orders=dict(
                imaging_orders=[{"name": "Early pregnancy ultrasound, transabdominal", "units": 1}],
                lab_tests=[{"name": "Prenatal panel", "components": ["Blood type and screen", "CBC", "Rubella IgG", "HBsAg", "Syphilis screen"]}],
            ),
            meds=[{"name": "Prenatal vitamins", "dose": "daily"}],
            attachments=["UltrasoundImagesPending"],
        ),
        [
            "S1. The patient has a missed period and a positive home pregnancy test with mild nausea.",
            "S2. Examination is normal with no abdominal tenderness or bleeding.",
            "S3. The assessment is early intrauterine pregnancy, first visit.",
            "S4. Plan: order prenatal laboratory tests, schedule ultrasound, start prenatal vitamins, and review warning signs.",
        ],
    ))

    return encs

def encounters_to_csv(encounters: List[Encounter]) -> List[Dict[str, Any]]:
    """Convert encounters to flattened CSV-friendly format."""
    csv_data = []
    for enc in encounters:
        # Parse blood pressure
        bp_parts = enc.structured.vitals.get("bp_mmHg", "0/0").split("/")
        bp_systolic = int(bp_parts[0]) if len(bp_parts) > 0 else 0
        bp_diastolic = int(bp_parts[1]) if len(bp_parts) > 1 else 0
        
        # Combine clinical notes
        clinical_notes = " ".join(enc.note_sentences)
        
        # Summarize orders
        orders_summary = []
        if enc.structured.orders.get("lab_tests"):
            lab_names = [test.get("name", "") for test in enc.structured.orders["lab_tests"]]
            orders_summary.append(f"Labs: {', '.join(lab_names)}")
        if enc.structured.orders.get("imaging"):
            img_names = [img.get("name", "") for img in enc.structured.orders["imaging"]]
            orders_summary.append(f"Imaging: {', '.join(img_names)}")
        if enc.structured.orders.get("imaging_orders"):
            img_ord_names = [img.get("name", "") for img in enc.structured.orders["imaging_orders"]]
            orders_summary.append(f"Imaging Orders: {', '.join(img_ord_names)}")
        if enc.structured.orders.get("tests"):
            test_names = [test.get("name", "") for test in enc.structured.orders["tests"]]
            orders_summary.append(f"Tests: {', '.join(test_names)}")
        if enc.structured.orders.get("in_clinic_treatments"):
            treat_names = [treat.get("name", "") for treat in enc.structured.orders["in_clinic_treatments"]]
            orders_summary.append(f"Treatments: {', '.join(treat_names)}")
        
        # Summarize medications
        med_summary = []
        for med in enc.structured.meds:
            med_desc = med.get("name", "")
            if med.get("dose"):
                med_desc += f" {med['dose']}"
            if med.get("days"):
                med_desc += f" x{med['days']} days"
            med_summary.append(med_desc)
        
        csv_row = {
            "encounter_id": enc.encounter_id,
            "patient_name": enc.identity.name,
            "date_of_birth": enc.identity.date_of_birth,
            "sex": enc.identity.sex,
            "insurance_plan": enc.identity.insurance_plan,
            "member_id": enc.identity.member_id,
            "visit_date": enc.context.date_time,
            "visit_type": enc.context.visit_type,
            "reason_for_visit": enc.context.reason_for_visit,
            "clinician_role": enc.context.clinician_role,
            "location": enc.context.location,
            "time_with_patient_min": enc.context.time_with_patient_min,
            "temperature_c": enc.structured.vitals.get("temperature_c", 0),
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "heart_rate": enc.structured.vitals.get("hr_bpm", 0),
            "spo2": enc.structured.vitals.get("spo2_pct", 0),
            "weight_kg": enc.structured.vitals.get("weight_kg", 0),
            "height_cm": enc.structured.vitals.get("height_cm", 0),
            "clinical_notes": clinical_notes,
            "orders": "; ".join(orders_summary),
            "medications": "; ".join(med_summary),
            "attachments": "; ".join(enc.structured.attachments),
            # Store original JSON data for processing
            "original_json": json.dumps({
                "encounter_id": enc.encounter_id,
                "identity": asdict(enc.identity),
                "context": asdict(enc.context),
                "structured": asdict(enc.structured),
                "note_sentences": enc.note_sentences,
            }, ensure_ascii=False)
        }
        csv_data.append(csv_row)
    return csv_data

def main():
    # Generate CSV file
    csv_out = Path("data/patient_encounters.csv")
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    
    encounters = make_encounters()
    csv_data = encounters_to_csv(encounters)
    
    # Write CSV file
    if csv_data:
        with csv_out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
    
    # Also keep the original JSONL for backwards compatibility
    jsonl_out = Path("data/rcm_demo_input.jsonl")
    with jsonl_out.open("w", encoding="utf-8") as f:
        for enc in encounters:
            f.write(json.dumps({
                "encounter_id": enc.encounter_id,
                "identity": asdict(enc.identity),
                "context": asdict(enc.context),
                "structured": asdict(enc.structured),
                "note_sentences": enc.note_sentences,
            }, ensure_ascii=False) + "\n")
    
    print(f"CSV: {csv_out}")
    print(f"JSONL: {jsonl_out}")

if __name__ == "__main__":
    main()
