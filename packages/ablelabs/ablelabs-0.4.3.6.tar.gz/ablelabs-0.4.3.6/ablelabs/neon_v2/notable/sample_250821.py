import asyncio

# Import from new structure
from ablelabs.neon_v2.notable import Notable


async def main():
    import subprocess

    # Launch Neon.exe using subprocess (for Windows systems)
    # Ensure 'Neon.exe' and the 'resources' folder are in the correct directory
    subprocess.Popen(
        [
            r"C:\your_path\Neon.exe",
        ]
    )

    base_url = "http://localhost:7777"
    notable = Notable(base_url)

    # configure pippettes
    await notable.config.pipette.set_pipette({"1": "8ch_200ul"})

    # configure deck
    await notable.config.deck.set_deck(
        {
            "7": "ablelabs_tip_box_200",
            "8": "nest_12_reservoir_360102",
            "9": "spl_96_well_plate_30096",
            "12": "ablelabs_trash",
        }
    )
    # initialize robot
    await notable.controller.upper_module.initialize(home_axes=True, move_to_ready=True)

    # pick up tip, drop tip example
    status = await notable.action.robot.get_status()
    print(f"Robot Status: {status}")

    # Lamp control and LED bar control
    await notable.driver.io.set_led_lamp(True)
    await notable.driver.io.set_led_bar(
        color="RED", bright_percent=50, progress_percent=50, blink_time_ms=1000
    )

    # Pick up tip
    await notable.controller.upper_module.pick_up_tip(
        pipette_number=1, deck_number=7, well="A1"
    )

    # move to reservoir
    await notable.controller.upper_module.move_to(
        pipette_number=1,
        deck_number=8,
        well="A1",
        z_reference="TOP",
        xyz_offset=[0.0, 0.0, 0.0],
        z_speed=False,
    )

    # aspirate
    await notable.controller.upper_module.aspirate(
        pipette_number=1,
        volume=100.0,
        flow_rate=50.0,
        z_offset=1.0,
        pause_sec=0.0,
    )

    # move to plate
    await notable.controller.upper_module.move_to(
        pipette_number=1,
        deck_number=9,
        well="A1",
        z_reference="TOP",
        xyz_offset=[0.0, 0.0, 0.0],
        z_speed=False,
    )

    await notable.controller.upper_module.dispense(
        pipette_number=1,
        volume=100.0,
        flow_rate=50.0,
        z_offset=1.0,
        pause_sec=0.0,
    )

    # Drop tip
    await notable.controller.upper_module.drop_tip(
        pipette_number=1, deck_number=7, well="A1"
    )  # tip_box
    await notable.controller.upper_module.drop_tip(
        pipette_number=1, deck_number=12
    )  # trash


if __name__ == "__main__":
    asyncio.run(main())
