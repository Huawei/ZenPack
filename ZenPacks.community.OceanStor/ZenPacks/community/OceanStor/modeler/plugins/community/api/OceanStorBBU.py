"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorBBU(OceanStorModel):
    relname = 'oceanStorBBUs'
    modname = 'ZenPacks.community.OceanStor.OceanStorBBU'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'REMAINLIFEDAYS': (OceanStorModel._parse_remain_life_days, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_backup_powers()


class OceanStorBBU(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorBBU': _OceanStorBBU}
