import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import DESCENDING, MongoClient, ASCENDING, TEXT
from concurrent.futures import ThreadPoolExecutor
from pymongo.errors import OperationFailure, DocumentTooLarge

from inoopa_utils.inoopa_logging import create_logger
from inoopa_utils.custom_types.decision_makers import DecisionMaker

load_dotenv()


class DbManagerMongo:
    """
    This class is used to manage the Mongo database.

    :param mongo_uri: The URI of the Mongo database to connect to.
    :param create_index_if_not_done: If the MongoDB indexes should be created if they don't exist.

    :attribute company_collection: The company collection object.
    :attribute do_not_call_me_collection: The do not call me collection object.
    :attribute decision_maker_collection: The decision maker collection object.
    :attribute company_keywords: The company keywords collection object.
    :attribute kaspr_cache: The kaspr cache collection object.
    :attribute delivery_memory_collection: The delivery memory collection object.
    :attribute api_users_collection: The api users collection object.
    :attribute stats_company_collection: Collection to hold metrics about companies over time.
    :attribute stats_nace_collection: Collection to hold metrics about NACE codes distribution over time.
    :attribute stats_decision_makers_collection: Collection to hold metrics about decision makers over time.

    :method update_do_not_call_me: Update the do_not_call_me collection in the database with a list of phone numbers.
    """

    def __init__(
        self,
        mongo_uri: str = os.environ["MONGO_READWRITE_PROD_URI"],
        create_index_if_not_done: bool = False,
        pretty_logging: bool = False,
    ):
        self._logger = create_logger("INOOPA_UTILS.DB_MANAGER.MONGO", pretty=pretty_logging)
        self._env = os.environ.get("ENV", "dev")

        _client = MongoClient(mongo_uri)
        self._db = _client[self._env]

        # Companies data Collections
        self.company_collection = self._db.get_collection("company")
        self.decision_maker_collection = self._db.get_collection("decision_maker")
        self.website_structure_collection = self._db.get_collection("website_structure")

        # Stats collection
        self.stats_company_collection = self._db.get_collection("stats_company")
        self.stats_nace_collection = self._db.get_collection("stats_nace")
        self.stats_decision_makers_collection = self._db.get_collection("stats_decision_makers")

        # Internal utils Collections
        self.do_not_call_me_collection = self._db.get_collection("do_not_call_me")
        self.phone_operators_cache_collection = self._db.get_collection("phone_operators_cache")
        self.delivery_memory_collection = self._db.get_collection("delivery_memory")
        self.api_users_collection = self._db.get_collection("api_users")
        self.kaspr_cache_collection = self._db.get_collection("kaspr_cache")

        # Legacy collections
        self.company_keywords = self._db.get_collection("company_keywords")

        if create_index_if_not_done:
            self._create_indexes()

    def update_do_not_call_me(self, phones: list[str]) -> None:
        """
        Method to update the do_not_call_me collection in the database.

        :param list[str]: The list of phone numbers to add to the do_not_call_me collection.
        """
        batch_size = 10_000
        phones_batch = [phones[i : i + batch_size] for i in range(0, len(phones), batch_size)]

        # We use a thread pool to update the database faster
        with ThreadPoolExecutor() as executor:
            executor.map(self._run_batch_update_do_not_call_me, phones_batch)
        self._logger.info(f"Updated {len(phones):_} phones in DoNotCallMe collection")

    def _run_batch_update_do_not_call_me(self, phone_batch: list[str]) -> None:
        """
        Method to update a chunk of the do_not_call_me collection in the database.

        :param updates: The list of DB update to execute.
        """
        batch_set = set(phone_batch)
        self._logger.info(f"Filtering {len(phone_batch)} phones...")
        existing_numbers = set(
            item["phone"] for item in self.do_not_call_me_collection.find({"phone": {"$in": list(batch_set)}})
        )
        new_numbers = [{"phone": number} for number in batch_set - existing_numbers]
        # Bulk insert new numbers
        if new_numbers:
            self._logger.info(f"Inserting {len(new_numbers)} new phones in collection...")
            self.do_not_call_me_collection.insert_many(new_numbers, ordered=False)
        else:
            self._logger.info("No new phones to insert found in batch")

    def _create_indexes(self) -> None:
        """Create the indexes in the Mongo database if they don't exist."""
        fields_to_index_kaspr_cache = [
            [("_id", ASCENDING)],
            [("profile.id", ASCENDING)],
            [("profile.starryWorkEmail", ASCENDING)],
        ]
        fields_to_index_decision_makers = [
            [("company_id", ASCENDING)],
            [("legacy_entity_id", ASCENDING)],
            [("email", ASCENDING)],
            [("best_match", ASCENDING)],
            [("function_string", ASCENDING)],
            [("linkedin_url", ASCENDING)],
        ]
        fields_to_index_company = [
            [("address.string_address", ASCENDING)],
            [("address.region", ASCENDING)],
            [("address.postal_code", ASCENDING)],
            [("legal_form_type", ASCENDING)],
            [("best_website", ASCENDING)],
            [("best_website.website", ASCENDING)],
            [("best_email", ASCENDING)],
            [("best_phone", ASCENDING)],
            [("board_members.name", ASCENDING)],
            [("country", ASCENDING)],
            [("employee_category_code", ASCENDING)],
            [("establishments.name", ASCENDING)],
            [("name", ASCENDING)],
            [("status", ASCENDING)],
            [("name_text", TEXT)],
        ]
        fields_to_index_website_structure = [
            [("_id", ASCENDING)],  # Base url
            [("domain", ASCENDING)],
            [("last_crawling", ASCENDING)],
            [("companies_id", ASCENDING)],
            [("home_url", ASCENDING)],
            [("about_url", ASCENDING)],
            [("contact_url", ASCENDING)],
        ]
        fields_to_index_company_keywords = [
            [("company_id", ASCENDING)],
        ]
        fields_to_index_delivery_memory = [
            [("company_id", ASCENDING)],
            [("best_phone.phone", ASCENDING)],
            [("best_email.email", ASCENDING)],
            [("best_website.website", ASCENDING)],
            [("delivery_date", ASCENDING)],
            [("decision_maker_ids", ASCENDING)],
        ]
        fields_to_index_phone_operators_cache = [
            [("operator", ASCENDING)],
            [("operator_last_update", ASCENDING)],
            [("last_update", ASCENDING)],
            [("_id", ASCENDING)],
        ]
        fields_to_index_do_no_call_me = [[("phone", ASCENDING)]]
        fields_to_index_stats = [
            [("date", DESCENDING)],
            [("country", ASCENDING)],
        ]
        self._logger.info("Creating indexes in collections (if not created yet)...")
        self._logger.info(
            "If this takes time (~10 mins), the indexes are not created yet. You will get a message when it's done."
        )

        collections_to_index = [
            {self.company_collection: fields_to_index_company},
            {self.decision_maker_collection: fields_to_index_decision_makers},
            {self.website_structure_collection: fields_to_index_website_structure},
            {self.company_keywords: fields_to_index_company_keywords},
            {self.delivery_memory_collection: fields_to_index_delivery_memory},
            {self.do_not_call_me_collection: fields_to_index_do_no_call_me},
            {self.phone_operators_cache_collection: fields_to_index_phone_operators_cache},
            {self.kaspr_cache_collection: fields_to_index_kaspr_cache},
            {self.stats_company_collection: fields_to_index_stats},
            {self.stats_decision_makers_collection: fields_to_index_stats},
            {self.stats_nace_collection: fields_to_index_stats},
        ]

        for indexer in collections_to_index:
            for collection, fields in indexer.items():
                for index in fields:
                    self._logger.debug(f"Creating index {index} in `{collection.name}` collection...")
                    try:
                        if index[0][0] != "_id":
                            collection.create_index(index, background=True)
                        else:
                            collection.create_index(index)
                    # Skip if index already exists
                    except OperationFailure as ex:
                        print(ex)
                        continue
        self._logger.info("Indexes created in all collections")

    def add_decision_makers_to_company(
        self, company_id: str, only_decision_makers_with_email: bool = False
    ) -> list[DecisionMaker]:
        """
        Add decision makers to companies list of dicts.

        :param companies: List of dicts containing companies data.
            Each company should contains a key `_id` or `registered_number`.
        :return: the list of decision makers objects.
        """
        self._logger.debug(f"Adding decision makers to company: {company_id}")
        filters: dict = {"company_id": company_id}
        if only_decision_makers_with_email:
            filters["email"] = {"$nin": [None, ""]}
        decision_makers = self.decision_maker_collection.find(filters)
        if decision_makers:
            decision_makers = [DecisionMaker(**decision_maker) for decision_maker in decision_makers]
            self._logger.info(f"Found {len(decision_makers)} decision makers for company: {company_id}")
            return decision_makers

        self._logger.debug(f"No decision makers found for company: {company_id}")
        return []


