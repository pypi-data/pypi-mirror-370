from ablelabs.neon_v2.notable.core import Base


class DriverParam(Base):

    async def get_driver_param(self) -> dict:
        """Get all driver parameters."""
        return await self._get("/api/v1/resource/driver-param/")

    async def get_driver_param_keys(self, keys: list) -> dict:
        """Get specific driver parameter values by keys."""
        return await self._post(
            "/api/v1/resource/driver-param/keys", body={"keys": keys}
        )

    async def reload(self) -> dict:
        """Reload driver parameters from file."""
        return await self._post("/api/v1/resource/driver-param/reload")

    async def update(self, data: dict) -> dict:
        """Update driver parameter values."""
        return await self._post("/api/v1/resource/driver-param/update", body=data)
