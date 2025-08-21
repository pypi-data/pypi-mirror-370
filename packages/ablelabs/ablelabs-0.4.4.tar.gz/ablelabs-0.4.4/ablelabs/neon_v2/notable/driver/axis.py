from ablelabs.neon_v2.notable.core import Base


class Axis(Base):
    async def get_max_speed(self) -> dict:
        """Get maximum speed for all axes."""
        return await self._get("/api/v1/driver/axis/max-speed")

    async def get_status(self, axis: str) -> dict:
        """Get current status of specific axis."""
        return await self._get("/api/v1/driver/axis/status", params={"axis": axis})

    async def get_fault(self, axis: str) -> dict:
        """Get fault status for specific axis."""
        return await self._get("/api/v1/driver/axis/fault", params={"axis": axis})

    async def get_error_code(self, axis: str) -> dict:
        """Get error code for specific axis."""
        return await self._get("/api/v1/driver/axis/error-code", params={"axis": axis})

    async def is_enabled(self, axis: str) -> bool:
        """Check if specific axis servo is enabled."""
        return await self._get("/api/v1/driver/axis/is-enabled", params={"axis": axis})

    async def is_home_done(self, axis: str) -> bool:
        """Check if homing is completed for specific axis."""
        return await self._get(
            "/api/v1/driver/axis/is-home-done", params={"axis": axis}
        )

    async def is_moving(self, axis: str) -> bool:
        """Check if specific axis is currently moving."""
        return await self._get("/api/v1/driver/axis/is-moving", params={"axis": axis})

    async def is_move_done(self, axis: str) -> bool:
        """Check if last movement command is completed for specific axis."""
        return await self._get(
            "/api/v1/driver/axis/is-move-done", params={"axis": axis}
        )

    async def get_position(self, axis: str, unit: bool = True) -> dict:
        """Get current position of specific axis."""
        return await self._get(
            "/api/v1/driver/axis/position", params={"axis": axis, "unit": unit}
        )

    async def set_position(self, axis: str, position: float, unit: bool = True) -> dict:
        """Force set current position value without actual movement."""
        params = {"axis": axis, "position": position, "unit": unit}
        return await self._post("/api/v1/driver/axis/position", params=params)

    async def get_home_offset(self, axis: str) -> dict:
        """Get home offset value for specific axis."""
        return await self._get("/api/v1/driver/axis/home-offset", params={"axis": axis})

    async def set_home_offset(self, axis: str, home_offset: float) -> dict:
        """Set home offset value for specific axis."""
        params = {"axis": axis, "home_offset": home_offset}
        return await self._post("/api/v1/driver/axis/home-offset", params=params)

    async def get_resolution(self, axis: str) -> float:
        """Get resolution value for specific axis."""
        return await self._get("/api/v1/driver/axis/resolution", params={"axis": axis})

    async def set_resolution(self, axis: str, resolution: float) -> dict:
        """Set resolution value for specific axis."""
        params = {"axis": axis, "resolution": resolution}
        return await self._post("/api/v1/driver/axis/resolution", params=params)

    async def enable(self, axis: str) -> dict:
        """Enable axis servo."""
        return await self._post("/api/v1/driver/axis/enable", params={"axis": axis})

    async def disable(self, axis: str) -> dict:
        """Disable axis servo."""
        return await self._post("/api/v1/driver/axis/disable", params={"axis": axis})

    async def clear_fault(self, axis: str) -> dict:
        """Clear fault state for specific axis."""
        return await self._post(
            "/api/v1/driver/axis/clear-fault", params={"axis": axis}
        )

    async def set_digital_output(self, axis: str, channel: int, on: bool) -> dict:
        """Control digital output connected to specific axis driver."""
        params = {"axis": axis, "channel": channel, "on": on}
        return await self._post("/api/v1/driver/axis/digital-output", params=params)

    async def stop(self, axis: str) -> dict:
        """Stop axis movement immediately."""
        return await self._post("/api/v1/driver/axis/stop", params={"axis": axis})

    async def home(self, axis: str) -> dict:
        """Execute homing operation for specified axis."""
        return await self._post("/api/v1/driver/axis/home", params={"axis": axis})

    async def set_speed(self, axis: str, speed: float, unit: bool = True) -> dict:
        """Set movement speed for specific axis."""
        params = {"axis": axis, "speed": speed, "unit": unit}
        return await self._post("/api/v1/driver/axis/speed", params=params)

    async def set_accel(self, axis: str, accel: float, unit: bool = True) -> dict:
        """Set acceleration for specific axis."""
        params = {"axis": axis, "accel": accel, "unit": unit}
        return await self._post("/api/v1/driver/axis/accel", params=params)

    async def set_decel(self, axis: str, decel: float, unit: bool = True) -> dict:
        """Set deceleration for specific axis."""
        params = {"axis": axis, "decel": decel, "unit": unit}
        return await self._post("/api/v1/driver/axis/decel", params=params)

    async def jog(self, axis: str, value: float, unit: bool = True) -> dict:
        """Move axis continuously at specified speed (0 = stop)."""
        params = {"axis": axis, "value": value, "unit": unit}
        return await self._post("/api/v1/driver/axis/jog", params=params)

    async def step(self, axis: str, value: float, unit: bool = True) -> dict:
        """Move axis by relative distance from current position."""
        return await self._post(
            "/api/v1/driver/axis/step",
            params={"axis": axis, "value": value, "unit": unit},
        )

    async def move(self, axis: str, position: float, unit: bool = True) -> dict:
        """Move axis to absolute position."""
        return await self._post(
            "/api/v1/driver/axis/move",
            params={"axis": axis, "position": position, "unit": unit},
        )

    async def wait_home_done(self, axis: str, timeout: float = None) -> dict:
        """Wait for homing operation to complete."""
        params = {"axis": axis}
        if timeout is not None:
            params["timeout"] = timeout
        return await self._post("/api/v1/driver/axis/wait-home-done", params=params)

    async def wait_move_done(self, axis: str, timeout: float = None) -> dict:
        """Wait for axis movement to complete."""
        params = {"axis": axis}
        if timeout is not None:
            params["timeout"] = timeout
        return await self._post("/api/v1/driver/axis/wait-move-done", params=params)

    async def repeat(
        self,
        axis: str,
        pos1: float,
        pos2: float,
        delay_ms: float = 0,
        count: int = 1,
        unit: bool = True,
    ) -> dict:
        """Move axis back and forth between two positions."""
        params = {
            "axis": axis,
            "pos1": pos1,
            "pos2": pos2,
            "delay_ms": delay_ms,
            "count": count,
            "unit": unit,
        }
        return await self._post("/api/v1/driver/axis/repeat", params=params)

    async def repeats(self, repeats_request: dict, unit: bool = True) -> dict:
        """Request multiple axes to repeat movement simultaneously."""
        return await self._post(
            "/api/v1/driver/axis/repeats", params={"unit": unit}, body=repeats_request
        )
