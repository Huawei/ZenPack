"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorHost(OceanStorModel):
    relname = 'oceanStorHosts'
    modname = 'ZenPacks.community.OceanStor.OceanStorHost'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'OPERATIONSYSTEM': (OceanStorModel._parse_os, None),
        'IP': (OceanStorModel._parse_str, None),
        'INITIATORNUM': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
    }

    def get_data(self, __):
        return self.cli.get_hosts()


class OceanStorHost(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorHost': _OceanStorHost}
