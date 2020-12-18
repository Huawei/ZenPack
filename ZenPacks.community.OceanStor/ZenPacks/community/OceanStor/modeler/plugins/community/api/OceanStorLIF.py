"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorLIF(OceanStorModel):
    relname = 'oceanStorLIFs'
    modname = 'ZenPacks.community.OceanStor.OceanStorLIF'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'OPERATIONALSTATUS': (OceanStorModel._parse_activate_status, None),
        'IPV4ADDR': (OceanStorModel._parse_str, None),
        'IPV6ADDR': (OceanStorModel._parse_str, None),
        'HOMEPORTNAME': (OceanStorModel._parse_str, None),
        'CURRENTPORTNAME': (OceanStorModel._parse_str, None),
        'ROLE': (OceanStorModel._parse_lif_role, None),
        'ddnsStatus': (OceanStorModel._parse_ddns_status, None),
        'SUPPORTPROTOCOL': (OceanStorModel._parse_support_protocol, None),
        'MANAGEMENTACCESS': (OceanStorModel._parse_str2, None),
        'vstoreName': (OceanStorModel._parse_str2, None),
    }

    def get_data(self, __):
        return self.cli.get_lifs()


class OceanStorLIF(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorLIF': _OceanStorLIF}
