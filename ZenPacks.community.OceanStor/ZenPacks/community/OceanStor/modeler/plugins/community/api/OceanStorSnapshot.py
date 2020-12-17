"""Models Huawei OceanStor Storage using the Storage REST API."""

import math

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorSnapshot(OceanStorModel):
    relname = 'oceanStorSnapshots'
    modname = 'ZenPacks.community.OceanStor.OceanStorSnapshot'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'PARENTID': (OceanStorModel._parse_id, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'USERCAPACITY': (OceanStorModel._parse_capacity, None),
        'CONSUMEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'TIMESTAMP': (OceanStorModel._parse_timestamp, None),
        'EXPOSEDTOINITIATOR': (OceanStorModel._parse_mapping, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
        'WWN': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        total_snapshots = []
        count = self.cli.get_lun_snapshot_count()

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            snapshots = self.cli.get_lun_snapshots(i * 100, (i + 1) * 100)
            total_snapshots.extend(snapshots)

        return total_snapshots

    @classmethod
    def compname(cls, obj):
        return 'oceanStorLUNs/' + obj['PARENTID']


class OceanStorSnapshot(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorSnapshot': _OceanStorSnapshot}
