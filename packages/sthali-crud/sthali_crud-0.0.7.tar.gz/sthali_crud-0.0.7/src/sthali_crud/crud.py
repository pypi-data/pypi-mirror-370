"""{...}."""

import typing
import uuid

import fastapi
import pydantic
import pydantic_core

import sthali_db
import sthali_db.clients

ResponseModel = sthali_db.Models.BaseWithId


class CRUDException(fastapi.HTTPException):
    def __init__(
        self,
        detail: str | list[str] | list[pydantic_core.ErrorDetails],
        status_code: int = fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
    ) -> None:
        super().__init__(status_code, detail)


class CRUD:
    def __init__(self, db: sthali_db.DB, models: sthali_db.Models) -> None:
        self.db = db
        self.models = models

    @property
    def response_model(self) -> type[ResponseModel]:
        return self.models.response_model

    def _handle_list(self, result: list[sthali_db.clients.ResourceObj]) -> list[ResponseModel]:
        errors: list[CRUDException] = []
        response_result: list[ResponseModel] = []

        for r in result:
            try:
                _r = self._handle_result(r)
            except CRUDException as exception:
                errors.append(exception)
            else:
                response_result.append(_r)

        try:
            assert not errors
        except AssertionError as exception:
            raise CRUDException([e.detail for e in errors]) from exception
        return response_result

    def _handle_result(self, result: dict[str, typing.Any] | None) -> ResponseModel:
        try:
            assert result, "Not found"
            response_result = self.response_model(**result)
        except AssertionError as exception:
            raise CRUDException(exception.args[0], fastapi.status.HTTP_404_NOT_FOUND) from exception
        except pydantic.ValidationError as exception:
            raise CRUDException(exception.errors()) from exception
        return response_result

    async def create(self, resource: sthali_db.Models.Base) -> ResponseModel:
        """Create a new resource.

        Args:
            resource (sthali_db.Models.Base): The resource object to be created.

        Returns:
            ResponseModel: The response model containing the result of the operation.
        """
        resource_id = uuid.uuid4()
        resource_obj = resource.model_dump()
        result = await self.db.insert_one(resource_id=resource_id, resource_obj=resource_obj)
        return self._handle_result(result)

    async def read(self, resource_id: uuid.UUID) -> ResponseModel:
        """Retrieves a resource from the database based on the given resource ID.

        Args:
            resource_id (uuid.UUID): The ID of the resource to retrieve.

        Returns:
            ResponseModel: The retrieved resource.

        """
        result = await self.db.select_one(resource_id=resource_id)
        return self._handle_result(result)

    async def update(
        self, request: fastapi.Request, resource_id: uuid.UUID, resource: sthali_db.Models.Base
    ) -> ResponseModel:
        """Update a resource in the database.

        Args:
            request (fastapi.Request): The FastAPI request object.
            resource_id (uuid.UUID): The ID of the resource to update.
            resource (sthali_db.Models.Base): The resource object containing the updated data.

        Returns:
            ResponseModel: The response model containing the result of the update operation.
        """
        partial = request.method == "PATCH"
        resource_obj = resource.model_dump(exclude_unset=partial)
        result = await self.db.update_one(resource_id=resource_id, resource_obj=resource_obj, partial=partial)
        return self._handle_result(result)

    async def delete(self, resource_id: uuid.UUID) -> None:
        """Deletes a resource with the given resource_id.

        Args:
            resource_id (uuid.UUID): The ID of the resource to delete.

        Raises:
            CRUDException: If the deletion fails.

        Returns:
            None: Indicates successful deletion.
        """
        result = await self.db.delete_one(resource_id=resource_id)
        try:
            assert result is None, "Result is not none"
        except AssertionError as _exception:
            raise CRUDException(repr(_exception), fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from _exception
        return result

    async def read_many(
        self,
        paginate_parameters: typing.Annotated[
            sthali_db.dependencies.PaginateParameters, fastapi.Depends(sthali_db.dependencies.PaginateParameters),
        ],
    ) -> list[ResponseModel]:
        """Retrieves multiple records from the database based on pagination parameters.

        Args:
            paginate_parameters: Pagination parameters for selecting multiple records. The `paginate` parameter should
                containing the following args:
                - `page` (int): The page number to retrieve.
                - `limit` (int): The maximum number of records to retrieve per page.

        Returns:
            list[ResponseModel]: A list of response models representing the retrieved records.
        """
        result = await self.db.select_many(paginate_parameters)
        return self._handle_list(result)
