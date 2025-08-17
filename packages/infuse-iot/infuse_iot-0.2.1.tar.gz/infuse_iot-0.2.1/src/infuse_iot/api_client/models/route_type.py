from enum import Enum


class RouteType(str, Enum):
    BT_ADV = "bt_adv"
    BT_CENTRAL = "bt_central"
    BT_PERIPHERAL = "bt_peripheral"
    HCI = "hci"
    SERIAL = "serial"
    UDP = "udp"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
