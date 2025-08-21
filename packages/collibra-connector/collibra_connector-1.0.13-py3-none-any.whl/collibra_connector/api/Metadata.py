from .Base import BaseAPI


class Metadata(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api

    def get_collibra_metadata(self):
        """
        Retrieve comprehensive metadata from Collibra including asset types,
        relation types, responsibilities, statuses, attributes, communities,
        domains, and domain types.
        :return: Dictionary containing all metadata with names as keys and UUIDs as values.
        """
        metadata = {
            "AssetType": {},
            "Relation": {},
            "Responsibility": {},
            "Status": {},
            "StringAttribute": {},
            "Community": {},
            "Domain": {},
            "DomainType": {},
        }

        try:
            # Get Asset Types
            asset_types_response = self._get(url=f"{self.__base_api}/assetTypes")
            asset_types_data = self._handle_response(asset_types_response)
            for asset_type in asset_types_data.get("results", []):
                metadata["AssetType"][asset_type["name"]] = asset_type["id"]

            # Get Relation Types
            relation_types_response = self._get(url=f"{self.__base_api}/relationTypes")
            relation_types_data = self._handle_response(relation_types_response)
            for relation_type in relation_types_data.get("results", []):
                import re
                source_name = re.sub(" ", "", relation_type["sourceType"]["name"])
                target_name = re.sub(" ", "", relation_type["targetType"]["name"])
                metadata["Relation"][f"{source_name}_{target_name}"] = relation_type["id"]

            # Get Roles/Responsibilities
            roles_response = self._get(url=f"{self.__base_api}/roles")
            roles_data = self._handle_response(roles_response)
            for role in roles_data.get("results", []):
                metadata["Responsibility"][role["name"]] = role["id"]

            # Get Statuses
            statuses_response = self._get(url=f"{self.__base_api}/statuses")
            statuses_data = self._handle_response(statuses_response)
            for status in statuses_data.get("results", []):
                metadata["Status"][status["name"]] = status["id"]

            # Get Attribute Types
            attributes_response = self._get(url=f"{self.__base_api}/attributeTypes")
            attributes_data = self._handle_response(attributes_response)
            for attribute in attributes_data.get("results", []):
                metadata["StringAttribute"][attribute["name"]] = attribute["id"]

            # Get Communities
            communities_response = self._get(url=f"{self.__base_api}/communities")
            communities_data = self._handle_response(communities_response)
            for community in communities_data.get("results", []):
                metadata["Community"][community["name"]] = community["id"]

            # Get Domains (with pagination)
            domains_params = {"limit": 1000, "offset": 0}
            while True:
                domains_response = self._get(url=f"{self.__base_api}/domains", params=domains_params)
                domains_data = self._handle_response(domains_response)
                for domain in domains_data.get("results", []):
                    metadata["Domain"][domain["name"]] = domain["id"]
                if (
                    domains_data.get("offset", 0) + domains_data.get("limit", 0)
                    >= domains_data.get("total", 0)
                ):
                    break
                domains_params["offset"] += domains_params["limit"]

            # Get Domain Types
            domain_types_response = self._get(url=f"{self.__base_api}/domainTypes")
            domain_types_data = self._handle_response(domain_types_response)
            for domain_type in domain_types_data.get("results", []):
                metadata["DomainType"][domain_type["name"]] = domain_type["id"]

            return metadata

        except Exception as e:
            raise Exception(f"Error fetching Collibra metadata: {str(e)}") from e

    def get_asset_types(self):
        """Get all asset types."""
        response = self._get(url=f"{self.__base_api}/assetTypes")
        return self._handle_response(response)

    def get_relation_types(self):
        """Get all relation types."""
        response = self._get(url=f"{self.__base_api}/relationTypes")
        return self._handle_response(response)

    def get_statuses(self):
        """Get all statuses."""
        response = self._get(url=f"{self.__base_api}/statuses")
        return self._handle_response(response)

    def get_attribute_types(self):
        """Get all attribute types."""
        response = self._get(url=f"{self.__base_api}/attributeTypes")
        return self._handle_response(response)

    def get_domain_types(self):
        """Get all domain types."""
        response = self._get(url=f"{self.__base_api}/domainTypes")
        return self._handle_response(response)

    def get_roles(self):
        """Get all roles."""
        response = self._get(url=f"{self.__base_api}/roles")
        return self._handle_response(response)
