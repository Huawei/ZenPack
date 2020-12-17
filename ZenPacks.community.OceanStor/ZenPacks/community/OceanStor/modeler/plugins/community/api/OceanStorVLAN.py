"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorVLAN(OceanStorModel):
    relname = 'oceanStorVLANs'
    modname = 'ZenPacks.community.OceanStor.OceanStorVLAN'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'TAG': (OceanStorModel._parse_str, None),
        'MTU': (OceanStorModel._parse_str, None),
        'PORTTYPE': (OceanStorModel._parse_vlan_port_type, None),
        'PORTID': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_vlans()


class OceanStorVLAN(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorVLAN': _OceanStorVLAN}
