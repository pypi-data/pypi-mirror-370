from ablelabs.neon_v2.notable.core import Base

class Pipette(Base):
    async def get_pipette(self) -> dict:
        """Get current pipette configuration."""
        return await self._get("/api/v1/config/pipette/")

    async def set_pipette(self, config: dict) -> dict:
        """Set pipette configuration (e.g., {'1': '8ch_200ul'})."""
        return await self._post("/api/v1/config/pipette/", body=config)