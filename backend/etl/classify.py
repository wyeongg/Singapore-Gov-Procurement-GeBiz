"""Medical / life-science tender classification.

Three-signal hybrid approach:
1. Curated keyword regex (with subcategory assignment)
2. Hardcoded discriminative bigrams
3. Agency-based boost (with exclusion patterns for non-medical tenders)
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# 1. KEYWORD LISTS (by subcategory, word-boundary regex)
# ---------------------------------------------------------------------------

DIAGNOSTICS_KEYWORDS = [
    r"\bdiagnostic", r"\belisa\b", r"\bpcr\b", r"\bqpcr\b",
    r"\bassay\b", r"\bantibod", r"\bantigen", r"\bserology",
    r"\bserum\b", r"\bplasma\b", r"\bblood test", r"\bblood bank",
    r"\btransfusion", r"\bswab\b", r"\brapid test",
    r"\bwestern blot", r"\bgel electrophoresis",
    r"\bnucleic\b", r"\bgenome\b", r"\bgenomic", r"\bsequencing\b",
    r"\bplasmid", r"\bprimer\b", r"\bprobe\b",
    r"\brecombinant", r"\bmonoclonal", r"\bpolyclonal",
    r"\bhistology", r"\bcytology", r"\bhaematology", r"\bimmunology",
    r"\bvirology", r"\bbacteriology", r"\bmicrobiology", r"\btoxicology",
    r"\bpathology", r"\bfluorescence\b",
]

DEVICES_KEYWORDS = [
    # Imaging
    r"\bx-ray\b", r"\bultrasound\b", r"\bmri\b", r"\bct scan\b",
    r"\bmammograph", r"\bradiograph", r"\bradiology\b", r"\bfluoroscop",
    # Patient care
    r"\bdefibrillator", r"\bventilator\b", r"\binfusion pump",
    r"\bpatient monitor", r"\bhospital bed", r"\bwheelchair", r"\bstretcher",
    # Surgical
    r"\bsurgical\b", r"\bendoscop", r"\blaparoscop", r"\borthop",
    r"\bprosthe", r"\bimplant\b", r"\bcatheter", r"\bstent\b",
    # Lab instruments
    r"\bmicroscop", r"\bcentrifuge", r"\bautoclave", r"\bincubator",
    r"\bspectrophotometer", r"\bspectromet", r"\bchromatograph",
    r"\bflow cytometer", r"\bhplc\b", r"\bfreezer\b", r"\bultra-low",
    r"\bfume hood", r"\blaminar flow", r"\bbiosafety\b",
    r"\bmass spectrometer",
]

CONSUMABLES_KEYWORDS = [
    r"\breagent", r"\bpipette", r"\bmicropipette", r"\bsyringe",
    r"\bglove\b", r"\bgloves\b", r"\bppe\b", r"\bpersonal protective",
    r"\bface mask", r"\brespirator\b", r"\btest kit",
    r"\bpetri\b", r"\bagar\b", r"\bbuffer\b", r"\bculture media",
    r"\bcentrifuge tube", r"\bcoverslip",
    r"\bsterile\b", r"\bsteriliz", r"\bdisinfect", r"\bsanitiz",
    r"\blaboratory consumable", r"\bnursing consumable",
    r"\bvial\b", r"\bvials\b", r"\bcollection tube",
]

PHARMA_KEYWORDS = [
    r"\bpharmaceut", r"\bpharma\b", r"\bbiopharma",
    r"\bprescription", r"\bvaccin", r"\bimmuniz",
    r"\bclinical trial", r"\bgood manufacturing", r"\bgmp\b",
    r"\bcell culture", r"\bstem cell", r"\bprotein\b", r"\benzyme\b",
    r"\bbiotech", r"\bbioscience", r"\blife science", r"\blife-science",
]

DENTAL_KEYWORDS = [
    r"\bdental\b", r"\bdentist", r"\borthodont",
]

SERVICES_KEYWORDS = [
    r"\bmedical service", r"\bhealthcare service", r"\bhealth screen",
    r"\bhealth exam", r"\bnursing home",
    r"\bphysiotherapy", r"\brehabilitat", r"\bambulance",
    r"\bfirst aid\b", r"\bresuscit", r"\baed\b",
    r"\bpharmacy\b", r"\bpharmacist", r"\bdispensary",
    r"\bophthalm",
]

GENERAL_MEDICAL_KEYWORDS = [
    r"\bmedical\b", r"\bbiomedical\b", r"\bhospital\b",
    r"\bhealthcare\b", r"\bhealth care\b",
    r"\blaboratory\b", r"\blab equipment",
    r"\bdialysis", r"\bchemotherapy", r"\bradiotherapy",
]

# Ordered by specificity (most specific first)
SUBCATEGORY_KEYWORDS = [
    ("diagnostics", DIAGNOSTICS_KEYWORDS),
    ("devices", DEVICES_KEYWORDS),
    ("consumables", CONSUMABLES_KEYWORDS),
    ("pharma_biotech", PHARMA_KEYWORDS),
    ("dental", DENTAL_KEYWORDS),
    ("services", SERVICES_KEYWORDS),
    ("general", GENERAL_MEDICAL_KEYWORDS),
]

# ---------------------------------------------------------------------------
# 2. DISCRIMINATIVE BIGRAMS
# ---------------------------------------------------------------------------

MEDICAL_BIGRAMS = frozenset([
    "laboratory equipment", "laboratory consumables", "laboratory chemicals",
    "laboratory analytical", "laboratory testing", "laboratory use",
    "nursing consumables", "nursing laboratory",
    "mass spectrometer", "liquid chromatography", "gas chromatograph",
    "performance liquid",  # "high performance liquid chromatography"
    "analytical instruments",
    "medical services", "medical equipment", "medical council",
    "dental service", "dental filling",
    "health screening", "health centre", "community hospital",
    "plant health",  # SFA biosecurity
    "environmental health",  # NEA Environmental Health Institute
    "centrifuge tubes",
    "filling materials", "finishing materials",  # dental context
    "materials surgical",
    "calibration service",  # lab equipment calibration
    "water quality",  # water testing / lab
    "youth preventive",  # HPB preventive health
])

# ---------------------------------------------------------------------------
# 3. AGENCY SIGNALS
# ---------------------------------------------------------------------------

STRONG_MEDICAL_AGENCIES = frozenset([
    "Health Sciences Authority",
    "Health Promotion Board",
    "Ministry of Health-Ministry Headquarter",
    "Singapore Medical Council",
    "Singapore Nursing Board",
])

# Exclusion patterns: tenders from medical agencies that are NOT medical
EXCLUSION_KEYWORDS = [
    r"\bit system", r"\bit security", r"\bcybersecurity", r"\bsoftware",
    r"\bnetwork\b", r"\bserver\b", r"\bcloud\b", r"\bwebsite\b",
    r"\bconstruction\b", r"\brenovation", r"\bbuilding maintenance",
    r"\boffice renovation", r"\binterior design",
    r"\btransport service", r"\bcourier service",
    r"\bmarketing\b", r"\bpublic relation", r"\bcreative agency",
    r"\brecruitment\b", r"\bmanpower\b", r"\bhr service",
    r"\baudit service", r"\blegal service", r"\binsurance\b",
    r"\bsecurity guard", r"\bsecurity service",
    r"\bcleaning service", r"\bpest control",
]

# ---------------------------------------------------------------------------
# Pre-compile all regex patterns for performance
# ---------------------------------------------------------------------------

_COMPILED_SUBCATEGORIES = [
    (subcat, [re.compile(p, re.IGNORECASE) for p in patterns])
    for subcat, patterns in SUBCATEGORY_KEYWORDS
]

_COMPILED_EXCLUSIONS = [re.compile(p, re.IGNORECASE) for p in EXCLUSION_KEYWORDS]


def _extract_bigrams(text: str) -> set[str]:
    """Extract consecutive word bigrams from lowered text."""
    words = re.findall(r"[a-z]+", text.lower())
    return {f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)}


# ---------------------------------------------------------------------------
# 4. MAIN CLASSIFICATION FUNCTION
# ---------------------------------------------------------------------------

def classify_tender(description: str, agency: str) -> tuple[bool, str | None, str]:
    """Classify a single tender as medical/life-science.

    Returns:
        (is_medical, subcategory, classification_source)
        - is_medical: True if classified as medical/life-science
        - subcategory: e.g. 'devices', 'diagnostics', or None
        - classification_source: 'keyword', 'bigram', 'agency', or 'none'
    """
    # Step 1: Keyword match (with subcategory)
    for subcat, compiled_patterns in _COMPILED_SUBCATEGORIES:
        for pattern in compiled_patterns:
            if pattern.search(description):
                return (True, subcat, "keyword")

    # Step 2: Bigram match
    bigrams = _extract_bigrams(description)
    if bigrams & MEDICAL_BIGRAMS:
        return (True, None, "bigram")

    # Step 3: Strong agency signal (if no exclusion hit)
    if agency in STRONG_MEDICAL_AGENCIES:
        has_exclusion = any(p.search(description) for p in _COMPILED_EXCLUSIONS)
        if not has_exclusion:
            return (True, None, "agency")

    return (False, None, "none")
