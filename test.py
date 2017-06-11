import inflect

p = inflect.engine()

singularKeys={
    'MQ2_1': ["toxicity", "safety", "health", "exposure", "human", "population", "public", "worker", "occupational",
              "man", "woman", "male", "female", "girl", "boy", "child", "infant", "adult", "consumer", "patient",
              "volunteer", "clinical", "cohort", "risk", "hazard", "blood-brain barrier", "immune", "immunological",
              "inflammation", "inflammatory", "cytotoxic", "cytotoxicity", "cytotoxin", "teratogen", "teratogenic",
              "carcinogen", "carcinogenic", "carcinogenicity", "neurotoxicity", "neurotoxin", "neurotoxin",
              "nephrotoxicity", "nephrotoxic", "hepatotoxicity", "hepatotoxin", "hepatotoxic", "endocrine",
              "hormonal", "hormone", "reproductive", "genotoxicity", "genotoxic", "cancer", "acute", "chronic",
              "review", "reviewed", "ingestion", "ingest", "oral", "orally", "consumption", "consumed", "consume",
              "intake", "absorption", "metabolism", "metabolize", "metabolic", "epidermal", "epithelial", "epithelium",
              "dermal", "dermis", "skin", "inhale", "inhaled", "inhalation", "dust", "vapour", "vapourized", "aerosol",
              "aerosolized", "aerosolised", "atmospheric", "pulmonary", "bioaccumulation", "bioaccumulative",
              "uptake", "excretion", "elimination", "bio-available", "bioavailable", "bioavailability", "synergism",
              "synergist", "synergistic", "agonist", "agonistic", "antagonist", "antagonistic", "blood", "brain",
              "cortex", "liver", "plasma", "NOAEL", "LOAEL", "NOEL", "LOEL", "TDI", "LD", "TD", "ED", "effective dose",
              "tolerable dose", "lethal dose", "threshold limit value", "TLV", "threshold dose", "NOEC",
              "no observable effect concentration", "IC", "inhibitory concentration",
              "(LC|EC|LD|ED|IC)[ -]?(50|₅₀)"],

    'MQ3_1': ["environment", "impact", "manufacturing", "consumption", "recycling", "disposal", "environmental",
              "ecotoxicology", "ecotoxicological", "ecotoxicity", "ecological", "ecology", "sustainable",
              "sustainably", "sustainability", "ecosystem", "trophic", "aquatic", "soil", "troposphere",
              "tropospheric", "atmospheric", "river", "freshwater", "marine", "waste", "waste-water", "wastewater",
              "biodiversity", "bio-indicator", "bioindicator", "biomonitor", "bio-monitor", "recovery", "recovered",
              "recycled", "recycling", "recycle", "recyclable", "disposal", "life-cycle", "life cycle", "biodegradable",
              "biodegradation", "biodegrade", "bio-degradable", "bio-degradation", "bio-degrade", "decompose",
              "decomposed", "decomposition", "consumption"],

    'MQ4_1': ["nanoparticle", "nanomaterial", "nanoscale", "nanosized", "nano", "ultrafine", "combustion",
              "coal-derived", "coal-fired", "engine", "motor[ ]vehicle", "airborne", "incidental", "aerosols",
              "naturally[ ]occurring", "dust", "mining", "raw[ ]material", "mineralogy", "ash"],

    'HUM': ["human", "man", "woman", "girl", "boy", "child", "infant", "adult", "cohort", "consumer",
            "clinical", "clinical trial", "patient", "worker", "employee", "volunteer", "health risk"],

    'LVL': ["NOAEL", "LOAEL", "NOEL", "LOEL", "TDI", "LD", "TD", "ED effective dose", "tolerable dose", "lethal dose",
            "threshold limit value", "TLV", "threshold dose", "NOEC", "no observable effect concentration", "IC",
            "inhibitory concentration", "(LC|EC|LD|ED|IC)[ -]?(50|₅₀)"],

    'REV': ["review", "reviewed"],

    'CTX': ["blood[-]?brain barrier", "immune", "immunological", "inflammation", "inflammatory", "cytotoxic",
            "cytotoxicity", "cytotoxin", "teratogen", "teratogenic", "carcinogen", "carcinogenic",
            "carcinogenicity", "neurotoxin", "neurotoxic", "neurotoxicity", "nephrotoxic", "nephrotoxicity",
            "nephrotoxin", "hepatotoxic", "hepatotoxicity", "hepatotoxin", "hepatotoxic", "hepatotoxicity",
            "endocrine", "hormonal", "hormone", "reproductive", "genotoxic", "genotoxin", "cancer", "acute",
            "chronic", "symptom"],

    'ERM': ["ingest", "ingestion", "oral", "orally", "consumption", "consumed", "consume", "intake", "absorption",
            "metabolism", "metabolic", "metabolise", "epidermis", "epidermal", "epithelial", "epithelium", "Dermal",
            "Dermis", "skin", "inhale", "inhaled", "inhalation", "dust", "vapour", "vapourised", "aerosoli[sz]ed",
            "aerosol", "atmospheric", "pulmonary", "bioaccumulation", "bioaccumulative", "uptake", "excretion",
            "elimination", "bio[-]?available", "bioavailability", "synergist", "synergistic", "agonist", "agonistic",
            "antagonists", "antagonistic", "blood", "brain", "cortex", "liver", "plasma", "respiratory"],

    'ETX': ["ecotoxicology", "ecotoxicological", "ecotoxicology", "ecotoxicity", "toxicity", "toxic",
            "trophic", "aquatic", "soil", "troposphere", "tropospheric", "atmospheric", "river", "freshwater", "marine",
            "bio-indicator", "indicator", "community"],
    'IND': ["manufacturing", "manufacture", "manufactured", "industry", "industrial", "waste", "waste-water",
            "waste water", "wastewater", "recovery", "recovered", "produce", "produced", "production", "life-cycle",
            "life cycle", "commercial"],
    'SUS': ["sustainable", "sustainably", "sustainability", "recycled", "recycling", "recycle", "recyclable",
            "disposal", "biodegradable", "biodegradation", "biodegrade", "bio-degradable", "bio-degradation",
            "bio-degrade", "decompose", "decomposed", "decomposition", "ecological"]
}

plsngKeys = dict()
for key in singularKeys.keys():
    value = str(r"\b")
    for elem in singularKeys[key]:
            value += p.plural(elem) + "|" if  elem != '(LC|EC|LD|ED|IC)[ -]?(50|₅₀)' else ''
            value += elem + "|"
    value = value.rstrip('|') + r"\b"
    plsngKeys[key] = value

print (plsngKeys)