# python 3.10 버전

# 가상환경 설정
## python -m venv .venv
## py 3.10 -m venv .venv

# ablelabs 패키지 설치
## pip install ablelabs

# Neon.exe + resources 파일 위치 확인
## resources 폴더는 Neon.exe와 같은 폴더 또는 하위 폴더에

# subprocess.Popen으로 Neon.exe 실행

# connect -> wait_boot -> set_pipettes/tips/labwares 순서대로 호출


import asyncio
import sys, os
import cv2

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.controllers.notable.kribb.api.robot_api import RobotAPI
from ablelabs.neon.common.notable.enums import LocationType, Axis, LocationReference
from ablelabs.neon.common.notable.structs import Speed, FlowRate, location
from ablelabs.neon.utils.format_conversion import floor_decimal
from ablelabs.neon.utils.location_conversion import LocationConversion, NUMBERING_ORDER


async def main():
    import subprocess

    # for windows.
    # subprocess.Popen(
    #     [
    #         r"C:\Users\ABLE Labs\Desktop\ABLE-Elba\robot\dist\Neon.exe",
    #     ]
    # )

    # for mac.
    # subprocess.Popen(
    #     [
    #         r"/Users/sypark/Code/ABLE-Elba/.venv/bin/python",
    #         r"/Users/sypark/Code/ABLE-Elba/robot/src/controllers/notable/kribb/robot_router.py",
    #     ],
    #     cwd=r"/Users/sypark/Code/ABLE-Elba",
    # )
    # await asyncio.sleep(2)

    ip = "localhost"
    port = 1234

    robot_api = RobotAPI()
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass

    await robot_api.wait_boot()

    # set
    await robot_api.set.pipettes(
        {
            # 1: "8ch1000ul",
            2: "1ch200ul",
        }
    )
    await robot_api.set.tips(
        {
            # 1: "tip_1000",
            2: "tip_200",
        }
    )
    await robot_api.set.camera(pipette_number=1)
    await robot_api.set.deck_modules(
        {
            10: "light_module",
        }
    )
    await robot_api.set.labwares(
        {
            12: "trash_#v2.5",
            11: "ablelabs_tiprack_#AL-CT-200",
            10: "spl_trayplate_60ml_#30001",
            7: "spl_96_well_0.2ml_#30096",
        }
    )

    # get
    pipette_infos = await robot_api.get.pipette_infos()
    tip_infos = await robot_api.get.tip_infos()
    deck_module_infos = await robot_api.get.deck_module_infos()
    labware_infos = await robot_api.get.labware_infos()
    setup_data = await robot_api.get.setup_data()

    x, y, z = setup_data["teaching"]["camera_1"]["deck10_up"]
    setup_data["teaching"]["camera_1"]["deck10_up"] = [x + 1, y + 2, z + 3]
    await robot_api.set.update_setup_data(setup_data, True)

    # robot
    await robot_api.stop()
    await robot_api.clear_error()  # stop 이후, motion 전에.
    await robot_api.pause()
    await robot_api.resume()
    is_connected = await robot_api.is_connected()

    # after motion.initialize
    await robot_api.motion.initialize()
    await robot_api.motion.move_to_camera(
        pipette_number=1,
        location=location(
            location_number=10,
            reference=LocationReference.BOTTOM_JUST,  # 동일하게 설정 필요.
        ),
    )
    (x_values, y_values, z_grid, width, height, scan_image) = (
        await robot_api.scan_displacement_sensor(
            pipette_number=1,
            location=location(
                location_number=10,
            ),
            padding=(5, 5),
            scan_count=(8, 5),
        )
    )
    cv2.imshow("scan_image", scan_image)
    # cv2.waitKey(0)
    await robot_api.move_to_interpolated_z(
        pipette_number=2,
        location=location(
            location_number=10,
            offset=(0, 0, 0),
            reference=LocationReference.BOTTOM,
        ),
        x=10,
        y=-15,  # 음수로 설정.
    )

    # motion
    await robot_api.motion.initialize()
    await robot_api.motion.move_to(
        pipette_number=2,
        location=location(
            location_number=7,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(1.0, 2.0, 3.0),
        ),
    )

    await robot_api.motion.pick_up_tip(
        pipette_number=2,
        location=location(
            location_number=11,
            well="a1",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=2,
        location=location(
            location_number=11,
            well="a1",
        ),
    )
    await robot_api.motion.pick_up_tip(
        pipette_number=2,
        location=location(
            location_number=11,
            well="a12",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=2,
        location=location(
            location_number=12,
        ),
    )

    await robot_api.motion.aspirate(
        pipette_number=2,
        volume=20,
        location=location(
            location_number=7,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.rise_tip(
        pipette_number=2,
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.motion.dispense(
        pipette_number=2,
        volume=20,
        location=location(
            location_number=7,
            well="a2",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.mix(
        pipette_number=2,
        volume=20,
        iteration=2,
        # location=location(
        #     location_number=7,
        #     well="a3",
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(20),
        delay=0.1,
    )
    await robot_api.motion.blow_out(
        pipette_number=2,
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.move_to_ready()

    # axis
    position = await robot_api.axis.get_position(axis=Axis.X)  # mm
    await robot_api.axis.set_speed(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.set_accel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.set_decel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.disable(axis=Axis.X)
    await robot_api.axis.enable(axis=Axis.X)
    await robot_api.axis.stop(axis=Axis.X)
    await robot_api.axis.home(axis=Axis.X)
    await robot_api.axis.wait_home_done(axis=Axis.X)
    await robot_api.axis.jog(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.jog(axis=Axis.X, value=0)  # mm/sec
    await robot_api.axis.step(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)
    await robot_api.axis.move(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)

    # optic
    await robot_api.optic.set_camera_live(on=True)
    image: cv2.Mat = await robot_api.optic.camera_capture(resize_ratio=0.5)
    # await robot_api.optic.camera_show(winname="camera", resize_ratio=0.5)
    await robot_api.optic.set_camera_live(on=False)
    await robot_api.optic.set_led_brightness(value=3)
    await robot_api.optic.set_led_on_off(on=True)
    image: cv2.Mat = await robot_api.optic.camera_capture(resize_ratio=0.3)
    await robot_api.optic.set_led_on_off(on=False)
    await robot_api.optic.set_displacement_zero()
    z = await robot_api.optic.get_displacement_value()
    image = cv2.imread(
        "/Users/sypark/Code/ABLE-Elba/robot/tests/notable_kribb/images/240904.bmp"
    )
    # cv2.imshow("image", image)
    (crop_info, label_infos, detected_image, process_images) = await robot_api.optic.detect_colony(
        image=image,  # or None (to use last captured image)
        resize_ratio=0.5,
        padding=(0.5, 0.5, 0.5, 0.5),
        rect_refer=(8, 8, 83, 83),
        rect_tolerance=5,
        vignette_size=30,
        binary_thresh=170,
        crop_border_thresh=30,
        return_process_images=True,
        font_scale=0.7,  # or None (to do not add index)
    )
    if process_images:
        cv2.imshow("vignette_image", process_images["vignette_image"])
        cv2.imshow("normalized_image", process_images["normalized_image"])
        cv2.imshow("binary_image", process_images["binary_image"])
        cv2.imshow("crop_border_image", process_images["crop_border_image"])
    for label_info in label_infos:
        info = [
            label_info.index,
            label_info.width,
            label_info.height,
            label_info.area,
            label_info.centroid,
            label_info.inscribed_center,
            label_info.inscribed_radius,
            label_info.perimeter,
            label_info.circularity,
            label_info.brightness,
            label_info.color,
            label_info.contours,
        ]
    cv2.imshow("detected_image", detected_image)
    (picked_infos, groupped_infos, groupped_image) = await robot_api.optic.group_colony(
        crop_info=crop_info,
        label_infos=label_infos,
        image=image,  # or None (to use last captured image)
        pick_count=3,
        resize_ratio=0.5,
        padding=(0.5, 0.5, 0.5, 0.5),
        initial_dist=60,
        row=8,
        column=12,
    )
    cv2.imshow("groupped_image", groupped_image)
    crop_x, crop_y, crop_w, crop_h = crop_info
    agar_plate_info: dict = labware_infos[10]
    well_offset_x, well_offset_y = (9, 6)
    xys = []
    for group_number, picked_info in dict(picked_infos).items():
        if not picked_info:
            continue
        for info in picked_info:
            x_pixel, y_pixel = info.inscribed_center
            x = (x_pixel / crop_w * agar_plate_info["well_x"]) + well_offset_x
            y = (y_pixel / crop_h * agar_plate_info["well_y"]) + well_offset_y
            xys.append((x, -y))  # y는 음수로 설정.
    target_plate_info: dict = labware_infos[7]
    well_index = 1
    for x, y in xys:
        well_row, well_column = LocationConversion.get_row_column(
            row_count=target_plate_info["row_count"],
            col_count=target_plate_info["column_count"],
            numbering_order=NUMBERING_ORDER.LTR_TTB,
            number=well_index,
        )
        well = LocationConversion.get_well(row=well_row, column=well_column)
        await robot_api.motion.move_to(
            pipette_number=2,
            location=location(
                location_number=10,
                reference=LocationReference.BOTTOM_JUST,
                offset=(x, y, -1.6),
            ),
            optimize=False,
        )
        await robot_api.motion.mix(
            pipette_number=2,
            volume=2,
            iteration=2,
            location=location(
                location_number=7,
                well=well,
                reference=LocationReference.BOTTOM,
                offset=(0, 0, 1),
            ),
        )
        well_index += 1

    cv2.waitKey(0)

    import io

    success, encoded_image = cv2.imencode(".png", image)
    # if not success:
    #     raise HTTPException(status_code=500, detail="Image encoding failed")
    image_bytes = io.BytesIO(encoded_image.tobytes())
    # return StreamingResponse(image_bytes, media_type="image/png")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
