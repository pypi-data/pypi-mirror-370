import re
import logging
from .Base import BaseAPI

logger = logging.getLogger(__name__)


class Utils(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api

    def get_uuids(self):
        """
        Retrieves UUIDs of asset types, relation types, responsibilities, statuses, and attributes from Collibra,
        returning a dictionary with names as keys and UUIDs as values. Relation type names are used.

        Returns:
            A dictionary containing dictionaries of named UUIDs for asset types, relation types,
            responsibilities, statuses, and attributes.
        """
        metadata = {
            "AssetType": {},
            "Relation": {},
            "Responsability": {},
            "Status": {},
            "Attribute": {},
            "Community": {},
            "Domain": {},
            "DomainType": {},
        }
        try:
            # Get Asset Type UUIDs
            asset_types_url = f"{self.__base_api}/assetTypes"
            asset_types_response = self._get(url=asset_types_url)
            asset_types_data = self._handle_response(asset_types_response)
            for asset_type in asset_types_data["results"]:
                metadata["AssetType"][asset_type["name"]] = asset_type["id"]

            # Get Relation Type UUIDs
            relation_types_url = f"{self.__base_api}/relationTypes"
            relation_types_response = self._get(url=relation_types_url)
            relation_types_data = self._handle_response(relation_types_response)
            for relation_type in relation_types_data["results"]:
                source_name = re.sub(" ", "", relation_type["sourceType"]["name"])
                target_name = re.sub(" ", "", relation_type["targetType"]["name"])
                metadata["Relation"][f"{source_name}_{target_name}"] = relation_type["id"]

            # Get Roles
            resource_roles_url = f"{self.__base_api}/roles"
            resource_roles_response = self._get(url=resource_roles_url)
            resource_roles_data = self._handle_response(resource_roles_response)
            for resource_role in resource_roles_data["results"]:
                metadata["Responsability"][resource_role["name"]] = resource_role["id"]

            # Get Status UUIDs
            statuses_url = f"{self.__base_api}/statuses"
            statuses_response = self._get(url=statuses_url)
            statuses_data = self._handle_response(statuses_response)
            for status in statuses_data["results"]:
                metadata["Status"][status["name"]] = status["id"]

            # Get Attribute UUIDs
            attributes_url = f"{self.__base_api}/attributeTypes"
            attributes_response = self._get(url=attributes_url)
            attributes_data = self._handle_response(attributes_response)
            for attribute in attributes_data["results"]:
                metadata["Attribute"][attribute["name"]] = attribute["id"]

            # Get Community UUIDs
            communities_url = f"{self.__base_api}/communities"
            communities_response = self._get(url=communities_url)
            communities_data = self._handle_response(communities_response)
            for community in communities_data["results"]:
                metadata["Community"][community["name"]] = community["id"]

            # Get Domain UUIDs
            domains_url = f"{self.__base_api}/domains"
            domains_params = {"limit": 1000, "offset": 0}
            while True:
                domains_response = self._get(url=domains_url, params=domains_params)
                domains_data = self._handle_response(domains_response)
                for domain in domains_data["results"]:
                    metadata["Domain"][domain["name"]] = domain["id"]
                if domains_data.get("offset") + domains_data.get(
                    "limit"
                ) >= domains_data.get("total"):
                    break
                domains_params["offset"] += domains_params["limit"]

            # Get Domain Type UUIDs
            domain_types_url = f"{self.__base_api}/domainTypes"
            domain_types_response = self._get(url=domain_types_url)
            domain_types_data = self._handle_response(domain_types_response)
            for domain_type in domain_types_data["results"]:
                metadata["DomainType"][domain_type["name"]] = domain_type["id"]

            logger.info("Collibra UUIDS fetched successfully")
            return metadata

        except (KeyError, ValueError, AttributeError) as e:
            logger.error("Error fetching Collibra UUIDs: %s", e)
            return None
