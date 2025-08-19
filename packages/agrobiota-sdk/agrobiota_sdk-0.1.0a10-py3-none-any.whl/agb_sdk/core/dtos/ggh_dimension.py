from enum import Enum


class GGHDimension(Enum):
    Biodiversity = "biodiversity"
    BiologicalAgents = "biological-agents"
    BiologicalFertility = "biological-fertility"
    Pathogenicity = "pathogenicity"

    PhytosanitaryRisk = "phytosanitary-risk"
    """This is the same of `pathogenicity`."""
