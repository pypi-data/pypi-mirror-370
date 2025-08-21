from ablelabs.neon_v2.notable.core import Base


class IO(Base):
    # Input operations
    async def get_inputs(self) -> dict:
        """Get all digital input (DI) port states."""
        return await self._get("/api/v1/driver/io/inputs")

    async def get_outputs(self) -> dict:
        """Get all digital output (DO) port states."""
        return await self._get("/api/v1/driver/io/outputs")

    async def set_outputs(self, outputs: dict) -> dict:
        """Set multiple digital output (DO) pin states."""
        return await self._post("/api/v1/driver/io/outputs", body=outputs)

    async def get_pdo(self, pin) -> float:
        """Get PDO pin PWM state (0-100)."""
        return await self._get("/api/v1/driver/io/pdo", params={"pin": pin})

    async def set_pdo(self, pin, value) -> dict:
        """Set PDO pin state (ON/OFF or PWM 0-100)."""
        return await self._post(
            "/api/v1/driver/io/pdo", params={"pin": pin, "value": value}
        )

    async def get_environment(self) -> dict:
        """Get environment sensor data (temperature, humidity, pressure)."""
        return await self._get("/api/v1/driver/io/environment")

    async def get_door(self) -> bool:
        """Get door open/closed status."""
        return await self._get("/api/v1/driver/io/door")

    # LED controls
    async def set_led_lamp(self, on: bool) -> None:
        """Turn LED lamp on or off."""
        return await self._post("/api/v1/driver/io/led-lamp", params={"on": on})

    async def set_led_bar(
        self,
        color: str = "GREEN",
        bright_percent: int = 20,
        progress_percent: int = 100,
        blink_time_ms: int = 0,
    ) -> None:
        """Set LED bar color, brightness, progress, and blinking."""
        params = {
            "color": color,
            "bright_percent": bright_percent,
            "progress_percent": progress_percent,
            "blink_time_ms": blink_time_ms,
        }
        return await self._post("/api/v1/driver/io/led-bar", params=params)

    async def set_led_bar_r(self, percent: int) -> None:
        """Set LED bar red brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/r", params={"percent": percent}
        )

    async def set_led_bar_g(self, percent: int) -> None:
        """Set LED bar green brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/g", params={"percent": percent}
        )

    async def set_led_bar_b(self, percent: int) -> None:
        """Set LED bar blue brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/b", params={"percent": percent}
        )

    async def set_led_bar_w(self, percent: int) -> None:
        """Set LED bar white brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/w", params={"percent": percent}
        )

    async def set_led_bar_percent(self, percent: int) -> None:
        """Set LED bar progress display (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/percent", params={"percent": percent}
        )

    async def set_led_bar_blink(self, msec: int) -> None:
        """Set LED bar blink time in milliseconds (0 = no blink)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/blink", params={"msec": msec}
        )
