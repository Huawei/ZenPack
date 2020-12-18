"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorEthPort(OceanStorModel):
    relname = 'oceanStorEthPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorEthPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'IPV4ADDR': (OceanStorModel._parse_str, None),
        'IPV4MASK': (OceanStorModel._parse_str, None),
        'IPV6ADDR': (OceanStorModel._parse_str, None),
        'IPV6MASK': (OceanStorModel._parse_str, None),
        'SPEED': (OceanStorModel._parse_port_speed, None),
        'maxSpeed': (OceanStorModel._parse_port_speed, None),
        'MTU': (OceanStorModel._parse_str, None),
        'BONDNAME': (OceanStorModel._parse_str, None),
        'PORTSWITCH': (OceanStorModel._parse_enable_disable, None),
        'numberOfInitiators': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_eth_ports()


class OceanStorEthPort(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorEthPort': _OceanStorEthPort}
