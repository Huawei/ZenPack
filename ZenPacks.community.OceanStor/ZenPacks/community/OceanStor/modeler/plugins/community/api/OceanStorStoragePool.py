"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorStoragePool(OceanStorModel):
    relname = 'oceanStorStoragePools'
    modname = 'ZenPacks.community.OceanStor.OceanStorStoragePool'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'USAGETYPE': (OceanStorModel._parse_pool_usage, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'USERTOTALCAPACITY': (OceanStorModel._parse_capacity, None),
        'USERCONSUMEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'USERFREECAPACITY': (OceanStorModel._parse_capacity, None),
    }

    def get_data(self, __):
        return self.cli.get_storage_pools()


class OceanStorStoragePool(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorStoragePool': _OceanStorStoragePool}
