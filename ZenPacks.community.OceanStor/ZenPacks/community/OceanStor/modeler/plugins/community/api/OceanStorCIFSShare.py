"""Models Huawei OceanStor Storage using the Storage REST API."""

import math

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorCIFSShare(OceanStorModel):
    relname = 'oceanStorCIFSShares'
    modname = 'ZenPacks.community.OceanStor.OceanStorCIFSShare'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'FSID': (OceanStorModel._parse_id, None),
        'SHAREPATH': (OceanStorModel._parse_str, None),
        'DESCRIPTION': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        total_shares = []
        count = self.cli.get_cifs_share_count()
        for_range = int(math.ceil(float(count) / 100))
        for i in range(for_range):
            shares = self.cli.get_cifs_shares(i * 100, (i + 1) * 100)
            total_shares.extend([i for i in shares if i['FSID'] != '--'])
        return total_shares


class OceanStorCIFSShare(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorCIFSShare': _OceanStorCIFSShare}