def _filter_decision_makers_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find all duplicates, keep the row with the most information in the email and linkedin_url columns.
    Ensure rows without decision makers are retained.
    """
    if df.empty or "decision_maker_firstname" not in df.columns or "decision_maker_lastname" not in df.columns:
        return df
    df["decision_maker_firstname"] = df["decision_maker_firstname"].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    df["decision_maker_lastname"] = df["decision_maker_lastname"].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    if "registration_number" in df.columns:
        id_column = "registration_number"
    elif "_id" in df.columns:
        id_column = "_id"
    else:
        raise ValueError("The companies dataframe should contain a column `_id` or `registration_number`.")

    # Identify the subset of columns to group by
    group_columns = [id_column, "decision_maker_firstname", "decision_maker_lastname"]

    # Split the dataframe into two subsets: with and without decision maker data
    df_with_dm = df[df["decision_maker_firstname"].notna() | df["decision_maker_lastname"].notna()]
    df_without_dm = df[df["decision_maker_firstname"].isna() & df["decision_maker_lastname"].isna()]

    if not df_with_dm.empty:
        # Count the number of NaNs in the relevant columns for each row
        df_with_dm["nan_count"] = df_with_dm[["decision_maker_email", "decision_maker_linkedin_url"]].isna().sum(axis=1)
        # Find the index of the row with the minimum NaN count in each group
        idx = df_with_dm.groupby(group_columns)["nan_count"].idxmin()
        # Select the rows with the least NaNs within each group
        filtered_with_dm = df_with_dm.loc[idx].drop(columns=["nan_count"], errors="ignore")
    else:
        filtered_with_dm = pd.DataFrame(columns=df.columns)

    # Combine the df with and without decision makers
    result = pd.concat([filtered_with_dm, df_without_dm], ignore_index=True)
    result = result.reset_index(drop=True)
    return result


def _count_decision_makers(df: pd.DataFrame) -> int:
    """Count the number of decision makers for each company."""
    if "decision_maker_firstname" not in df.columns:
        return 0
    return df["decision_maker_firstname"].notna().sum()


def enrich_companies_df_with_decision_makers(
    companies_df: pd.DataFrame,
    decision_makers_department: list[str | None],
    decision_makers_responsibility_level: list[str | None],
    db_manager: DbManagerMongo | None = None,
    only_decision_makers_with_email: bool = False,
    streamlit_user_logger=None,
) -> pd.DataFrame:
    """
    Add decision makers to a companies dataframe.

    :param companies_df: The companies dataframe to enrich. Should contain a column `__id` or `registered_number`.
    :param streamlit_user_logger: The streamlit user logger to use for logging. No typing here to avoid including streamlit in the dependencies.
    :return: The companies dataframe with the decision makers added.
        If multiple decision makers are found for one company, will create multiple rows for the company.
    """
    if companies_df.empty:
        return companies_df
    if db_manager is None:
        db_manager = DbManagerMongo()
    db_manager._logger.info("Adding decision makers to companies dataframe...")
    if "_id" in companies_df.columns:
        id_column = "_id"
    elif "registration_number" in companies_df.columns:
        id_column = "registration_number"
    else:
        raise ValueError("The companies dataframe should contain a column `_id` or `registered_number`.")

    companies_ids = list(set(companies_df[id_column].to_list()))
    db_manager._logger.info(f"counting companies with decision makers: {len(companies_ids)}")

    # Graydon DMs are not good enough. So we exclude them.
    filters = {
        "company_id": {"$in": companies_ids},
        "source": {"$ne": "graydon"},
        "department": {"$in": decision_makers_department},
        "responsibility_level_formatted": {"$in": decision_makers_responsibility_level},
    }
    if only_decision_makers_with_email:
        filters["email"] = {"$nin": [None, ""]}

    try:
        companies_with_dms = {}
        if streamlit_user_logger:
            streamlit_user_logger.log_progress(f"Looking for decision makers for **{len(companies_ids)}** companies")
        companies_with_dms_cursor = db_manager.decision_maker_collection.find(filters)
        for company in companies_with_dms_cursor:
            if company["company_id"] in companies_with_dms:
                companies_with_dms[company["company_id"]].append(company)
            else:
                companies_with_dms[company["company_id"]] = [company]

        companies_with_dms_ids = set([company_id for company_id in companies_with_dms.keys()])
    except DocumentTooLarge:
        db_manager._logger.info("The decision maker results are too large, batching the query...")
        companies_with_dms = {}
        companies_with_dms_ids = set()
        batch_size = 10_000
        for i in range(0, len(companies_ids), batch_size):
            filters = {"company_id": {"$in": companies_ids[i : i + batch_size]}}
            if only_decision_makers_with_email:
                filters["email"] = {"$nin": [None, ""]}
            batch_companies_with_dms = db_manager.decision_maker_collection.find(filters).skip(i).limit(batch_size)
            companies_with_dms.update({company["company_id"]: company for company in batch_companies_with_dms})
            companies_with_dms_ids.update(
                set(
                    [
                        company["company_id"]
                        for company in db_manager.decision_maker_collection.find(filters).skip(i).limit(batch_size)
                    ]
                )
            )
    log_message = f"Found **{len(companies_with_dms_ids)} companies** with decision makers"
    db_manager._logger.info(log_message)
    if streamlit_user_logger:
        streamlit_user_logger.log_success(log_message)
    if streamlit_user_logger:
        streamlit_user_logger.log_progress("Adding decision makers to companies...")
    new_rows = []
    for i, row in companies_df.iterrows():
        if row[id_column] not in companies_with_dms_ids:
            continue
        decision_makers = companies_with_dms[row[id_column]]
        if not decision_makers:
            continue
        else:
            if decision_makers and not isinstance(decision_makers, list):
                decision_makers = [decision_makers]
            # If there are multiple decision makers, create a new row for each one
            for y, decision_maker in enumerate(decision_makers):
                try:
                    decision_maker = DecisionMaker(**decision_maker)
                except TypeError as e:
                    error = f"Error with decision makers: `{decision_maker}` from company: {row[id_column]}"
                    if streamlit_user_logger:
                        streamlit_user_logger.log_progress(error)
                    print(error)
                    raise e
                if y == 0:
                    # Update the original row with the first decision maker's information
                    companies_df.at[i, "decision_maker_firstname"] = decision_maker.firstname
                    companies_df.at[i, "decision_maker_lastname"] = decision_maker.lastname
                    companies_df.at[i, "decision_maker_email"] = decision_maker.email
                    companies_df.at[i, "decision_maker_language"] = decision_maker.language
                    companies_df.at[i, "decision_maker_department"] = decision_maker.department
                    companies_df.at[i, "decision_maker_responsibility_level_formatted"] = (
                        decision_maker.responsibility_level_formatted
                    )
                    companies_df.at[i, "decision_maker_responsibility_level_code"] = (
                        decision_maker.responsibility_level_code
                    )
                    companies_df.at[i, "decision_maker_linkedin_url"] = decision_maker.linkedin_url
                    companies_df.at[i, "decision_maker_function"] = (
                        decision_maker.function_string or decision_maker.raw_function_string
                    )
                else:
                    # Create new rows for additional decision makers
                    new_row = row.copy()
                    new_row["decision_maker_firstname"] = decision_maker.firstname
                    new_row["decision_maker_lastname"] = decision_maker.lastname
                    new_row["decision_maker_email"] = decision_maker.email
                    new_row["decision_maker_language"] = decision_maker.language
                    new_row["decision_maker_linkedin_url"] = decision_maker.linkedin_url
                    new_row["decision_maker_department"] = decision_maker.department
                    new_row["decision_maker_responsibility_level_formatted"] = (
                        decision_maker.responsibility_level_formatted
                    )
                    new_row["decision_maker_responsibility_level_code"] = decision_maker.responsibility_level_code
                    new_row["decision_maker_function"] = (
                        decision_maker.function_string or decision_maker.raw_function_string
                    )
                    new_rows.append(new_row)

    if new_rows:
        companies_df = pd.concat([companies_df, pd.DataFrame(new_rows)], ignore_index=True)
    # make sure the companies are displayed in the same order as the original dataframe
    if streamlit_user_logger:
        streamlit_user_logger.log_success("Decision makers added!")
        streamlit_user_logger.log_progress(
            f"Filtering duplicate decision makers. Before filtering: {_count_decision_makers(companies_df)} decision makers."
        )

    companies_df = companies_df.sort_values(by=id_column)
    companies_df = _filter_decision_makers_duplicates(companies_df)
    if streamlit_user_logger:
        streamlit_user_logger.log_success(
            f"Filtering duplicate decision makers. After filtering: {_count_decision_makers(companies_df)} decision makers."
        )
    return companies_df


def enrich_companies_dicts_with_decision_makers(
    companies_dicts: list[dict], db_manager: DbManagerMongo | None = None, streamlit_user_logger=None
) -> list[dict]:
    """
    Add decision makers to a companies list of dicts.

    :param companies_dicts: List of dicts containing companies data.
        Each company should contains a key `_id` or `registered_number`.
    :param streamlit_user_logger: The streamlit user logger to use for logging. No typing here to avoid including streamlit in the dependencies.
    :return: the list of companies dicts with the decision makers added under the `decision_makers` key.
    """
    if db_manager is None:
        db_manager = DbManagerMongo()
    db_manager._logger.info("Adding decision makers to companies dicts...")
    if streamlit_user_logger:
        streamlit_user_logger.log_progress("Looking for decision makers...")
    dm_count = 0
    for i, company_dict in enumerate(companies_dicts):
        decision_makers = db_manager.add_decision_makers_to_company(company_dict["_id"])
        companies_dicts[i]["decision_makers"] = []

        if not decision_makers:
            continue

        for dm in decision_makers:
            dm_count += 1
            companies_dicts[i]["decision_makers"].append(
                {
                    "firstname": dm.firstname,
                    "lastname": dm.lastname,
                    "email": dm.email,
                    "language": dm.language,
                    "department": dm.department,
                    "responsibility_level_formatted": dm.responsibility_level_formatted,
                    "responsibility_level_code": dm.responsibility_level_code,
                    "function_string": dm.function_string or dm.raw_function_string,
                    "linkedin_url": dm.linkedin_url,
                }
            )
    if streamlit_user_logger:
        streamlit_user_logger.log_success(f"Found {dm_count} decision makers!")
    return companies_dicts


if __name__ == "__main__":
    os.environ["ENV"] = "prod"
    db_manager = DbManagerMongo(create_index_if_not_done=True)
