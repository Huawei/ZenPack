"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorFCInitiator(OceanStorModel):
    relname = 'oceanStorFCInitiators'
    modname = 'ZenPacks.community.OceanStor.OceanStorFCInitiator'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ISFREE': (OceanStorModel._parse_initiator_free, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'MULTIPATHTYPE': (OceanStorModel._parse_multipath_type, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
    }

    def get_data(self, __):
        return self.cli.get_fc_initiators()


class OceanStorFCInitiator(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorFCInitiator': _OceanStorFCInitiator}
