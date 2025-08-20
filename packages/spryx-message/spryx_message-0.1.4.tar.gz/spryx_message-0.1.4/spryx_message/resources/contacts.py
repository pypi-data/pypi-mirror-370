from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class Contacts:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def list_contacts(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
    ) -> dict:
        """List all contacts."""
        return await self._client.get(
            f"{self._base_url}/v1/contacts",
            params={"page": page, "limit": limit, "order": order},
            headers={"x-organization-id": organization_id},
        )

    async def create_contact(
        self,
        organization_id: str,
        name: str,
        image_url: str = NOT_GIVEN,
        phone: list = None,
        email: list = None,
        channels: list = None,
        metadata: dict = None,
    ) -> dict:
        """Create a new contact."""
        payload = {
            "name": name,
        }

        if is_given(image_url):
            payload["image_url"] = image_url

        if phone:
            payload["phone"] = phone

        if email:
            payload["email"] = email

        if channels:
            payload["channels"] = channels
        else:
            payload["channels"] = []

        if metadata:
            payload["metadata"] = metadata
        else:
            payload["metadata"] = {}

        return await self._client.post(
            f"{self._base_url}/v1/contacts",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def get_contact(
        self,
        organization_id: str,
        contact_id: str,
    ) -> dict:
        """Retrieve a specific contact by ID."""
        return await self._client.get(
            f"{self._base_url}/v1/contacts/{contact_id}",
            headers={"x-organization-id": organization_id},
        )

    async def update_contact(
        self,
        organization_id: str,
        contact_id: str,
        name: str,
        image_url: str = NOT_GIVEN,
        phone: list = None,
        email: list = None,
        channels: list = None,
        metadata: dict = None,
    ) -> dict:
        """Update an existing contact."""
        payload = {
            "name": name,
        }

        if is_given(image_url):
            payload["image_url"] = image_url

        if phone:
            payload["phone"] = phone

        if email:
            payload["email"] = email

        if channels:
            payload["channels"] = channels
        else:
            payload["channels"] = []

        if metadata:
            payload["metadata"] = metadata
        else:
            payload["metadata"] = {}

        return await self._client.put(
            f"{self._base_url}/v1/contacts/{contact_id}",
            json=payload,
            headers={"x-organization-id": organization_id},
        ) 