"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorEnclosure(OceanStorModel):
    relname = 'oceanStorEnclosures'
    modname = 'ZenPacks.community.OceanStor.OceanStorEnclosure'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'MODEL': (OceanStorModel._parse_enclosure_model, None),
        'TEMPERATURE': (OceanStorModel._parse_str, None),
        'SERIALNUM': (OceanStorModel._parse_str, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_enclosures()


class OceanStorEnclosure(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorEnclosure': _OceanStorEnclosure}
