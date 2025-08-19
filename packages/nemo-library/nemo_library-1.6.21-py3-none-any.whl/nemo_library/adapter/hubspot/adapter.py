import json
import logging
from pathlib import Path

import requests
from nemo_library.adapter.hubspot.model.activityassociation import (
    ActivityAssociationEntry,
)
from nemo_library.adapter.hubspot.model.activitybase import ActivityBase
from nemo_library.adapter.hubspot.model.companyassociation import (
    CompanyAssociationEntry,
)
from nemo_library.adapter.hubspot.model.companydetail import CompanyDetailEntry
from nemo_library.adapter.hubspot.model.deal_raw import DealRaw
from nemo_library.adapter.hubspot.model.deal_transform import DealTransformed
from nemo_library.adapter.hubspot.model.dealhistory import DealHistoryEntry
from nemo_library.adapter.hubspot.util import (
    ACTIVITY_TYPE_DETAILS,
    ACTIVITY_TYPES,
    json_serial,
    parse_datetime,
)
from nemo_library.core import NemoLibrary
from hubspot import HubSpot
import time
from hubspot.crm.associations.models.batch_input_public_object_id import (
    BatchInputPublicObjectId,
)

class HubspotAdapter:
    """
    Adapter for Hubspot API.
    """

    def __init__(self) -> None:

        nl = NemoLibrary()
        self.config = nl.config

        self.hubspot = self._getHubSpotAPIToken()

        super().__init__()

    def _getHubSpotAPIToken(self) -> HubSpot:
        """
        Initializes and returns a HubSpot API client using the API token from the provided configuration.

        Args:
            config (ConfigHandler): An instance of ConfigHandler that contains configuration details,
                                    including the HubSpot API token.

        Returns:
            HubSpot: An instance of the HubSpot API client initialized with the API token.
        """
        hs = HubSpot(access_token=self.config.get_hubspot_api_token())
        return hs

    def _getDealIDs(self) -> list[str]:
        """
        Retrieves all deal IDs from HubSpot.

        Returns:
            list[str]: A list of deal IDs.
        """
        # Load deals from previously saved JSON file
        etl_dir = self.config.get_etl_directory()
        file_path = Path(etl_dir) / "hubspot" / "deals.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Deals file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            deal_data = json.load(f)

        deals: list[DealRaw] = [DealRaw.from_dict(deal) for deal in deal_data]
        deal_ids = [deal.id for deal in deals]
        return deal_ids

    def _getHeaders(self) -> dict[str, str]:
        """
        Returns the headers required for making API requests to HubSpot.

        Returns:
            dict[str, str]: A dictionary containing the authorization header with the HubSpot API token.
        """
        return {
            "Authorization": f"Bearer {self.config.get_hubspot_api_token()}",
            "Content-Type": "application/json",
        }

    def _exportObjects(
        self,
        object_type: str,
        objects: list,
    ) -> None:

        etl_dir = self.config.get_etl_directory()
        if not etl_dir:
            raise ValueError("ETL directory is not configured.")

        output_path = Path(etl_dir) / "hubspot" / f"{object_type}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                [entry.to_dict() for entry in objects],
                f,
                indent=4,
                ensure_ascii=False,
                default=json_serial,
            )
        logging.info(f"Saved {len(objects)} {object_type} to {output_path}")

    def extract_deals(self) -> None:
        """
        Extracts deals from HubSpot using the API token.

        Returns:
            list: A list of deals extracted from HubSpot.
        """
        logging.info("Extracting deals from HubSpot...")

        # load all deals
        deal_properties = [
            "id",
            "dealname",
            "hubspot_owner_id",
            "revenue_stream",
            "verkauf_uber",
            "belegnummer",
            "budget_bekannt",
            "entscheider_bekannt",
            "entscheider_freigabe",
            "entscheidungsdauer_bekannt",
            "entscheidungsprozess_bekannt",
            "closedate",
            "amount",
            "dealstage",
        ]

        # Retrieve all deals from HubSpot using specified properties
        response = self.hubspot.crm.deals.get_all(properties=deal_properties)

        # Convert raw HubSpot data to list of Deal instances using the updated from_dict() method
        deals: list[DealRaw] = [DealRaw.from_dict(deal.to_dict()) for deal in response]

        # export objects to JSON file
        self._exportObjects(object_type="deals", objects=deals)

    def extract_deal_history(self) -> None:
        """
        Extracts and stores the property change history for all HubSpot deals.

        This method retrieves historical changes for dealstage, amount, and closedate
        properties and stores the results as DealHistoryEntry instances in a JSON file.
        """
        logging.info("Extracting deal history from HubSpot...")
        deal_ids = self._getDealIDs()
        batch_size = 50
        base_url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"
        headers = self._getHeaders()

        all_history: list[DealHistoryEntry] = []

        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i : i + batch_size]
            batch_read_input = {
                "inputs": [{"id": deal_id} for deal_id in batch_ids],
                "propertiesWithHistory": ["dealstage", "amount", "closedate"],
            }

            response = requests.post(base_url, json=batch_read_input, headers=headers)

            if response.status_code != 200:
                logging.error(
                    f"Failed to fetch history batch {i // batch_size + 1}: {response.text}"
                )
                continue

            batch_data = response.json()

            for deal in batch_data.get("results", []):
                deal_id = deal["id"]
                for prop, history in deal.get("propertiesWithHistory", {}).items():
                    sorted_history = sorted(history, key=lambda h: h["timestamp"])
                    previous_value = None
                    for h in sorted_history:
                        entry = DealHistoryEntry(
                            deal_id=deal_id,
                            update_type=f"{prop} changed",
                            property_name=prop,
                            old_value=previous_value,
                            new_value=h.get("value"),
                            timestamp=parse_datetime(h["timestamp"]),
                            user_id=h.get("updatedByUserId"),
                            source_type=h.get("sourceType"),
                        )
                        all_history.append(entry)
                        previous_value = h.get(
                            "value"
                        )  # Keep original ID for next diff

            logging.info(
                f"Processed deal history for {min(i + batch_size, len(deal_ids)):,} of {len(deal_ids):,} deals"
            )
            time.sleep(0.2)

        # export objects to JSON file
        self._exportObjects(object_type="deal_history", objects=all_history)

    def extract_company_associations(self) -> None:
        """
        Extracts company associations for deals from HubSpot and saves them to a JSON file.

        This method retrieves all deals, extracts their associated companies, and saves the
        associations in a structured format.
        """
        logging.info("Extracting company associations for deals from HubSpot...")
        deal_ids = self._getDealIDs()

        batch_size = 1000
        all_associations: list[CompanyAssociationEntry] = []

        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i : i + batch_size]
            batch_input = BatchInputPublicObjectId(inputs=batch_ids)

            response = self.hubspot.crm.associations.batch_api.read(
                from_object_type="deals",
                to_object_type="companies",
                batch_input_public_object_id=batch_input,
            )

            for result in response.results:
                deal_id = result._from.id
                for to in result.to:
                    all_associations.append(
                        CompanyAssociationEntry(
                            deal_id=deal_id,
                            company_id=to.id,
                        )
                    )

            logging.info(f"Company associations batch {i // batch_size + 1} loaded...")
            time.sleep(0.2)

        # Save associations to JSON file
        self._exportObjects(
            object_type="company_associations", objects=all_associations
        )

    def extract_company_details(self) -> None:
        """
        Extracts company details associated with deals from HubSpot and saves them to a JSON file.

        This method retrieves all companies associated with deals and saves their details in a structured format.
        """
        logging.info("Extracting company details from HubSpot...")

        # Load company associations from previously saved JSON file
        etl_dir = self.config.get_etl_directory()
        file_path = Path(etl_dir) / "hubspot" / "company_associations.json"

        if not file_path.exists():
            logging.error(f"Company associations file not found: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            company_association_data = json.load(f)

        associations: list[CompanyAssociationEntry] = [
            CompanyAssociationEntry(**entry) for entry in company_association_data
        ]
        company_ids = [entry.company_id for entry in associations]

        batch_size = 100
        all_companies: list[CompanyDetailEntry] = []

        properties_to_fetch = [
            "name",
            "domain",
            "industry",
            "numberofemployees",
            "annualrevenue",
        ]

        for i in range(0, len(company_ids), batch_size):
            batch_ids = company_ids[i : i + batch_size]

            # Using the search API to fetch company details with specific properties
            filter_group = {
                "filters": [
                    {
                        "propertyName": "hs_object_id",
                        "operator": "IN",
                        "values": batch_ids,
                    }
                ]
            }
            search_request = {
                "filterGroups": [filter_group],
                "properties": properties_to_fetch,
                "limit": batch_size,
            }

            response = self.hubspot.crm.companies.search_api.do_search(search_request)
            for result in response.results:
                all_companies.append(
                    CompanyDetailEntry(
                        company_id=result.id,
                        name=result.properties.get("name"),
                        domain=result.properties.get("domain"),
                        industry=result.properties.get("industry"),
                        numberofemployees=result.properties.get("numberofemployees"),
                        annualrevenue=result.properties.get("annualrevenue"),
                    )
                )
            logging.info(f"Company details batch {i // batch_size + 1} loaded...")
            time.sleep(0.2)

        # Save companies to JSON file
        self._exportObjects(object_type="companies", objects=all_companies)

    def extract_activity_association_type(self, activity_type: str) -> None:
        """
        Extracts HubSpot activity associations for a given activity type and saves the results to a JSON file.

        Args:
            activity_type (str): The HubSpot object type to associate (e.g., 'calls', 'emails', 'meetings').
        """
        logging.info(
            f"Extracting activity associations type '{activity_type}' from HubSpot..."
        )

        deal_ids = self._getDealIDs()

        batch_size = 1000
        all_associations: list[ActivityAssociationEntry] = []

        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i : i + batch_size]
            batch_input = BatchInputPublicObjectId(inputs=batch_ids)

            response = self.hubspot.crm.associations.batch_api.read(
                from_object_type="deals",
                to_object_type=activity_type,
                batch_input_public_object_id=batch_input,
            )

            for result in response.results:
                deal_id = result._from.id
                for to in result.to:
                    all_associations.append(
                        ActivityAssociationEntry(
                            deal_id=deal_id,
                            activity_id=to.id,
                            activity_type=activity_type,
                        )
                    )

            logging.info(f"{activity_type} batch {i // batch_size + 1} loaded...")
            time.sleep(0.2)

        # Save associations to JSON file
        self._exportObjects(
            object_type=f"{activity_type}_associations", objects=all_associations
        )

    def fetch_activity_details_batch_via_rest(
        self,
        activity_type: str,
        activity_ids: list[str],
        properties: list[str],
    ) -> list[dict]:

        headers = self._getHeaders()
        url = f"https://api.hubapi.com/crm/v3/objects/{activity_type}/batch/read"

        results = []
        total_items = len(activity_ids)

        # Split IDs into batches of up to 100
        for i in range(0, total_items, 100):
            batch_ids = activity_ids[i : i + 100]

            # Prepare the data for the batch API request
            data = {
                "properties": properties,
                "inputs": [{"id": obj_id} for obj_id in batch_ids],
            }

            # Execute the POST request to the Batch API
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                batch_results = response.json().get("results", [])
                for idx, result in enumerate(batch_results):
                    activity_details = result.get("properties", {})
                    results.append(activity_details)

                processed_count = min(i + 100, total_items)
                logging.info(
                    f"Processed {processed_count:,} of {total_items:,} items for {activity_type}."
                )
                # Pause to avoid exceeding rate limits
                time.sleep(0.2)
            else:
                raise requests.HTTPError(
                    f"Error fetching batch for {activity_type}: {response.status_code}, {response.text}"
                )

        return results

    def extract_activities_type(self, activity_type: str) -> None:
        logging.info(f"Extracting activity type '{activity_type}' from HubSpot...")

        # Dynamically get the dataclass for the given activity_type
        activity_class = ACTIVITY_TYPES.get(activity_type)
        if not activity_class:
            raise ValueError(
                f"Activity type '{activity_type}' is not supported."
            )

        # Load deals from previously saved JSON file
        etl_dir = self.config.get_etl_directory()
        file_path = Path(etl_dir) / "hubspot" / f"{activity_type}_associations.json"

        if not file_path.exists():
            logging.error(f"file not found: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            activity_association_data = json.load(f)

        activities: list[ActivityAssociationEntry] = [
            ActivityAssociationEntry(**entry) for entry in activity_association_data
        ]
        activity_ids = [entry.activity_id for entry in activities]
        properties_to_fetch = ACTIVITY_TYPE_DETAILS.get(activity_type, [])

        if properties_to_fetch and activity_ids:
            # Fetch the details via REST API
            details_raw = self.fetch_activity_details_batch_via_rest(
                activity_type=activity_type,
                activity_ids=activity_ids,
                properties=properties_to_fetch,
            )

            # Parse the raw detail data into dataclass instances
            details: list[ActivityBase] = [
                activity_class(**item) for item in details_raw
            ]

            # Export the structured objects
            self._exportObjects(
                object_type=f"{activity_type}_details", objects=details
            )

    def transform_deals(self) -> None:
        """
        Transforms the deals data by mapping deal stages to their corresponding labels.
        """
        logging.info("Transforming deals data...")

        # Load deals from previously saved JSON file
        etl_dir = self.config.get_etl_directory()
        file_path = Path(etl_dir) / "hubspot" / "deals.json"

        if not file_path.exists():
            logging.error(f"Deals file not found: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            deal_data = json.load(f)

        deals_raw: list[DealRaw] = [DealRaw.from_dict(deal) for deal in deal_data]
        
        deals_transformed = [DealTransformed.from_deal_raw(deal) for deal in deals_raw]

        # Export transformed deals to JSON file
        self._exportObjects("deals_transformed", deals_transformed)
