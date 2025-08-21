from ablelabs.neon_v2.notable.core import Base


class SetupData(Base):

    async def get_setup_data(self) -> dict:
        """Get all setup data."""
        return await self._get("/api/v1/resource/setup-data/")

    async def get_setup_data_keys(self, keys: list) -> dict:
        """Get specific setup data values by keys.

        Args:
            keys: List of keys to retrieve from setup data

        Returns:
            Dictionary containing requested key-value pairs
        """
        return await self._post("/api/v1/resource/setup-data/keys", body={"keys": keys})

    async def reload(self) -> dict:
        """Reload setup_data.toml file into memory."""
        return await self._post("/api/v1/resource/setup-data/reload")

    async def update(self, data: dict) -> dict:
        """Update setup data values."""
        return await self._post("/api/v1/resource/setup-data/update", body=data)
