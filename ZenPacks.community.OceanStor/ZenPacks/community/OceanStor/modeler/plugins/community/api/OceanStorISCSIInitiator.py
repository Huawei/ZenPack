"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorISCSIInitiator(OceanStorModel):
    relname = 'oceanStorISCSIInitiators'
    modname = 'ZenPacks.community.OceanStor.OceanStorISCSIInitiator'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ISFREE': (OceanStorModel._parse_initiator_free, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'USECHAP': (OceanStorModel._parse_yes_no, None),
        'MULTIPATHTYPE': (OceanStorModel._parse_multipath_type, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
    }

    def get_data(self, __):
        return self.cli.get_iscsi_initiators()


class OceanStorISCSIInitiator(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorISCSIInitiator': _OceanStorISCSIInitiator}
