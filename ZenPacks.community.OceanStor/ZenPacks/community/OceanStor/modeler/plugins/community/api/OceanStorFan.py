"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorFan(OceanStorModel):
    relname = 'oceanStorFans'
    modname = 'ZenPacks.community.OceanStor.OceanStorFan'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'RUNLEVEL': (OceanStorModel._parse_fan_run_level, None),
    }

    def get_data(self, __):
        return self.cli.get_fans()


class OceanStorFan(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorFan': _OceanStorFan}
