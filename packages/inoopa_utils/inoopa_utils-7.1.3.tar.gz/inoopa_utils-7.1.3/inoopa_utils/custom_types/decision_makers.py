from bson import ObjectId
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class DecisionMakerDepartment(Enum):
    """The department of the decision maker."""

    it_RND = "IT / R&D"
    sales_marketing_communication = "Sales / Marketing / Communication"
    legal = "Legal"
    finance = "Finance"
    ceo_board = "CEO / Board"
    purchase_logistic_safety = "Purchase / Logistic / Safety"
    human_resources = "Human Resources"
    customer_support = "Customer Support"
    enviromental_esg = "Environmental / ESG"
    not_working = "Not working anymore / Not a person / Not a role"
    unknown = "UNKNOWN"

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


responsibilities_level_mapper: dict[int, str] = {
    1: "C-Level / Director / Board / Chief / Owner / Founder",
    2: "Manager / Middle management",
    3: "Employee (Senior)",
    4: "Employee (Junior/Medior)",
    5: "UNKNOWN",
    6: "Not working anymore / Not a person / Not a role",
}


@dataclass(slots=True)
class DecisionMaker:
    # Foreign key to the `company` collection
    company_id: str
    firstname: str
    lastname: str
    source: str
    # The raw string from the source, will cleaned and classified into `function_string`
    raw_function_string: str
    last_seen: datetime
    last_email_check: datetime | None = None
    _id: ObjectId = field(default_factory=ObjectId)
    function_string: str | None = None
    email: str | None = None
    email_score: int | None = None
    language: str | None = None
    linkedin_url: str | None = None
    department: str | None = None
    responsibility_level_code: int | None = None
    responsibility_level_formatted: str | None = None


@dataclass(slots=True)
class DecisionMakerLegacy:
    """
    Decision makers imported from the legacy SQL database.

    This is deperecated and kept for reference purpose only.
    """

    # Company ID (same _id as in company collection with leading zeros BE:012345667)
    company_id: str
    # Company ID (id in the old format (VAT without leading zeros) BE:12345667)
    legacy_entity_id: str
    name: str | None = None
    firstname: str | None = None
    # deprecated
    language: str | None = None
    # Gender (deprecated)
    sex: str | None = None
    # deprecated
    function: str | None = None
    source: str | None = None
    function_string: str | None = None
    linkedin_url: str | None = None
    email: str | None = None
    email_source: str | None = None
    email_score: int | None = None
    blacklisted: str | None = None
    # deprecated
    phone: str | None = None
    cluster: str | None = None
    cluster_score: int | None = None
    # cluster match
    best_match: str | None = None
    position_request_base: int | None = None
    position_request_ceo: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    google_last_seen: datetime | None = None
    norbert_last_seen: datetime | None = None
