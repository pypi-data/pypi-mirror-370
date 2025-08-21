# python 3.10.0

# Install the ablelabs package using "pip install ablelabs"
# Import necessary modules from ablelabs package
from ablelabs.neon.controllers.notable.api.robot_api import RobotAPI
from ablelabs.neon.common.notable.enums import (
    Axis,
    LocationReference,
    RunStatus,
)
from ablelabs.neon.common.notable.structs import Speed, FlowRate, location


async def main():
    import subprocess

    # Launch Neon.exe using subprocess (for Windows systems)
    # Ensure 'Neon.exe' and the 'resources' folder are in the correct directory
    subprocess.Popen(
        [
            r"C:\your_path\Neon.exe",
        ]
    )

    # Instantiate the robot API client
    robot_api = RobotAPI()
    # Ensure to follow the sequence: connect -> wait_boot -> set_pipettes/tips/labwares -> initialize -> motion_api for proper operation

    # Connect to the robot system
    ip = "localhost"
    port = 1234
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass  # Handle exceptions for connection failures

    # Wait for the robot system to boot
    await robot_api.wait_boot()
    # LED bar indicates the robot's current run_status
    # READY (white), INITIALIZE (blue), RUN (green), PAUSE (yellow), ERROR (red)
    await robot_api.set_run_status(RunStatus.READY)
    await robot_api.get_run_status()

    # --- Set up robot components ---

    # Configure pipettes
    await robot_api.set.pipettes(
        {
            # 1: "8ch1000ul",
            2: "1ch200ul",
        }
    )

    # Configure tips
    await robot_api.set.tips(
        {
            # 1: "tip_1000",
            2: "tip_200",
        }
    )

    # Configure labware layout on the deck
    await robot_api.set.labwares(
        {
            1: "spl_trayplate_60ml_#30001",
            2: "spl_96_well_0.2ml_#30096",
            10: "ablelabs_tiprack_#AL-CT-200",
            11: "ablelabs_tiprack_#AL-CT-1000",
            12: "trash_#v2.5",
        }
    )

    # Retrieve robot setup data
    await robot_api.get.pipette_infos()
    await robot_api.get.tip_infos()
    await robot_api.get.deck_module_infos()
    await robot_api.get.labware_infos()
    setup_data = await robot_api.get.setup_data()

    # Modify setup data: Example for teaching offsets
    x, y, z = setup_data["teaching"]["pipette_1"]["8ch200ul"]["deck1_up"]
    setup_data["teaching"]["pipette_1"]["8ch200ul"]["deck1_up"] = [x + 1, y + 2, z + 3]
    await robot_api.set.update_setup_data(setup_data, True)

    # --- Robot Control Functions ---

    # Stop, clear errors, pause, and resume robot operation
    await robot_api.stop()
    await robot_api.clear_error()  # Clear errors after stopping
    await robot_api.pause()
    await robot_api.resume()

    # Check if the robot is still connected
    is_connected = await robot_api.is_connected()

    # --- Motion Commands ---

    # Initialize the motion system
    await robot_api.motion.initialize()

    # Move pipette to a specified location with an offset
    await robot_api.motion.move_to(
        pipette_number=2,
        location=location(
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(1.0, 2.0, 3.0),
        ),
    )

    # Pick up and drop tips at specified locations
    await robot_api.motion.pick_up_tip(
        pipette_number=2,
        location=location(
            location_number=10,
            well="a1",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=2,
        location=location(
            location_number=10,
            well="a1",
        ),
    )

    # Aspirate and dispense liquids at specified locations
    await robot_api.motion.aspirate(
        pipette_number=2,
        volume=200,
        location=location(
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.dispense(
        pipette_number=2,
        volume=200,
        location=location(
            location_number=2,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )

    # Mix liquids at the last specified position
    await robot_api.motion.mix(
        pipette_number=2,
        volume=100,
        iteration=2,
        flow_rate=FlowRate.from_ul(70),
        delay=0.1,
    )

    # Blow-out liquids to clear the pipette tip
    await robot_api.motion.blow_out(
        pipette_number=2,
        flow_rate=FlowRate.from_ul(200),
    )

    # Return pipette to the ready position
    await robot_api.motion.move_to_ready()

    # --- Axis Control Commands ---

    # Retrieve, set, and adjust axis parameters (X-axis example)
    position = await robot_api.axis.get_position(axis=Axis.X)  # Get position in mm
    await robot_api.axis.set_speed(axis=Axis.X, value=10)  # Set speed in mm/sec
    await robot_api.axis.set_accel(axis=Axis.X, value=10)  # Set acceleration in mm/sec2
    await robot_api.axis.disable(axis=Axis.X)  # Disable the axis
    await robot_api.axis.enable(axis=Axis.X)  # Enable the axis
    await robot_api.axis.stop(axis=Axis.X)  # Stop the axis movement
    await robot_api.axis.home(axis=Axis.X)  # Perform homing operation
    await robot_api.axis.wait_home_done(axis=Axis.X)  # Wait for homing to complete
    await robot_api.axis.move(axis=Axis.X, value=10)  # Move axis by 10mm
    await robot_api.axis.wait_move_done(axis=Axis.X)  # Wait for movement to complete


if __name__ == "__main__":
    # Run the main async function with an event loop
    import asyncio

    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
