"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorPower(OceanStorModel):
    relname = 'oceanStorPowers'
    modname = 'ZenPacks.community.OceanStor.OceanStorPower'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'POWERTYPE': (OceanStorModel._parse_power_type, None),
        'MODEL': (OceanStorModel._parse_str, None),
        'MANUFACTURER': (OceanStorModel._parse_str, None),
        'SERIALNUMBER': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_powers()


class OceanStorPower(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorPower': _OceanStorPower}
