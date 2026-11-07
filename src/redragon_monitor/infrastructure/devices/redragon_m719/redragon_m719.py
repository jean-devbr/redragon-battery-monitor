from redragon_monitor.domain.connection_type import ConnectionType
from redragon_monitor.domain.device_spec import DeviceSpec


class RedragonM719:
    NAME = "Redragon M719RGB-PRO"
    VENDOR_ID = 0x3554
    PID_USB_C = 0xF55E
    PID_RECEIVER = 0xF5D5
    USAGE_PAGE = 0xFF02
    REPORT_ID = 0x08
    REPORT_BYTES = 16

    @classmethod
    def spec(cls) -> DeviceSpec:
        return DeviceSpec(
            name=cls.NAME,
            vendor_id=cls.VENDOR_ID,
            connections={cls.PID_USB_C: ConnectionType.USB_C, cls.PID_RECEIVER: ConnectionType.RECEIVER},
            usage_page=cls.USAGE_PAGE,
            report_id=cls.REPORT_ID,
            report_bytes=cls.REPORT_BYTES,
        )
