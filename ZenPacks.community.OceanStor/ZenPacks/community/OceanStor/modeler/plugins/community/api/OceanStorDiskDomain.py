"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorDiskDomain(OceanStorModel):
    relname = 'oceanStorDiskDomains'
    modname = 'ZenPacks.community.OceanStor.OceanStorDiskDomain'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'DISKTYPE': (OceanStorModel._parse_domain_disk_type, None),
        'TOTALCAPACITY': (OceanStorModel._parse_capacity, None),
        'USEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'FREECAPACITY': (OceanStorModel._parse_capacity, None),
    }

    def get_data(self, __):
        return self.cli.get_diskdomains()


class OceanStorDiskDomain(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorDiskDomain': _OceanStorDiskDomain}
