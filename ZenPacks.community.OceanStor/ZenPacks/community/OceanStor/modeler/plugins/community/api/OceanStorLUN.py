"""Models Huawei OceanStor Storage using the Storage REST API."""

import math

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorLUN(OceanStorModel):
    relname = 'oceanStorLUNs'
    modname = 'ZenPacks.community.OceanStor.OceanStorLUN'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ALLOCTYPE': (OceanStorModel._parse_alloc_type, None),
        'CAPACITY': (OceanStorModel._parse_capacity, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'EXPOSEDTOINITIATOR': (OceanStorModel._parse_mapping, None),
        'WWN': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
    }

    def get_data(self, __):
        total_luns = []
        count = self.cli.get_lun_count()

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            luns = self.cli.get_luns(i * 100, (i + 1) * 100)
            total_luns.extend(luns)

        return total_luns


class OceanStorLUN(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorLUN': _OceanStorLUN}
