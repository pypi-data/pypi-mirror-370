from ablelabs.neon_v2.notable.core import Base
class Robot(Base):
    async def get_status(self) -> dict:
        """Get current robot execution status (IDLE, RUNNING, PAUSED)."""
        return await self._get("/api/v1/action/robot/status")

    async def pause(self) -> None:
        """Pause currently running protocol."""
        return await self._post("/api/v1/action/robot/status/pause")

    async def resume(self) -> None:
        """Resume paused protocol."""
        return await self._post("/api/v1/action/robot/status/resume")

    async def stop(self) -> None:
        """Stop currently running protocol."""
        return await self._post("/api/v1/action/robot/status/stop")

    async def reset(self) -> None:
        """Reset robot state."""
        return await self._post("/api/v1/action/robot/status/reset")