from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_message.types.channel import ChannelSource


class Channels:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def list_channels(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
    ) -> dict:
        """List all channels."""
        return await self._client.get(
            "/v1/channels",
            params={"page": page, "limit": limit, "order": order},
            headers={"x-organization-id": organization_id},
        )

    async def create_channel(
        self,
        organization_id: str,
        name: str,
        source: ChannelSource,
        default_owner: dict = NOT_GIVEN,
        data: dict = NOT_GIVEN,
        metadata: dict = NOT_GIVEN,
    ) -> dict:
        """Create a new channel."""
        payload = {
            "name": name,
            "source": source.value,
        }

        if is_given(default_owner):
            payload["default_owner"] = default_owner

        if is_given(data):
            payload["data"] = data

        if is_given(metadata):
            payload["metadata"] = metadata

        return await self._client.post(
            "/v1/channels",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def list_channels_by_agent(
        self,
        organization_id: str,
        agent_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
    ) -> dict:
        """List channels by agent."""
        return await self._client.get(
            f"/v1/channels/agent/{agent_id}",
            params={"page": page, "limit": limit, "order": order},
            headers={"x-organization-id": organization_id},
        )

    async def retrieve_channel(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Retrieve a specific channel by ID."""
        return await self._client.get(
            f"/v1/channels/{channel_id}",
            headers={"x-organization-id": organization_id},
        )

    async def update_channel(
        self,
        organization_id: str,
        channel_id: str,
        source: ChannelSource,
        name: str = NOT_GIVEN,
        default_owner: dict = NOT_GIVEN,
        data: dict = NOT_GIVEN,
        metadata: dict = NOT_GIVEN,
    ) -> dict:
        """Update an existing channel."""
        payload = {
            "source": source.value,
        }

        if is_given(name):
            payload["name"] = name

        if is_given(default_owner):
            payload["default_owner"] = default_owner

        if is_given(data):
            payload["data"] = data

        if is_given(metadata):
            payload["metadata"] = metadata

        return await self._client.patch(
            f"/v1/channels/{channel_id}",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def delete_channel(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Delete a channel."""
        return await self._client.delete(
            f"/v1/channels/{channel_id}",
            headers={"x-organization-id": organization_id},
        )

    # WAHA specific endpoints
    async def waha_webhook(
        self,
        payload: dict,
    ) -> dict:
        """Handle WAHA webhook."""
        return await self._client.post(
            "/v1/channels/waha/webhooks",
            json=payload,
        )

    async def connect_waha_channel(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Connect WAHA channel and get QR code."""
        return await self._client.get(
            f"/v1/channels/waha/{channel_id}/connect",
            headers={"x-organization-id": organization_id},
        )

    async def disconnect_waha_channel(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Disconnect WAHA channel."""
        return await self._client.get(
            f"/v1/channels/waha/{channel_id}/disconnect",
            headers={"x-organization-id": organization_id},
        )

    # WhatsApp specific endpoints
    async def whatsapp_webhook_verify(self) -> dict:
        """Verify WhatsApp webhook."""
        return await self._client.get("/v1/channels/whatsapp/webhooks")

    async def whatsapp_webhook(self) -> dict:
        """Handle WhatsApp webhook."""
        return await self._client.post("/v1/channels/whatsapp/webhooks")

    async def verify_whatsapp_connection(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Verify WhatsApp connection."""
        return await self._client.get(
            f"/v1/channels/whatsapp/{channel_id}/verify",
            headers={"x-organization-id": organization_id},
        )

    # Legacy endpoints (without /v1/ prefix)
    async def waha_webhook_legacy(
        self,
        payload: dict,
    ) -> dict:
        """Handle WAHA webhook (legacy endpoint)."""
        return await self._client.post("/waha/webhooks", json=payload)

    async def connect_waha_channel_legacy(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Connect WAHA channel (legacy endpoint)."""
        return await self._client.get(
            f"/waha/{channel_id}/connect",
            headers={"x-organization-id": organization_id},
        )

    async def disconnect_waha_channel_legacy(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Disconnect WAHA channel (legacy endpoint)."""
        return await self._client.get(
            f"/waha/{channel_id}/disconnect",
            headers={"x-organization-id": organization_id},
        )

    async def whatsapp_webhook_verify_legacy(self) -> dict:
        """Verify WhatsApp webhook (legacy endpoint)."""
        return await self._client.get("/whatsapp/webhooks")

    async def whatsapp_webhook_legacy(self) -> dict:
        """Handle WhatsApp webhook (legacy endpoint)."""
        return await self._client.post("/whatsapp/webhooks")

    async def verify_whatsapp_connection_legacy(
        self,
        organization_id: str,
        channel_id: str,
    ) -> dict:
        """Verify WhatsApp connection (legacy endpoint)."""
        return await self._client.get(
            f"/whatsapp/{channel_id}/verify",
            headers={"x-organization-id": organization_id},
        )

    async def webhooks_verify_legacy(self) -> dict:
        """Verify webhooks (legacy endpoint)."""
        return await self._client.get("/webhooks")

    async def webhooks_legacy(self) -> dict:
        """Handle webhooks (legacy endpoint)."""
        return await self._client.post("/webhooks") 