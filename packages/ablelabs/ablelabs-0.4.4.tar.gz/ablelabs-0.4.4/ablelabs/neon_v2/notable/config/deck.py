from ablelabs.neon_v2.notable.core import Base

class Deck(Base):
    async def get_deck(self) -> dict:
        """Get current deck configuration."""
        return await self._get("/api/v1/config/deck/")

    async def set_deck(self, config: dict) -> dict:
        """Set deck configuration (e.g., {'1': 'ablelabs_tip_box_200'})."""
        return await self._post("/api/v1/config/deck/", body=config)