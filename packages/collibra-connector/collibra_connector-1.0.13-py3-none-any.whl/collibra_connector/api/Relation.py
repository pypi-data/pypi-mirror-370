import uuid
from .Base import BaseAPI


class Relation(BaseAPI):
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/relations"

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        type_id: str = None,
        starting_date: int = None,
        ending_date: int = None,
        type_public_id: str = None
    ):
        """
        Adds a new relation.
        :param source_id: The ID of the source of the relation (required UUID).
        :param target_id: The ID of the target of the relation (required UUID).
        :param type_id: The ID of the type of the relation (optional UUID).
        :param starting_date: The starting date of the relation (deprecated, int64).
        :param ending_date: The ending date of the relation (deprecated, int64).
        :param type_public_id: The public ID of the type of the relation (optional).
        :return: Details of the created relation.
        """
        # Validate required parameters
        if not source_id:
            raise ValueError("source_id is required")
        if not isinstance(source_id, str):
            raise ValueError("source_id must be a string")
        try:
            uuid.UUID(source_id)
        except ValueError as exc:
            raise ValueError("source_id must be a valid UUID") from exc

        if not target_id:
            raise ValueError("target_id is required")
        if not isinstance(target_id, str):
            raise ValueError("target_id must be a string")
        try:
            uuid.UUID(target_id)
        except ValueError as exc:
            raise ValueError("target_id must be a valid UUID") from exc

        # Validate type_id if provided
        if type_id is not None:
            if not isinstance(type_id, str):
                raise ValueError("type_id must be a string")
            try:
                uuid.UUID(type_id)
            except ValueError as exc:
                raise ValueError("type_id must be a valid UUID") from exc

        # Validate starting_date if provided
        if starting_date is not None:
            if not isinstance(starting_date, int):
                raise ValueError("starting_date must be an integer")
            if starting_date < 0:
                raise ValueError("starting_date must be a positive integer")

        # Validate ending_date if provided
        if ending_date is not None:
            if not isinstance(ending_date, int):
                raise ValueError("ending_date must be an integer")
            if ending_date < 0:
                raise ValueError("ending_date must be a positive integer")

        # Validate type_public_id if provided
        if type_public_id is not None and not isinstance(type_public_id, str):
            raise ValueError("type_public_id must be a string")

        # Build request data - only include provided values
        data = {
            "sourceId": source_id,
            "targetId": target_id
        }

        if type_id is not None:
            data["typeId"] = type_id
        if starting_date is not None:
            data["startingDate"] = starting_date
        if ending_date is not None:
            data["endingDate"] = ending_date
        if type_public_id is not None:
            data["typePublicId"] = type_public_id

        response = self._post(url=self.__base_api, data=data)
        return self._handle_response(response)

    def get_relation(self, relation_id: str):
        """
        Returns a relation identified by given id.
        :param relation_id: The ID of the relation (required UUID).
        :return: Relation details.
        """
        if not relation_id:
            raise ValueError("relation_id is required")
        if not isinstance(relation_id, str):
            raise ValueError("relation_id must be a string")

        try:
            uuid.UUID(relation_id)
        except ValueError as exc:
            raise ValueError("relation_id must be a valid UUID") from exc

        response = self._get(url=f"{self.__base_api}/{relation_id}")
        return self._handle_response(response)

    def remove_relation(self, relation_id: str):
        """
        Removes a relation identified by given id.
        :param relation_id: The ID of the relation to remove (required UUID).
        :return: Response from the removal operation.
        """
        if not relation_id:
            raise ValueError("relation_id is required")
        if not isinstance(relation_id, str):
            raise ValueError("relation_id must be a string")

        try:
            uuid.UUID(relation_id)
        except ValueError as exc:
            raise ValueError("relation_id must be a valid UUID") from exc

        response = self._delete(url=f"{self.__base_api}/{relation_id}")
        return self._handle_response(response)

    def change_relation(
        self,
        relation_id: str,
        source_id: str = None,
        target_id: str = None,
        starting_date: int = None,
        ending_date: int = None
    ):
        """
        Changes the relation with the information that is present in the request.
        Only properties that are specified in this request and have non-null values are updated.
        :param relation_id: The ID of the relation to be changed (required UUID).
        :param source_id: The ID of the new source for the relation (optional UUID).
        :param target_id: The ID of the new target for the relation (optional UUID).
        :param starting_date: The new starting date for the relation (deprecated, int64).
        :param ending_date: The new ending date for the relation (deprecated, int64).
        :return: Details of the updated relation.
        """
        # Validate required parameters
        if not relation_id:
            raise ValueError("relation_id is required")
        if not isinstance(relation_id, str):
            raise ValueError("relation_id must be a string")

        try:
            uuid.UUID(relation_id)
        except ValueError as exc:
            raise ValueError("relation_id must be a valid UUID") from exc

        # Validate source_id if provided
        if source_id is not None:
            if not isinstance(source_id, str):
                raise ValueError("source_id must be a string")
            try:
                uuid.UUID(source_id)
            except ValueError as exc:
                raise ValueError("source_id must be a valid UUID") from exc

        # Validate target_id if provided
        if target_id is not None:
            if not isinstance(target_id, str):
                raise ValueError("target_id must be a string")
            try:
                uuid.UUID(target_id)
            except ValueError as exc:
                raise ValueError("target_id must be a valid UUID") from exc

        # Validate starting_date if provided
        if starting_date is not None:
            if not isinstance(starting_date, int):
                raise ValueError("starting_date must be an integer")
            if starting_date < 0:
                raise ValueError("starting_date must be a positive integer")

        # Validate ending_date if provided
        if ending_date is not None:
            if not isinstance(ending_date, int):
                raise ValueError("ending_date must be an integer")
            if ending_date < 0:
                raise ValueError("ending_date must be a positive integer")

        # Build request body - only include provided values
        # Include the relation_id in the body as required by the API
        data = {"id": relation_id}

        if source_id is not None:
            data["sourceId"] = source_id
        if target_id is not None:
            data["targetId"] = target_id
        if starting_date is not None:
            data["startingDate"] = starting_date
        if ending_date is not None:
            data["endingDate"] = ending_date

        response = self._patch(url=f"{self.__base_api}/{relation_id}", data=data)
        return self._handle_response(response)
