# RCM (Revenue Cycle Management) Prototype

A healthcare revenue cycle management prototype that demonstrates automated clinical coding and charge capture from patient encounter data. The system processes clinical notes using natural language processing to extract billable services, diagnoses, and procedures.

## Overview

This prototype simulates a complete healthcare revenue cycle workflow:

1. **Patient Encounter Data** - CSV format with demographics, vitals, clinical notes, and orders
2. **Clinical Processing** - Automated extraction of diagnoses, procedures, tests, and medications from clinical notes
3. **Charge Capture** - Generation of itemized billing based on extracted clinical information
4. **Policy Validation** - Business rules checking for compliance and completeness

## Key Features

- **CSV-First Workflow** - Healthcare professionals work with familiar tabular data
- **Pattern-Based Extraction** - Clinical facts extracted using regex patterns from clinical notes
- **Mock Billing Integration** - Generates charges with realistic healthcare codes and pricing
- **Web Interface** - Interactive dashboard for reviewing and processing encounters
- **Structured Data Cross-Referencing** - Validates extracted information against structured orders

## Quick Start

### Prerequisites

- Python 3.8+
- Flask
- Modern web browser

### Installation

1. **Clone or download the project**
   ```bash
   cd rcm_prototype
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data**
   ```bash
   python generate_rcm_testdata.py
   ```
   This creates:
   - `data/patient_encounters.csv` - Healthcare-friendly CSV format
   - `data/rcm_demo_input.jsonl` - JSON format for processing

4. **Start the web application**
   ```bash
   python app.py
   ```
   Open your browser to `http://localhost:8080`

## Demo Usage

### Web Interface Demo

1. **View Patient Encounters**: The main page displays a table of 10 synthetic patient encounters with realistic Middle Eastern demographics and medical conditions
2. **Select an Encounter**: Click any row to see the detailed JSON data populate in the textarea below
3. **Process Encounter**: Click "Process Selected Encounter" to see:
   - Extracted clinical facts (diagnoses, procedures, medications)
   - Policy validation warnings
   - Generated billing charges with mock pricing

### Sample Conditions Included

- Acute pharyngitis with rapid strep test
- Knee injury with X-ray imaging
- Diabetes management with lab work
- Hypertension monitoring with ECG
- Asthma exacerbation with nebulizer treatment
- Migraine with MRI authorization
- Urinary tract infection with urinalysis
- Contact dermatitis treatment
- Lower back pain with physical therapy referral
- Early pregnancy with prenatal labs

### Command Line Processing

**Process all encounters at once:**
```bash
python parse_rcm_documents.py
```

**Output files:**
- `data/rcm_parsed_output.jsonl` - Detailed processing results
- `data/rcm_parsed_summary.csv` - Summary with charges and warnings

## Architecture

### Data Flow
```
CSV Patient Data → Clinical Note Processing → Fact Extraction → Policy Validation → Charge Generation → Web Display
```

### Core Components

1. **Data Generation** (`generate_rcm_testdata.py`)
   - Creates synthetic medical encounters
   - Outputs both CSV and JSON formats

2. **Clinical Processing** (`parse_rcm_documents.py`)
   - Extracts diagnoses, procedures, medications from clinical notes
   - Applies business rules and validation
   - Generates billing charges

3. **Web Interface** (`app.py`, `templates/`, `static/`)
   - Flask-based dashboard
   - CSV table interface for healthcare professionals
   - Real-time processing and results display

### Key Directories

```
rcm_prototype/
├── data/                    # Generated data files
├── templates/               # HTML templates
├── static/                  # CSS and static assets
├── generate_rcm_testdata.py # Sample data generation
├── parse_rcm_documents.py   # Clinical processing engine
├── app.py                   # Flask web application
└── requirements.txt         # Python dependencies
```

## Sample Output

**Extracted Clinical Facts:**
```
Diagnoses: Acute pharyngitis (Evidence: "The assessment is acute pharyngitis" [S4])
Services: Outpatient visit (New patient, Level 3)
Tests: Rapid streptococcal antigen test
```

**Generated Charges:**
```
Description                              | Code                    | Units | Price | Total
Outpatient visit (New patient, Level 3) | SVC_VISIT_NEW_LEVEL_3  | 1     | 90.00 | 90.00
Rapid streptococcal antigen test         | TEST_RAPID_STREP       | 1     | 25.00 | 25.00
                                                                   Grand Total: 115.00
```

## Customization

### Adding New Clinical Patterns

Edit `parse_rcm_documents.py` to add new diagnostic or procedure patterns:

```python
diag_patterns = [
    (r"your_condition_pattern", "DX_YOUR_CODE", "Your Diagnosis Label"),
    # Add more patterns...
]
```

### Adding New Pricing

Update the `PRICE` dictionary in `parse_rcm_documents.py`:

```python
PRICE = {
    "YOUR_SERVICE_CODE": 150,
    # Add more pricing...
}
```

## Important Notes

- **Mock Data**: All patient data is synthetic and for demonstration purposes only
- **Demo Pricing**: All charges use mock currency and pricing for prototype demonstration
- **Pattern Matching**: Clinical extraction uses simple regex patterns; production systems would use more sophisticated NLP
- **No PHI**: No real patient health information is used or stored

## Use Cases

This prototype demonstrates concepts useful for:
- Healthcare technology companies
- Medical billing software development
- Revenue cycle management training
- Clinical coding automation research
- Healthcare workflow optimization

## Support

For technical issues or questions about the demo, refer to the code comments and documentation in individual files.