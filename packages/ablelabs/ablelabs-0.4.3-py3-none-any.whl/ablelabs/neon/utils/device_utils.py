def check_com_port_count(required: int, port: str):
    import serial.tools.list_ports

    device_ports = [comport.device for comport in serial.tools.list_ports.comports()]
    if (count := len(device_ports)) < required:
        raise Exception(f"COM port count : {count} (< {required})")
    config_port = port
    if config_port == "any":
        # port 번호 오름차순으로 정렬.
        device_ports.sort(key=lambda port: int(port[3:]), reverse=False)
        return device_ports
    else:
        config_ports = config_port.split(" ")
        if set(config_ports) > set(device_ports):
            raise Exception(
                f"COM port mismatch : device manager={device_ports}  config={config_port}"
            )
        return config_ports
