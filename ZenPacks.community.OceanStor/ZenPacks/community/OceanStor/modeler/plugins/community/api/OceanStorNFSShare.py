"""Models Huawei OceanStor Storage using the Storage REST API."""

import math

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorNFSShare(OceanStorModel):
    relname = 'oceanStorNFSShares'
    modname = 'ZenPacks.community.OceanStor.OceanStorNFSShare'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'FSID': (OceanStorModel._parse_id, None),
        'SHAREPATH': (OceanStorModel._parse_str, None),
        'DESCRIPTION': (OceanStorModel._parse_str, None),
        'CHARACTERENCODING': (OceanStorModel._parse_character_encoding, None),
    }

    def get_data(self, __):
        total_shares = []
        count = self.cli.get_nfs_share_count()

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            shares = self.cli.get_nfs_shares(i * 100, (i + 1) * 100)
            total_shares.extend(shares)

        return total_shares


class OceanStorNFSShare(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorNFSShare': _OceanStorNFSShare}
