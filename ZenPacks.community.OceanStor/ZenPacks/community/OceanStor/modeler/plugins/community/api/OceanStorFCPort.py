"""Models Huawei OceanStor Storage using the Storage REST API."""

from ZenPacks.community.OceanStor.lib.model import OceanStorModel, OceanStorBase


class _OceanStorFCPort(OceanStorModel):
    relname = 'oceanStorFCPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorFCPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'WWN': (OceanStorModel._parse_str, None),
        'RUNSPEED': (OceanStorModel._parse_port_speed, None),
        'MAXSPEED': (OceanStorModel._parse_port_speed, None),
        'FCRUNMODE': (OceanStorModel._parse_port_runmode, None),
        'PORTSWITCH': (OceanStorModel._parse_enable_disable, None),
        'numberOfInitiators': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_fc_ports()


class OceanStorFCPort(OceanStorBase):
    DEVICE_MODELERS = {'OceanStorFCPort': _OceanStorFCPort}
