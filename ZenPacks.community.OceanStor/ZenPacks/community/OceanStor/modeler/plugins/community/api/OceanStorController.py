"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorController(OceanStorModel):
    relname = 'oceanStorControllers'
    modname = 'ZenPacks.community.OceanStor.OceanStorController'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'CPUINFO': (OceanStorModel._parse_str, None),
        'MEMORYSIZE': (OceanStorModel._parse_cache_size, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_controllers()


class OceanStorController(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorController': _OceanStorController}
