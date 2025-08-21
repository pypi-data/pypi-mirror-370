import uuid
from .Base import BaseAPI


class Asset(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/assets"

    def _get(self, url: str = None, params: dict = None, headers: dict = None):
        """
        Makes a GET request to the asset API.
        :param url: The URL to send the GET request to.
        :param params: Optional parameters to include in the GET request.
        :param headers: Optional headers to include in the GET request.
        :return: The response from the GET request.
        """
        return super()._get(self.__base_api if not url else url, params, headers)

    def get_asset(self, asset_id):
        """
        Retrieves an asset by its ID.
        :param asset_id: The ID of the asset to retrieve.
        :return: Asset details.
        """
        response = self._get(url=f"{self.__base_api}/{asset_id}")
        return self._handle_response(response)

    def add_asset(
        self,
        name: str,
        domain_id: str,
        display_name: str = None,
        type_id: str = None,
        _id: str = None,
        status_id: str = None,
        excluded_from_auto_hyperlink: bool = False,
        type_public_id: str = None,
    ):
        """
        Adds a new asset.
        :param name: The name of the asset.
        :param domain_id: The ID of the domain to which the asset belongs.
        :param display_name: Optional display name for the asset.
        :param type_id: Optional type ID for the asset.
        :param id: Optional ID for the asset.
        :param status_id: Optional status ID for the asset.
        :param excluded_from_auto_hyperlink: Whether the asset is excluded from auto hyperlinking.
        :param type_public_id: Optional public ID for the asset type.
        :return: Details of the created asset.
        """
        # Parameter type validation
        if not name or not domain_id:
            raise ValueError("Name and domain_id are required parameters.")
        if not isinstance(excluded_from_auto_hyperlink, bool):
            raise ValueError("excluded_from_auto_hyperlink must be a boolean value.")
        if type_id and not isinstance(type_id, str):
            raise ValueError("type_id must be a string if provided.")
        if _id and not isinstance(_id, str):
            raise ValueError("_id must be a string if provided.")
        if status_id and not isinstance(status_id, str):
            raise ValueError("status_id must be a string if provided.")
        if type_public_id and not isinstance(type_public_id, str):
            raise ValueError("type_public_id must be a string if provided.")

        # Check Ids are UUIDS
        if _id and self._uuid_validation(_id) is False:
            raise ValueError("id must be a valid UUID.")
        if domain_id and self._uuid_validation(domain_id) is False:
            raise ValueError("domain_id must be a valid UUID.")
        if type_id and self._uuid_validation(type_id) is False:
            raise ValueError("type_id must be a valid UUID.")
        if status_id and self._uuid_validation(status_id) is False:
            raise ValueError("status_id must be a valid UUID.")

        data = {
            "name": name,
            "domainId": domain_id,
            "displayName": display_name,
            "typeId": type_id,
            "id": id,
            "statusId": status_id,
            "excludedFromAutoHyperlink": excluded_from_auto_hyperlink,
            "typePublicId": type_public_id
        }
        response = self._post(url=self.__base_api, data=data)
        return self._handle_response(response)

    def change_asset(
        self,
        asset_id: str,
        name: str = None,
        display_name: str = None,
        type_id: str = None,
        status_id: str = None,
        domain_id: str = None,
        excluded_from_auto_hyperlinking: bool = None,
        type_public_id: str = None
    ):
        """
        Update asset properties.
        :param asset_id: The ID of the asset to update.
        :param name: Optional new name for the asset.
        :param display_name: Optional new display name.
        :param type_id: Optional new type ID.
        :param status_id: Optional new status ID.
        :param domain_id: Optional new domain ID.
        :param excluded_from_auto_hyperlinking: Optional auto-hyperlinking setting.
        :param type_public_id: Optional new type public ID.
        :return: Updated asset details.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        # Validate UUID fields if provided
        uuid_fields = [
            ("type_id", type_id),
            ("status_id", status_id),
            ("domain_id", domain_id)
        ]

        for field_name, field_value in uuid_fields:
            if field_value:
                if not isinstance(field_value, str):
                    raise ValueError(f"{field_name} must be a string")
                try:
                    uuid.UUID(field_value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be a valid UUID") from exc

        data = {
            "id": asset_id,
            "name": name,
            "displayName": display_name,
            "typeId": type_id,
            "statusId": status_id,
            "domainId": domain_id,
            "excludedFromAutoHyperlinking": excluded_from_auto_hyperlinking,
            "typePublicId": type_public_id,
        }

        response = self._patch(url=f"{self.__base_api}/{asset_id}", data=data)
        return self._handle_response(response)

    def update_asset_attribute(self, asset_id: str, attribute_id: str, value):
        """
        Update an asset attribute.
        :param asset_id: The ID of the asset.
        :param attribute_id: The ID of the attribute type.
        :param value: The new value for the attribute.
        :return: The response from updating the attribute.
        """
        if not all([asset_id, attribute_id]):
            raise ValueError("asset_id and attribute_id are required")

        for param_name, param_value in [("asset_id", asset_id), ("attribute_id", attribute_id)]:
            if not isinstance(param_value, str):
                raise ValueError(f"{param_name} must be a string")
            try:
                uuid.UUID(param_value)
            except ValueError as exc:
                raise ValueError(f"{param_name} must be a valid UUID") from exc

        data = {
            "values": [value],
            "typeId": attribute_id
        }

        response = self._put(url=f"{self.__base_api}/{asset_id}/attributes", data=data)
        return self._handle_response(response)

    def set_asset_attributes(self, asset_id: str, type_id: str = None, type_public_id: str = None, values: list = None):
        """
        Set asset attributes. Replaces all attributes of the asset with the given ID
        (of given attribute type) with the attributes from the request.
        :param asset_id: The ID of the asset.
        :param type_id: The ID of the attribute type for the new attribute.
        :param type_public_id: The public ID of the attribute type for the new attribute.
        :param values: The values for the new attribute (list of objects).
        :return: The response from setting the attributes.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        if not values:
            raise ValueError("values is required")
        if not isinstance(values, list):
            raise ValueError("values must be a list")

        # Validate that either type_id or type_public_id is provided
        if not type_id and not type_public_id:
            raise ValueError("Either type_id or type_public_id must be provided")

        # Validate type_id if provided
        if type_id:
            if not isinstance(type_id, str):
                raise ValueError("type_id must be a string")
            try:
                uuid.UUID(type_id)
            except ValueError as exc:
                raise ValueError("type_id must be a valid UUID") from exc

        # Validate type_public_id if provided
        if type_public_id and not isinstance(type_public_id, str):
            raise ValueError("type_public_id must be a string")

        data = {
            "values": values
        }

        # Add type_id or type_public_id to the data
        if type_id:
            data["typeId"] = type_id
        if type_public_id:
            data["typePublicId"] = type_public_id

        response = self._put(url=f"{self.__base_api}/{asset_id}/attributes", data=data)
        return self._handle_response(response)

    def remove_asset(self, asset_id: str):
        """
        Remove an asset identified by given ID.
        :param asset_id: The ID of the asset to remove.
        :return: The response from removing the asset.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        response = self._delete(url=f"{self.__base_api}/{asset_id}")
        return self._handle_response(response)

    def set_asset_relations(self, asset_id: str, related_asset_ids: list, relation_direction: str,
                            type_id: str = None, type_public_id: str = None):
        """
        Set relations for the asset with the given ID. All relations described by this request
        will replace the existing ones (identified with asset as one end, relation type and direction).
        :param asset_id: The ID of the asset.
        :param related_asset_ids: The IDs of the related assets (list of UUIDs).
        :param relation_direction: The relation direction ('TO_TARGET' or 'TO_SOURCE').
        :param type_id: The ID of the relation type for the relations to be set.
        :param type_public_id: The public ID of the relation type for the relations to be set.
        :return: The response from setting the relations.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        if not related_asset_ids:
            raise ValueError("related_asset_ids is required")
        if not isinstance(related_asset_ids, list):
            raise ValueError("related_asset_ids must be a list")

        # Validate all related asset IDs are valid UUIDs
        for i, related_id in enumerate(related_asset_ids):
            if not isinstance(related_id, str):
                raise ValueError(f"related_asset_ids[{i}] must be a string")
            try:
                uuid.UUID(related_id)
            except ValueError as exc:
                raise ValueError(f"related_asset_ids[{i}] must be a valid UUID") from exc

        if not relation_direction:
            raise ValueError("relation_direction is required")
        if relation_direction not in ["TO_TARGET", "TO_SOURCE"]:
            raise ValueError("relation_direction must be either 'TO_TARGET' or 'TO_SOURCE'")

        # Validate that either type_id or type_public_id is provided
        if not type_id and not type_public_id:
            raise ValueError("Either type_id or type_public_id must be provided")

        # Validate type_id if provided
        if type_id:
            if not isinstance(type_id, str):
                raise ValueError("type_id must be a string")
            try:
                uuid.UUID(type_id)
            except ValueError as exc:
                raise ValueError("type_id must be a valid UUID") from exc

        # Validate type_public_id if provided
        if type_public_id and not isinstance(type_public_id, str):
            raise ValueError("type_public_id must be a string")

        data = {
            "relatedAssetIds": related_asset_ids,
            "relationDirection": relation_direction
        }

        # Add type_id or type_public_id to the data
        if type_id:
            data["typeId"] = type_id
        if type_public_id:
            data["typePublicId"] = type_public_id

        response = self._put(url=f"{self.__base_api}/{asset_id}/relations", data=data)
        return self._handle_response(response)

    def set_asset_responsibilities(self, asset_id: str, role_id: str, owner_ids: list):
        """
        Set responsibilities for the asset with the given ID.
        :param asset_id: The ID of the asset.
        :param role_id: The ID of the role for the responsibilities to be set.
        :param owner_ids: The IDs of the owners (list of UUIDs). An owner is either user or group.
        :return: The response from setting the responsibilities.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        if not role_id:
            raise ValueError("role_id is required")
        if not isinstance(role_id, str):
            raise ValueError("role_id must be a string")

        try:
            uuid.UUID(role_id)
        except ValueError as exc:
            raise ValueError("role_id must be a valid UUID") from exc

        if not owner_ids:
            raise ValueError("owner_ids is required")
        if not isinstance(owner_ids, list):
            raise ValueError("owner_ids must be a list")

        # Validate all owner IDs are valid UUIDs
        for i, owner_id in enumerate(owner_ids):
            if not isinstance(owner_id, str):
                raise ValueError(f"owner_ids[{i}] must be a string")
            try:
                uuid.UUID(owner_id)
            except ValueError as exc:
                raise ValueError(f"owner_ids[{i}] must be a valid UUID") from exc

        data = {
            "roleId": role_id,
            "ownerIds": owner_ids
        }

        response = self._put(url=f"{self.__base_api}/{asset_id}/responsibilities", data=data)
        return self._handle_response(response)

    def find_assets(
        self,
        community_id: str = None,
        asset_type_ids: list = None,
        domain_id: str = None,
        limit: int = 1000
    ):
        """
        Find assets with optional filters.
        :param community_id: Optional community ID to filter by.
        :param asset_type_ids: Optional list of asset type IDs to filter by.
        :param domain_id: Optional domain ID to filter by.
        :param limit: Maximum number of results per page.
        :return: List of assets matching the criteria.
        """
        params = {"limit": limit}

        if community_id:
            if not isinstance(community_id, str):
                raise ValueError("community_id must be a string")
            try:
                uuid.UUID(community_id)
            except ValueError as exc:
                raise ValueError("community_id must be a valid UUID") from exc
            params["communityId"] = community_id

        if asset_type_ids:
            if not isinstance(asset_type_ids, list):
                raise ValueError("asset_type_ids must be a list")
            for type_id in asset_type_ids:
                if not isinstance(type_id, str):
                    raise ValueError("All asset_type_ids must be strings")
                try:
                    uuid.UUID(type_id)
                except ValueError as exc:
                    raise ValueError("All asset_type_ids must be valid UUIDs") from exc
            params["typeIds"] = asset_type_ids

        if domain_id:
            if not isinstance(domain_id, str):
                raise ValueError("domain_id must be a string")
            try:
                uuid.UUID(domain_id)
            except ValueError as exc:
                raise ValueError("domain_id must be a valid UUID") from exc
            params["domainId"] = domain_id

        response = self._get(params=params)
        return self._handle_response(response)

    def get_asset_activities(self, asset_id: str, limit: int = 50):
        """
        Get activities for a specific asset.
        :param asset_id: The ID of the asset.
        :param limit: Maximum number of activities to retrieve.
        :return: List of activities for the asset.
        """
        if not asset_id:
            raise ValueError("asset_id is required")
        if not isinstance(asset_id, str):
            raise ValueError("asset_id must be a string")

        try:
            uuid.UUID(asset_id)
        except ValueError as exc:
            raise ValueError("asset_id must be a valid UUID") from exc

        params = {
            "contextId": asset_id,
            "resourceTypes": ["Asset"],
            "limit": limit
        }

        response = self._get(url=f"{self.__base_api}/activities", params=params)
        result = self._handle_response(response)
        return result.get("results", [])
