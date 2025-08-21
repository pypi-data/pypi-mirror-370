from ablelabs.neon_v2.notable.core import Base

class UpperModule(Base):
    # Main operation methods
    async def initialize(
        self, home_axes: bool = True, move_to_ready: bool = True
    ) -> None:
        """Initialize robot (homing all axes and move to ready position)."""
        body = {"home_axes": home_axes, "move_to_ready": move_to_ready}
        return await self._post("/api/v1/controller/upper-module/initialize", body=body)

    async def move_z_up(self) -> None:
        """Move all Z axes to safe height."""
        return await self._post("/api/v1/controller/upper-module/move-z-up")

    async def move_to(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        z_reference: str = "TOP",
        xyz_offset: list = None,
        z_speed = False,
    ) -> None:
        """Move safely to specified deck well position."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
            "z_reference": z_reference,
            "z_speed": z_speed,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post("/api/v1/controller/upper-module/move-to", body=body)

    async def move_xy(self, x: float, y: float, safe_z_height: bool = True) -> None:
        """Move to XY coordinates after raising Z to safe height."""
        body = {"x": x, "y": y, "safe_z_height": safe_z_height}
        return await self._post("/api/v1/controller/upper-module/move-xy", body=body)

    async def move_z(
        self,
        pipette_number: int,
        deck_number: int,
        z_reference: str = "TOP",
        z_offset: float = 0,
        z_speed = False,
    ) -> None:
        """Move only Z axis to specified height at current XY position."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "z_reference": z_reference,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post("/api/v1/controller/upper-module/move-z", body=body)

    async def step_z(
        self, pipette_number: int, z_offset: float, z_speed: bool = False
    ) -> None:
        """Move Z axis by relative distance from current position."""
        body = {
            "pipette_number": pipette_number,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post("/api/v1/controller/upper-module/step-z", body=body)

    async def pick_up_tip(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        xyz_offset: list = None,
    ) -> None:
        """Pick up tips at specified position."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/pick-up-tip", body=body
        )

    async def drop_tip(
        self,
        pipette_number: int,
        deck_number: int = None,
        well: str = "A1",
        xyz_offset: list = None,
    ) -> None:
        """Drop tips at specified position."""
        body = {"pipette_number": pipette_number, "well": well}
        if deck_number is not None:
            body["deck_number"] = deck_number
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post("/api/v1/controller/upper-module/drop-tip", body=body)

    async def ready_plunger(
        self, pipette_number: int, flow_rate = False
    ) -> None:
        """Move plunger to ready position for aspiration."""
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/ready-plunger", body=body
        )

    async def blow_out(
        self, pipette_number: int, flow_rate = False
    ) -> None:
        """Blow out remaining liquid in tip."""
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post("/api/v1/controller/upper-module/blow-out", body=body)

    async def drop_plunger(self, pipette_number: int) -> None:
        """Move plunger down for tip ejection."""
        body = {"pipette_number": pipette_number}
        return await self._post(
            "/api/v1/controller/upper-module/drop-plunger", body=body
        )

    async def aspirate(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Aspirate specified volume of liquid."""
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post("/api/v1/controller/upper-module/aspirate", body=body)

    async def dispense(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Dispense specified volume of liquid."""
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post("/api/v1/controller/upper-module/dispense", body=body)

    async def mix(
        self,
        pipette_number: int,
        cycle: int,
        volume: float,
        flow_rate: float,
        delay: float = 0,
        z_offset: float = 0,
    ) -> None:
        """Mix liquid at current position."""
        body = {
            "pipette_number": pipette_number,
            "cycle": cycle,
            "volume": volume,
            "flow_rate": flow_rate,
            "delay": delay,
            "z_offset": z_offset,
        }
        return await self._post("/api/v1/controller/upper-module/mix", body=body)

    # Estimation methods
    async def estimate_initialize(
        self, home_axes: bool = True, move_to_ready: bool = True
    ) -> None:
        """Estimate time for initialization."""
        body = {"home_axes": home_axes, "move_to_ready": move_to_ready}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/initialize", body=body
        )

    async def estimate_move_z_up(self) -> None:
        """Estimate time for moving all Z axes up."""
        return await self._post("/api/v1/controller/upper-module/estimate/move-z-up")

    async def estimate_move_to(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        z_reference: str = "TOP",
        xyz_offset: list = None,
        z_speed = False,
    ) -> None:
        """Estimate time for move_to operation."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
            "z_reference": z_reference,
            "z_speed": z_speed,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-to", body=body
        )

    async def estimate_move_xy(
        self, x: float, y: float, safe_z_height: bool = True
    ) -> None:
        """Estimate time for XY movement."""
        body = {"x": x, "y": y, "safe_z_height": safe_z_height}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-xy", body=body
        )

    async def estimate_move_z(
        self,
        pipette_number: int,
        deck_number: int,
        z_reference: str = "TOP",
        z_offset: float = 0,
        z_speed = False,
    ) -> None:
        """Estimate time for Z movement."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "z_reference": z_reference,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-z", body=body
        )

    async def estimate_step_z(
        self, pipette_number: int, z_offset: float, z_speed: bool = False
    ) -> None:
        """Estimate time for Z step movement."""
        body = {
            "pipette_number": pipette_number,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/step-z", body=body
        )

    async def estimate_pick_up_tip(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        xyz_offset: list = None,
    ) -> None:
        """Estimate time for pick_up_tip operation."""
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/pick-up-tip", body=body
        )

    async def estimate_drop_tip(
        self,
        pipette_number: int,
        deck_number: int = None,
        well: str = "A1",
        xyz_offset: list = None,
    ) -> None:
        """Estimate time for drop_tip operation."""
        body = {"pipette_number": pipette_number, "well": well}
        if deck_number is not None:
            body["deck_number"] = deck_number
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/drop-tip", body=body
        )

    async def estimate_ready_plunger(
        self, pipette_number: int, flow_rate = False
    ) -> None:
        """Estimate time for plunger ready operation."""
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/ready-plunger", body=body
        )

    async def estimate_blow_out(
        self, pipette_number: int, flow_rate = False
    ) -> None:
        """Estimate time for blow out operation."""
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/blow-out", body=body
        )

    async def estimate_drop_plunger(self, pipette_number: int) -> None:
        """Estimate time for plunger drop operation."""
        body = {"pipette_number": pipette_number}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/drop-plunger", body=body
        )

    async def estimate_aspirate(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Estimate time for aspirate operation."""
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/aspirate", body=body
        )

    async def estimate_dispense(
        self,
        pipette_number: int,
        volume: float,
        flow_rate,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Estimate time for dispense operation."""
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/dispense", body=body
        )

    async def estimate_mix(
        self,
        pipette_number: int,
        cycle: int,
        volume: float,
        flow_rate: float,
        delay: float = 0,
        z_offset: float = 0,
    ) -> None:
        """Estimate time for mix operation."""
        body = {
            "pipette_number": pipette_number,
            "cycle": cycle,
            "volume": volume,
            "flow_rate": flow_rate,
            "delay": delay,
            "z_offset": z_offset,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/mix", body=body
        )