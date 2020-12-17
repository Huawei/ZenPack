"""Models Huawei OceanStor Storage using the Storage REST API."""

from collections import OrderedDict
import math

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorFileSystem(OceanStorModel):
    relname = 'oceanStorFileSystems'
    modname = 'ZenPacks.community.OceanStor.OceanStorFileSystem'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ALLOCTYPE': (OceanStorModel._parse_alloc_type, None),
        'CAPACITY': (OceanStorModel._parse_capacity, None),
        'AVAILABLECAPCITY': (OceanStorModel._parse_capacity, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
        'ISCLONEFS': (OceanStorModel._parse_yes_no, None),
        'inodeTotalCount': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        total_fs = []
        count = self.cli.get_filesystem_count()

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            fs = self.cli.get_filesystems(i * 100, (i + 1) * 100)
            total_fs.extend(fs)

        return total_fs


class _OceanStorFSSnapshot(OceanStorModel):
    relname = 'oceanStorFSSnapshots'
    modname = 'ZenPacks.community.OceanStor.OceanStorFSSnapshot'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'PARENTID': (OceanStorModel._parse_id, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'CONSUMEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'TIMESTAMP': (OceanStorModel._parse_timestamp, None),
    }

    def get_data(self, results):
        total_snapshots = []

        for fs in results['OceanStorFileSystem']:
            count = self.cli.get_fs_snapshot_count(fs['ID'])

            for_range = int(math.ceil(float(count)/100))
            for i in range(for_range):
                snapshots = self.cli.get_fs_snapshots(fs['ID'], i * 100, (i + 1) * 100)
                total_snapshots.extend(snapshots)

        return total_snapshots

    @classmethod
    def compname(cls, obj):
        return 'oceanStorFileSystems/' + obj['PARENTID']


class _OceanStorQuotaTree(OceanStorModel):
    relname = 'oceanStorQuotaTrees'
    modname = 'ZenPacks.community.OceanStor.OceanStorQuotaTree'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'PARENTID': (OceanStorModel._parse_id, None),
        'QUOTASWITCH': (OceanStorModel._parse_str, None),
    }

    def get_data(self, results):
        total_qtrees = []

        for fs in results['OceanStorFileSystem']:
            count = self.cli.get_quota_tree_count(fs['ID'])

            for_range = int(math.ceil(float(count)/100))
            for i in range(for_range):
                qtrees = self.cli.get_quota_trees(fs['ID'], i * 100, (i + 1) * 100)
                total_qtrees.extend(qtrees)

        return total_qtrees

    @classmethod
    def compname(cls, obj):
        return 'oceanStorFileSystems/' + obj['PARENTID']


class OceanStorFileSystem(OceanStorBase):
    DEVICE_MODELERS = OrderedDict(
        [
            ('OceanStorFileSystem', _OceanStorFileSystem),
            ('OceanStorFSSnapshot', _OceanStorFSSnapshot),
            ('OceanStorQuotaTree', _OceanStorQuotaTree),
        ]
    )
