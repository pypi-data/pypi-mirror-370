from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from inoopa_utils.custom_types.addresses import (
    Country,
    ProvinceBe,
    ProvinceFr,
    ProvinceNl,
    RegionBe,
    RegionFr,
    RegionNl,
)
from inoopa_utils.custom_types.legal_filters import EmployeeCategoryClass, EntityType, LegalFormBe, LegalFormCategory

MongoFilters = dict[str, dict[str, dict[str, int | str | list[str]]]]

AdditionalFields = Literal["email", "phone", "website", "nace_codes", "social_medias"]


class LeadGenerationCompanyFilters(BaseModel):
    """
    Represents the filters used to generate the leads.

    This is a pydantic model, so it can be used in the apis as a parameter.
    """

    additional_fields: list[AdditionalFields] | None = ["email", "phone", "website", "nace_codes", "social_medias"]

    countries: list[Country] | None = None
    regions: list[RegionBe | RegionFr | RegionNl] | None = None
    provinces: list[ProvinceBe | ProvinceFr | ProvinceNl] | None = None
    zipcodes: list[str] | None = None
    declared_best_nace_codes: list[str] | None = None
    declared_best_nace_codes_regex: str | None = None
    inoopa_best_nace_codes: list[str] | None = None
    inoopa_best_nace_codes_regex: str | None = None

    minimum_number_of_estanlishments: int | None = None
    maximum_number_of_estanlishments: int | None = None
    employee_categories: list[EmployeeCategoryClass] | None = None
    created_before: datetime | None = None
    created_after: datetime | None = None
    include_decision_makers: bool = False

    max_results: int | None = None
    excluded_companies: list[str] | None = None

    legal_form_Categories: list[LegalFormCategory] | None = None
    legal_forms: list[LegalFormBe] | None = None
    entity_types: list[EntityType] | None = None

    def to_mongo_filters(
        self,
        only_include_companies_with_phone_no_do_not_call_me: bool = False,
        only_include_companies_with_email: bool = False,
        only_include_companies_with_website: bool = False,
        only_include_companies_with_nace_codes: bool = False,
        only_include_active_companies: bool = True,
    ) -> MongoFilters:
        """
        Generate a MongoDB filter to search for companies based on the LeadGenerationCompanyFilters.

        can be used as a filter parameter in the MongoDB Collection.find() method.
        """
        filters = {}
        if self.countries:
            filters["country"] = {"$in": [c.value for c in self.countries]}
        if self.legal_forms:
            filters["legal_form"] = {"$in": [form.value for form in self.legal_forms]}
        if self.employee_categories:
            filters["employee_category_formatted"] = {"$in": [c.value for c in self.employee_categories]}
        if self.regions:
            regions = [r.value if r.value != RegionBe.not_found.value else None for r in self.regions]
            filters["address.region"] = {"$in": regions}
        if self.provinces:
            provinces = [p.value if p.value != ProvinceBe.not_found.value else None for p in self.provinces]
            filters["address.province"] = {"$in": provinces}
        if self.zipcodes:
            zipcodes = [z if z != "NOT FOUND" else None for z in self.zipcodes]
            filters["address.postal_code"] = {"$in": zipcodes}

        if self.minimum_number_of_estanlishments and self.maximum_number_of_estanlishments:
            filters["number_of_establishments"] = {
                "$gte": self.minimum_number_of_estanlishments,
                "$lte": self.maximum_number_of_estanlishments,
            }
        elif self.minimum_number_of_estanlishments:
            filters["number_of_establishments"] = {"$gte": self.minimum_number_of_estanlishments}
        elif self.maximum_number_of_estanlishments:
            filters["number_of_establishments"] = {"$lte": self.maximum_number_of_estanlishments}

        if self.declared_best_nace_codes:
            filters["$or"] = [
                {"nace_codes": {"$elemMatch": {"number": {"$in": self.declared_best_nace_codes}}}},
                {
                    "establishments": {
                        "$elemMatch": {"nace_codes": {"$elemMatch": {"number": {"$in": self.declared_best_nace_codes}}}}
                    }
                },
            ]
        if self.declared_best_nace_codes_regex:
            nace_section_codes = []
            naces_codes_regex = []
            for code_regex in self.declared_best_nace_codes_regex.split("|"):
                # if the regex is only one letter, it's a nace section code
                if len(code_regex) == 1:
                    nace_section_codes.append(code_regex)
                else:
                    # if the regex is more than one letter, it's a nace code regex
                    naces_codes_regex.append(code_regex)

            filters["$or"] = []
            if naces_codes_regex:
                filters["$or"].append(
                    {"nace_codes": {"$elemMatch": {"number": {"$regex": "|".join(naces_codes_regex)}}}}
                )
                filters["$or"].append(
                    {
                        "establishments": {
                            "$elemMatch": {
                                "nace_codes": {"$elemMatch": {"number": {"$regex": "|".join(naces_codes_regex)}}}
                            }
                        }
                    },
                )
            if nace_section_codes:
                filters["$or"].append({"nace_codes": {"$elemMatch": {"section_code": {"$in": nace_section_codes}}}})
                filters["$or"].append(
                    {
                        "establishments": {
                            "$elemMatch": {"nace_codes": {"$elemMatch": {"section_code": {"$in": nace_section_codes}}}}
                        }
                    },
                )

        if self.inoopa_best_nace_codes:
            filters["best_nace_codes.first_best_nace_code.number"] = {"$in": self.inoopa_best_nace_codes}
        if self.inoopa_best_nace_codes_regex:
            nace_codes = []
            nace_section_codes = []
            for code_regex in self.inoopa_best_nace_codes_regex.split("|"):
                # if the regex is only one letter, it's a nace section code
                if len(code_regex) == 1:
                    nace_section_codes.append(code_regex)
                else:
                    # if the regex is more than one letter, it's a nace code regex
                    nace_codes.append(code_regex)
            filters["$or"] = []
            if nace_codes:
                filters["$or"].append({"best_nace_codes.first_best_nace_code.number": {"$regex": "|".join(nace_codes)}})
            if nace_section_codes:
                filters["$or"].append(
                    {"best_nace_codes.first_best_nace_code.section_code": {"$in": nace_section_codes}}
                )

        if self.legal_form_Categories:
            filters["legal_form_type"] = {"$in": [c.value for c in self.legal_form_Categories]}
        if self.entity_types:
            filters["entity_type"] = {"$in": [e.value for e in self.entity_types]}
        if self.created_before and not self.created_after:
            filters["start_date"] = {"$lte": self.created_before}
        if self.created_after and not self.created_before:
            filters["start_date"] = {"$gte": self.created_after}
        if self.created_before and self.created_after:
            filters["start_date"] = {"$lte": self.created_before, "$gte": self.created_after}
        if self.excluded_companies:
            filters["_id"] = {"$nin": self.excluded_companies}
        if only_include_active_companies:
            filters["status"] = "Active"
            filters["legal_situation"] = "Normal situation"

        if only_include_companies_with_phone_no_do_not_call_me:
            filters["best_phone"] = {"$ne": None}
            filters["best_phone.phone"] = {"$nin": ["DO_NOT_CALL_ME", None]}

        if only_include_companies_with_email:
            filters["best_email"] = {"$ne": None}
        if only_include_companies_with_website:
            filters["best_website"] = {"$ne": None}
        if only_include_companies_with_nace_codes:
            filters["best_nace_codes"] = {"$ne": None}
        return filters

    def to_dict(self) -> dict:
        data_dict = self.model_dump()
        # Convert datetime objects to isoformat for json serialization
        if self.created_before:
            data_dict["created_before"] = _datetime_serializer(self.created_before)
        if self.created_after:
            data_dict["created_after"] = _datetime_serializer(self.created_after)
        return data_dict


