from ablelabs.neon_v2.notable.core import Base


class Library(Base):

    async def get_pipette(self) -> dict:
        """Get pipette library information."""
        return await self._get("/api/v1/resource/library/pipette")

    async def update(self, pipette_code: str, data: dict) -> dict:
        """Update specific pipette library data."""
        return await self._post(
            "/api/v1/resource/library/pipette/update",
            params={"pipette_code": pipette_code},
            body=data,
        )

    async def getlabware(self) -> dict:
        """Get labware library information."""
        return await self._get("/api/v1/resource/library/labware")

    async def reload(self) -> dict:
        """Reload pipette and labware libraries from files."""
        return await self._post("/api/v1/resource/library/reload")
