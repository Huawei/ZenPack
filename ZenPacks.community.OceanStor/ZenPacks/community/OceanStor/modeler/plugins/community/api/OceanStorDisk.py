"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorDisk(OceanStorModel):
    relname = 'oceanStorDisks'
    modname = 'ZenPacks.community.OceanStor.OceanStorDisk'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'LOCATION': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'DISKTYPE': (OceanStorModel._parse_disk_type, None),
        'CAPACITY': (OceanStorModel._parse_disk_capacity, None),
        'POOLNAME': (OceanStorModel._parse_str, None),
        'MODEL': (OceanStorModel._parse_str, None),
        'MANUFACTURER': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_disks()


class OceanStorDisk(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorDisk': _OceanStorDisk}