class EnrichmentCompanyFilters(BaseModel):
    vats_to_enrich: list[str]
    country: Country = Country.belgium
    additional_fields: list[AdditionalFields] = ["email", "phone", "website", "nace_codes", "social_medias"]
    include_decision_makers: bool = False

    def to_mongo_filters(
        self,
        only_include_companies_with_phone_no_do_not_call_me: bool = False,
        only_include_companies_with_email: bool = False,
        only_include_companies_with_website: bool = False,
        only_include_companies_with_nace_codes: bool = False,
    ) -> MongoFilters:
        filters = {"country": self.country.value, "_id": {"$in": self.vats_to_enrich}}
        if only_include_companies_with_phone_no_do_not_call_me:
            filters["best_phone"] = {"$ne": None}
        if only_include_companies_with_email:
            filters["best_email"] = {"$ne": None}
        if only_include_companies_with_website:
            filters["best_website"] = {"$ne": None}
        if only_include_companies_with_nace_codes:
            filters["best_nace_codes"] = {"$ne": None}
        return filters

    def to_dict(self) -> dict:
        return self.model_dump()


class SemanticSearchCompanyFilters(BaseModel):
    countries: list[Country] = Country.get_all_values()
    regions: list[RegionBe | RegionFr | RegionNl] | None = None
    zipcodes: list[str] | None = None
    declared_best_nace_codes: list[str] | None = None
    declared_best_nace_codes_regex: str | None = None
    inoopa_best_nace_codes: list[str] | None = None
    inoopa_best_nace_codes_regex: str | None = None

    minimum_number_of_estanlishments: int | None = None
    maximum_number_of_estanlishments: int | None = None
    employee_categories: list[EmployeeCategoryClass] | None = None
    created_before: datetime | None = None
    created_after: datetime | None = None
    include_decision_makers: bool = False

    max_results: int | None = None
    excluded_companies: list[str] | None = None

    legal_form_types: list[LegalFormCategory] | None = None
    legal_forms: list[LegalFormBe] | None = None

    additional_fields: list[AdditionalFields] | None = None

    def to_dict(self) -> dict:
        data_dict = self.model_dump()
        # Convert datetime objects to isoformat for json serialization
        if self.created_before:
            data_dict["created_before"] = _datetime_serializer(self.created_before)
        if self.created_after:
            data_dict["created_after"] = _datetime_serializer(self.created_after)
        return data_dict


def _datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
