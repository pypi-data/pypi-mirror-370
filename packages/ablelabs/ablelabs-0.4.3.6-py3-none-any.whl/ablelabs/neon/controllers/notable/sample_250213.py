# python 3.10.0

# Install the ablelabs package using "pip install ablelabs"
# Import necessary modules from ablelabs package
from ablelabs.neon.controllers.notable.api.robot_api import RobotAPI
from ablelabs.neon.common.notable.enums import (
    Axis,
    LocationReference,
    RunStatus,
    NUMBERING_ORDER,
)
from ablelabs.neon.common.notable.structs import Speed, FlowRate, location
from ablelabs.neon.utils.location_conversion import LocationConversion
from ablelabs.neon.utils.decorators import log_func_args_async


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

    # --- Set up robot components ---

    # Configure pipettes
    await robot_api.set.pipettes(
        {
            1: "8ch200ul",
        }
    )

    # Configure tips
    await robot_api.set.tips(
        {
            1: "tip_200",
        }
    )

    # Configure labware layout on the deck
    await robot_api.set.labwares(
        {
            1: "12_reservoir",
            2: "96_rv_plate",
            3: "96_pcr_plate",
            10: "tipbox_200",
            11: "tipbox_200",
            12: "trash",
        }
    )

    # --- User Defined ---

    pipette_number = 1
    reservoir = 1
    rv_plate = 2
    pcr_plate = 3
    tipboxs = [10, 11]
    trash = 12
    tipbox_wells = [(tipbox, f"a{col+1}") for tipbox in tipboxs for col in range(12)]
    pipette_volume = 200
    wells = [f"a{col+1}" for col in range(12)]

    @log_func_args_async(log_before_func=print)
    async def pick_up_tip():
        tipbox, well = tipbox_wells.pop(0)
        print(f"{tipbox=} {well=}")
        await robot_api.motion.pick_up_tip(
            pipette_number=pipette_number,
            location=location(location_number=tipbox, well=well),
        )

    @log_func_args_async(log_before_func=print)
    async def drop_tip():
        await robot_api.motion.drop_tip(
            pipette_number=pipette_number,
            location=location(location_number=trash),
        )

    @log_func_args_async(log_before_func=print)
    async def aspirate(deck: int, well: str, volume: float):
        await robot_api.motion.aspirate(
            pipette_number=pipette_number,
            volume=volume,
            location=location(
                location_number=deck,
                well=well,
                reference=LocationReference.BOTTOM,
            ),
        )

    @log_func_args_async(log_before_func=print)
    async def dispense(deck: int, well: str, volume: float):
        await robot_api.motion.dispense(
            pipette_number=pipette_number,
            volume=volume,
            location=location(
                location_number=deck,
                well=well,
                reference=LocationReference.BOTTOM,
            ),
        )

    # --- Motion Commands ---

    # Initialize the motion system
    await robot_api.motion.initialize()

    # reservoir -> 96_rv_plate: 10ul, multi, reuse tip
    volume = 10
    chunk_count = int(pipette_volume / volume)
    chunked_wells = [
        wells[i : i + chunk_count] for i in range(0, len(wells), chunk_count)
    ]

    await pick_up_tip()
    for wells in chunked_wells:
        await aspirate(deck=reservoir, well="a1", volume=volume * len(wells))
        for well in wells:
            await dispense(deck=rv_plate, well=well, volume=volume)
    await drop_tip()

    # 96_rv_plate -> 96_pcr_plate: 10ul, single, change tip
    volume = 10
    for well in wells:
        await pick_up_tip()
        await aspirate(deck=rv_plate, well=well, volume=volume)
        await dispense(deck=pcr_plate, well=well, volume=volume)
        await drop_tip()


if __name__ == "__main__":
    # Run the main async function with an event loop
    import asyncio

    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
