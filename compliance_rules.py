# compliance_rules.py
# This is your "policy handbook" — a list of KYC rules your RAG system will search through.
# Think of this as the database of compliance knowledge your AI will refer to.

COMPLIANCE_RULES = [
    {
        "id": "rule_001",
        "rule": "Government-issued ID must not be expired. Expiry date must be clearly visible and the document must be valid at time of submission.",
        "category": "expiry"
    },
    {
        "id": "rule_002",
        "rule": "The name on the submitted document must exactly match the name provided during registration. Minor spelling variations may be flagged for manual review.",
        "category": "name_mismatch"
    },
    {
        "id": "rule_003",
        "rule": "Document must not show signs of tampering, digital editing, or physical alteration. Any signs of modification result in automatic rejection.",
        "category": "tampering"
    },
    {
        "id": "rule_004",
        "rule": "Accepted document types: Passport, National ID Card, Driver's License issued by a recognized government authority. Bank statements and utility bills are not accepted as primary ID.",
        "category": "document_type"
    },
    {
        "id": "rule_005",
        "rule": "Document image must be clear, fully visible, and legible. Blurry, cropped, or partially visible documents will be rejected.",
        "category": "image_quality"
    },
    {
        "id": "rule_006",
        "rule": "Date of birth on document must indicate the applicant is at least 18 years of age at time of application.",
        "category": "age_requirement"
    },
    {
        "id": "rule_007",
        "rule": "Documents from sanctioned countries or issued by unrecognized governments are automatically rejected per international compliance standards.",
        "category": "jurisdiction"
    },
    {
        "id": "rule_008",
        "rule": "MRZ (Machine Readable Zone) on passports must be fully visible and parseable. Covered or damaged MRZ is grounds for rejection.",
        "category": "mrz"
    }
]