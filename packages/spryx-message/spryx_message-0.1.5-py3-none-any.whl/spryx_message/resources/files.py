from spryx_http import SpryxAsyncClient


class Files:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def presign_upload(
        self,
        organization_id: str,
        file_name: str,
        content_type: str,
    ) -> dict:
        """Get a pre-signed URL for file upload."""
        payload = {
            "file_name": file_name,
            "content_type": content_type,
        }

        return await self._client.post(
            "/v1/files/presign/upload",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def add_file(
        self,
        organization_id: str,
        object_key: str,
    ) -> dict:
        """Add a file using the object key from a successful upload."""
        payload = {
            "object_key": object_key,
        }

        return await self._client.post(
            "/v1/files", 
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def retrieve_file(
        self,
        organization_id: str,
        file_id: str,
    ) -> dict:
        """Retrieve a file by ID."""
        return await self._client.get(
            f"/v1/files/{file_id}",
            headers={"x-organization-id": organization_id},
        ) 