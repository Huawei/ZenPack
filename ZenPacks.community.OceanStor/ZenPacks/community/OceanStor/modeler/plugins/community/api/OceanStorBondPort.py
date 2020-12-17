"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorBondPort(OceanStorModel):
    relname = 'oceanStorBondPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorBondPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'MTU': (OceanStorModel._parse_str, None),
        'numberOfPorts': (OceanStorModel._parse_member_number_of_bond_port, None),
    }

    def get_data(self, __):
        return self.cli.get_bond_ports()


class OceanStorBondPort(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorBondPort': _OceanStorBondPort}
