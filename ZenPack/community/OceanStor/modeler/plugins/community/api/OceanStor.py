"""Models Huawei OceanStor Storage using the Storage REST API."""

# stdlib Imports
from collections import OrderedDict
from datetime import datetime
import json
import logging
import math

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import RelationshipMap, ObjectMap
from Products.ZenUtils.Utils import prepId

from ZenPacks.community.OceanStor.lib import client
from ZenPacks.community.OceanStor.lib import utils


log = logging.getLogger('zen.Storage.Huawei.OceanStor')


class OceanStorModel(object):
    FIELD_PARSER = {}

    HEALTH_STATUS = {
        '0': 'Unknown',
        '1': 'Normal',
        '2': 'Fault',
        '3': 'Pre-Fail',
        '4': 'partially broken',
        '5': 'Degraded',
        '6': 'Bad sectors found',
        '7': 'Bit errors found',
        '8': 'Consistent',
        '9': 'Inconsistent',
        '10': 'Busy',
        '11': 'No input',
        '12': 'Low battery',
        '13': 'Single link fault',
        '14': 'Invalid',
        '15': 'WRITE_PROTECT',
    }

    RUNNING_STATUS = {
        '0': 'Unknown',
        '1': 'Normal',
        '2': 'Running',
        '3': 'Not running',
        '4': 'Not existed',
        '5': 'Sleep in high temperature',
        '6': 'Starting',
        '7': 'Power failure protection',
        '8': 'Spin down',
        '9': 'Started',
        '10': 'Link Up',
        '11': 'Link Down',
        '12': 'Powering on',
        '13': 'Powered off',
        '14': 'Precopy',
        '15': 'Copyback',
        '16': 'Reconstruction',
        '17': 'Expansion',
        '18': 'Unformatted',
        '19': 'Formatting',
        '20': 'Unmapped',
        '21': 'Initial synchronizing',
        '22': 'Consistent',
        '23': 'Synchronizing',
        '24': 'Synchronized',
        '25': 'Unsynchronized',
        '26': 'Splited',
        '27': 'Online',
        '28': 'Offline',
        '29': 'Locked',
        '30': 'Enabled',
        '31': 'Disabled',
        '32': 'balancing',
        '33': 'To be recovered',
        '34': 'Interrupted',
        '35': 'Invalid',
        '36': 'Not start',
        '37': 'Queuing',
        '38': 'Stopped',
        '39': 'Copying',
        '40': 'Completed',
        '41': 'Paused',
        '42': 'Reverse synchronizing',
        '43': 'Activated',
        '44': 'Restore',
        '45': 'Inactive',
        '46': 'Idle',
        '47': 'Powering off',
        '48': 'Charging',
        '49': 'Charging completed',
        '50': 'Discharging',
        '51': 'Upgrading',
        '52': 'Power Lost',
        '53': 'Initializing',
        '54': 'Apply Change',
        '55': 'online disable',
        '56': 'Offline disable',
        '57': 'online frozen',
        '58': 'offline frozen',
        '59': 'closed',
        '60': 'removing',
        '61': 'in service',
        '62': 'out of service',
        '63': 'Running normal',
        '64': 'Running fail',
        '65': 'Running success',
        '66': 'Running success',
        '67': 'Running failed',
        '68': 'Waiting',
        '69': 'Cancelling',
        '70': 'Cancelled',
        '71': 'About to synchronize',
        '72': 'Synchronizing data',
        '73': 'Failed to synchronize',
        '74': 'Fault',
        '75': 'Migrating',
        '76': 'Migrated',
        '77': 'Activating',
        '78': 'Deactivating',
        '79': 'Start failed',
        '80': 'Stop failed',
        '81': 'decommissioning',
        '82': 'decommissioned',
        '83': 'recommissioning',
        '84': 'replacing node',
        '85': 'scheduling',
        '86': 'Pausing',
        '87': 'Suspending',
        '88': 'Suspended',
        '89': 'Overload',
        '90': 'To be switch',
        '91': 'Switching',
        '92': 'To be cleanup',
        '93': 'FORCED START',
        '94': 'ERROR',
        '95': 'Job completed',
        '96': 'Partition Migrating',
        '97': 'Mount',
        '98': 'Umount',
        '99': 'INSTALLING',
        '100': 'To Be Synchronized',
        '101': 'Connecting',
        '102': 'Service Switching',
        '103': 'Power-on failed',
        '104': 'Repairing',
        '105': 'Abnormal',
        '106': 'Deleting',
        '107': 'Modifying',
    }

    PRODUCT_MODEL = {
        '61': '6800 V3',
        '62': '6900 V3',
        '63': '5600 V3',
        '64': '5800 V3',
        '68': '5500 V3',
        '69': '2600 V3',
        '70': '5300 V3',
        '71': '2800 V3',
        '72': '18500 V3',
        '73': '18800 V3',
        '74': '2200 V3',
        '84': '2600F V3',
        '85': '5500F V3',
        '86': '5600F V3',
        '87': '5800F V3',
        '88': '6800F V3',
        '89': '18500F V3',
        '90': '18800F V3',
        '92': '2800 V5',
        '93': '5300 V5',
        '94': '5300F V5',
        '95': '5500 V5',
        '96': '5500F V5',
        '97': '5600 V5',
        '98': '5600F V5',
        '99': '5800 V5',
        '100': '5800F V5',
        '101': '6800 V5',
        '102': '6800F V5',
        '103': '18500 V5',
        '104': '18500F V5',
        '105': '18800 V5',
        '106': '18800F V5',
        '107': '5500 V5 Elite',
        '108': '2100 V3',
        '805': 'Dorado5000 V3',
        '806': 'Dorado6000 V3',
        '807': 'Dorado18000 V3',
        '808': 'Dorado NAS',
        '809': 'Dorado NAS',  # Enhanced
        '810': 'Dorado3000 V3',
        '112': '2200 V3',  # Enhanced
        '113': '2600 V3',  # Enhanced
        '114': '2600F V3',  # Enhanced
        '115': '5300 V5',  # Enhanced
        '116': '5110 V5',
        '117': '5110F V5',
        '118': '5210 V5',
        '119': '5210F V5',
        '120': '5310 V5',
        '121': '5310F V5',
        '122': '5510 V5',
        '123': '5510F V5',
        '124': '5610 V5',
        '125': '5610F V5',
        '126': '5810 V5',
        '127': '5810F V5',
        '128': '6810 V5',
        '129': '6810F V5',
        '130': '18510 V5',
        '131': '18510F V5',
        '132': '18810 V5',
        '133': '18810F V5',
        '134': '5210 V5 Enhanced',
        '135': '5210F V5 Enhanced',
    }

    ENCLOSURE_MODEL = {
        '0': 'baseboard management controller (BMC) enclosure',
        '1': '2 U 2-controller 12-slot 3.5-inch 6 Gbit/s SAS controller enclosure',
        '2': '2 U 2-controller 24-slot 6 Gbit/s SAS controller enclosure',
        '16': '2 U 12-slot 3.5-inch 6 Gbit/s SAS disk enclosure',
        '17': '2 U SAS 24 - disk expansion enclosure',
        '18': '4 U 24 - slot 3.5 - inch 12 Gbit / s SAS disk enclosure',
        '19': '4 U Fibre Channel 24 - disk expansion enclosure',
        '20': '1 U PCIe data switch',
        '21': '4 U 75 - slot 3.5 - inch 6 Gbit / s SAS disk enclosure',
        '22': 'service processor(SVP)',
        '97': '6 U 4 - controller controller enclosure',
        '96': '3 U 2 - controller controller enclosure',
        '24': '2 U 25 - slot 2.5 - inch 6 Gbit / s SAS disk enclosure',
        '25': '4 U 24 - slot 3.5 - inch 6 Gbit / s SAS disk enclosure',
        '26': '2 U 2 - controller 25 - slot 2.5 - inch 6 Gbit / s SAS controller enclosure',
        '23': '2 U 2 - controller 12 - slot 3.5 - inch 6 Gbit / s SAS controller enclosure',
        '39': '4 U 75 - slot 3.5 - inch 12 Gbit / s SAS disk enclosure',
        '65': '2 U 25 - slot 2.5 - inch 12 Gbit / s SAS disk enclosure',
        '66': '4 U 24 - slot 3.5 - inch 12 Gbit / s SAS disk enclosure',
        '40': '2 U 2 - controller 25 - slot 2.5 - inch 12 Gbit / s SAS controller enclosure',
        '37': '2 U 2 - controller 12 - slot 3.5 - inch 6 Gbit / s SAS controller enclosure',
        '38': '2 U 2 - controller 25 - slot 2.5 - inch 6 Gbit / s SAS controller enclosure',
        '98': '2U 25 Slot 2.5 SSD Disks Enclosure',
        '99': '2 U 25 - slot 2.5 - inch active NVMe controller enclosure',
        '101': '2U 25 - slot 2.5 - inch SSD NVMe disk enclosure',
        '112': '4 U 4 - controller controller enclosure',
        '113': '2 U 2 - controller 25 - slot 2.5 - inch SAS controller enclosure',
        '114': '2 U 2 - controller 12 - slot 3.5 - inch SAS controller enclosure',
        '115': '2 U 2 - controller 36 - slot NVMe controller enclosure',
        '116': '2 U 2 - controller 25 - slot 2.5 - inch SAS controller enclosure',
        '117': '2 U 2 - controller 12 - slot 3.5 - inch SAS controller enclosure',
        '118': '2 U 25 - slot 2.5 - inch SAS IP disk enclosure',
        '119': '2 U 12 - slot 3.5 - inch SAS IP disk enclosure',
        '120': '2 U 36 - slot NVMe IP disk enclosure',
        '67': '2 U 25 - slot 2.5 - inch SAS disk enclosure',
        '69': '4 U 24 - slot 3.5 - inch SAS disk enclosure',
    }

    DISK_TYPE = {
        '0': 'FC',
        '1': 'SAS',
        '2': 'SATA',
        '3': 'SSD',
        '4': 'NL_SAS',
        '5': 'SLC SSD',
        '6': 'MLC SSD',
        '7': 'FC_SED',
        '8': 'SAS_SED',
        '9': 'SATA_SED',
        '10': 'SSD_SED',
        '11': 'NL_SAS_SED',
        '12': 'SLC_SSD_SED',
        '13': 'MLC_SSD_SED',
    }

    CHARACTER_ENCODING = {
        '0': 'UTF-8',
        '11': 'ZH',
        '12': 'GBK',
        '13': 'EUC-TW',
        '14': 'BIG5',
        '21': 'EUC-JP',
        '22': 'JIS',
        '23': 'S-JIS',
        '30': 'DE',
        '31': 'PT',
        '32': 'ES',
        '33': 'FR',
        '34': 'IT',
        '40': 'KO',
    }

    SUPPORT_PROTOCOL = {
        '0': 'NONE',
        '1': 'NFS',
        '2': 'CIFS',
        '3': 'NFS+CIFS',
        '4': 'iSCSI',
        '8': 'FC/FCoE',
    }

    OPERATION_SYSTEM = {
        '0': 'Linux',
        '1': 'Windows',
        '2': 'Solaris',
        '3': 'HP-UX',
        '4': 'AIX',
        '5': 'XenServer',
        '6': 'Mac OS',
        '7': 'VMware ESX',
        '8': 'LINUX_VIS',
        '9': 'Windows Server 2012',
        '10': 'Oracle VM',
        '11': 'OpenVMS',
    }

    def __init__(self, cli):
        self.cli = cli

    @classmethod
    def process_result(cls, result):
        oms = {}

        for i in result:
            parsed = {}

            for k in cls.FIELD_PARSER:
                if k in i:
                    obj = i[k]
                else:
                    obj = i

                func = cls.FIELD_PARSER[k][0]

                new_key = cls.FIELD_PARSER[k][1] if cls.FIELD_PARSER[k][1] else k

                try:
                    parsed[new_key] = func(obj)
                except Exception as e:
                    log.error('Parse field %s from %s error: %s', k, i, e)
                    parsed[new_key] = 'Unknown'

            compname = cls.compname(parsed)
            if compname not in oms:
                oms[compname] = []

            oms[compname].append(parsed)

        return oms

    @classmethod
    def compname(cls, obj):
        return ''

    @classmethod
    def _parse_str(cls, v):
        return '' if isinstance(v, dict) else v

    @classmethod
    def _parse_id(cls, v):
        return prepId(v)

    @classmethod
    def _parse_health_status(cls, v):
        return cls.HEALTH_STATUS.get(v, 'Unknown')

    @classmethod
    def _parse_running_status(cls, v):
        return cls.RUNNING_STATUS.get(v, 'Unknown')

    @classmethod
    def _parse_product_model(cls, v):
        if isinstance(v, dict):
            return cls.PRODUCT_MODEL.get(v.get('PRODUCTMODE'), 'Unknown')
        else:
            return v

    @classmethod
    def _parse_capacity(cls, v, sector_size=512):
        return utils.convert_capacity(v, sector_size)

    @classmethod
    def _parse_power_type(cls, v):
        return {
            '0': 'DC',
            '1': 'AC',
        }.get(v, 'unknown')

    @classmethod
    def _parse_enclosure_model(cls, v):
        return cls.ENCLOSURE_MODEL.get(v, 'Unknown')

    @classmethod
    def _parse_domain_disk_type(cls, v):
        disk_type = ''
        if 'SSDDISKNUM' in v and int(v['SSDDISKNUM']) > 0:
            disk_type += 'SSD'
        if 'SASDISKNUM' in v and int(v['SASDISKNUM']) > 0:
            if len(disk_type) > 0:
                disk_type += '/'

            disk_type += 'SAS'
        if 'NLSASDISKNUM' in v and int(v['NLSASDISKNUM']) > 0:
            if len(disk_type) > 0:
                disk_type += '/'

            disk_type += 'NL-SAS'

        return disk_type

    @classmethod
    def _parse_disk_type(cls, v):
        return cls.DISK_TYPE.get(v, 'Unknown')

    @classmethod
    def _parse_disk_capacity(cls, v):
        return cls._parse_capacity(v['SECTORS'], float(v['SECTORSIZE']))

    @classmethod
    def _parse_pool_usage(cls, v):
        return {
            '1': 'Block Storage Service',
            '2': 'File Storage Service',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_alloc_type(cls, v):
        return {
            '0': 'Thick LUN',
            '1': 'Thin LUN',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_mapping(cls, v):
        return {
            'false': 'Unmapped',
            'true': 'Mapped',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_fan_run_level(cls, v):
        return {
            '0': 'Low',
            '1': 'Normal',
            '2': 'High',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_yes_no(cls, v):
        return 'Yes' if v == 'true' else 'No'

    @classmethod
    def _parse_timestamp(cls, v):
        ts = int(v)
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def _parse_character_encoding(cls, v):
        return cls.CHARACTER_ENCODING.get(v, 'Unknown')

    @classmethod
    def _parse_enable_disable(cls, v):
        return {
            'false': 'Disable',
            'true': 'Enable',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_member_number_of_bond_port(cls, v):
        if not v.get('PORTIDLIST'):
            return 0
        port_list = json.loads(v['PORTIDLIST'])
        return len(port_list)

    @classmethod
    def _parse_activate_status(cls, v):
        return {
            'false': 'Not Activated',
            'true': 'Activated',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_lif_role(cls, v):
        return {
            '1': 'Management',
            '2': 'Service',
            '3': 'Management+Service',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_ddns_status(cls, v):
        return {
            '0': 'Invalid',
            '1': 'Enable',
            '2': 'Disabled',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_support_protocol(cls, v):
        return cls.SUPPORT_PROTOCOL.get(v, 'Unknown')

    @classmethod
    def _parse_os(cls, v):
        return cls.OPERATION_SYSTEM.get(v, 'Unknown')

    @classmethod
    def _parse_multipath_type(cls, v):
        return {
            '0': 'Default',
            '1': 'Uses 3rd-party multipath',
        }.get(v, 'Unknown')

    @classmethod
    def _parse_initiator_free(cls, v):
        return 'No' if v == 'true' else 'Yes'

    @classmethod
    def _parse_vlan_port_type(cls, v):
        return {
            '1': 'Eth Port',
            '7': 'Bond Port',
        }.get(v, 'Unknown')


class OceanStorArray(OceanStorModel):
    relname = 'oceanStorArrays'
    modname = 'ZenPacks.community.OceanStor.OceanStorArray'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'productModeString': (OceanStorModel._parse_product_model, None),
        'PRODUCTVERSION': (OceanStorModel._parse_str, None),
        'TOTALCAPACITY': (OceanStorModel._parse_capacity, None),
        'USEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'STORAGEPOOLCAPACITY': (OceanStorModel._parse_capacity, None),
        'STORAGEPOOLFREECAPACITY': (OceanStorModel._parse_capacity, None),
    }

    def get_data(self, __):
        return [self.cli.get_system()]


class OceanStorEnclosure(OceanStorModel):
    relname = 'oceanStorEnclosures'
    modname = 'ZenPacks.community.OceanStor.OceanStorEnclosure'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'MODEL': (OceanStorModel._parse_enclosure_model, None),
        'TEMPERATURE': (OceanStorModel._parse_str, None),
        'SERIALNUM': (OceanStorModel._parse_str, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_enclosures()


class OceanStorPower(OceanStorModel):
    relname = 'oceanStorPowers'
    modname = 'ZenPacks.community.OceanStor.OceanStorPower'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'POWERTYPE': (OceanStorModel._parse_power_type, None),
        'MODEL': (OceanStorModel._parse_str, None),
        'MANUFACTURER': (OceanStorModel._parse_str, None),
        'SERIALNUMBER': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_powers()


class OceanStorFan(OceanStorModel):
    relname = 'oceanStorFans'
    modname = 'ZenPacks.community.OceanStor.OceanStorFan'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'RUNLEVEL': (OceanStorModel._parse_fan_run_level, None),
    }

    def get_data(self, __):
        return self.cli.get_fans()


class OceanStorBBU(OceanStorModel):
    relname = 'oceanStorBBUs'
    modname = 'ZenPacks.community.OceanStor.OceanStorBBU'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'REMAINLIFEDAYS': (OceanStorModel._parse_str, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_backup_powers()


class OceanStorController(OceanStorModel):
    relname = 'oceanStorControllers'
    modname = 'ZenPacks.community.OceanStor.OceanStorController'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'CPUINFO': (OceanStorModel._parse_str, None),
        'MEMORYSIZE': (OceanStorModel._parse_str, None),
        'ELABEL': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_controllers()


class OceanStorDiskDomain(OceanStorModel):
    relname = 'oceanStorDiskDomains'
    modname = 'ZenPacks.community.OceanStor.OceanStorDiskDomain'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'DISKTYPE': (OceanStorModel._parse_domain_disk_type, None),
        'TOTALCAPACITY': (OceanStorModel._parse_capacity, None),
        'USEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'FREECAPACITY': (OceanStorModel._parse_capacity, None),
    }

    def get_data(self, __):
        return self.cli.get_diskdomains()


class OceanStorDisk(OceanStorModel):
    relname = 'oceanStorDisks'
    modname = 'ZenPacks.community.OceanStor.OceanStorDisk'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'LOCATION': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'DISKTYPE': (OceanStorModel._parse_disk_type, None),
        'CAPACITY': (OceanStorModel._parse_disk_capacity, None),
        'POOLNAME': (OceanStorModel._parse_str, None),
        'MODEL': (OceanStorModel._parse_str, None),
        'MANUFACTURER': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_disks()


class OceanStorStoragePool(OceanStorModel):
    relname = 'oceanStorStoragePools'
    modname = 'ZenPacks.community.OceanStor.OceanStorStoragePool'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'USAGETYPE': (OceanStorModel._parse_pool_usage, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'USERTOTALCAPACITY': (OceanStorModel._parse_capacity, None),
        'USERCONSUMEDCAPACITY': (OceanStorModel._parse_capacity, None),
        'USERFREECAPACITY': (OceanStorModel._parse_capacity, None),
    }

    def get_data(self, __):
        return self.cli.get_storage_pools()


class OceanStorLUN(OceanStorModel):
    relname = 'oceanStorLUNs'
    modname = 'ZenPacks.community.OceanStor.OceanStorLUN'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'PARENTID': (OceanStorModel._parse_id, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ALLOCTYPE': (OceanStorModel._parse_alloc_type, None),
        'CAPACITY': (OceanStorModel._parse_capacity, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'EXPOSEDTOINITIATOR': (OceanStorModel._parse_mapping, None),
        'WWN': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        total_luns = []
        count = self.cli.get_lun_count()

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            luns = self.cli.get_luns(i * 100, (i + 1) * 100)
            total_luns.extend(luns)

        return total_luns


class OceanStorFileSystem(OceanStorModel):
    relname = 'oceanStorFileSystems'
    modname = 'ZenPacks.community.OceanStor.OceanStorFileSystem'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'PARENTID': (OceanStorModel._parse_id, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ALLOCTYPE': (OceanStorModel._parse_alloc_type, None),
        'CAPACITY': (OceanStorModel._parse_capacity, None),
        'AVAILABLECAPCITY': (OceanStorModel._parse_capacity, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str, None),
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


class OceanStorSnapshot(OceanStorModel):
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
        'vstoreName': (OceanStorModel._parse_str, None),
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


class OceanStorFSSnapshot(OceanStorModel):
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


class OceanStorNFSShare(OceanStorModel):
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

    @classmethod
    def compname(cls, obj):
        return 'oceanStorFileSystems/' + obj['FSID']


class OceanStorCIFSShare(OceanStorModel):
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

        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            shares = self.cli.get_cifs_shares(i * 100, (i + 1) * 100)
            total_shares.extend(shares)

        return total_shares

    @classmethod
    def compname(cls, obj):
        return 'oceanStorFileSystems/' + obj['FSID']


class OceanStorQuotaTree(OceanStorModel):
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


class OceanStorEthPort(OceanStorModel):
    relname = 'oceanStorEthPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorEthPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'IPV4ADDR': (OceanStorModel._parse_str, None),
        'IPV4MASK': (OceanStorModel._parse_str, None),
        'IPV6ADDR': (OceanStorModel._parse_str, None),
        'IPV6MASK': (OceanStorModel._parse_str, None),
        'SPEED': (OceanStorModel._parse_str, None),
        'maxSpeed': (OceanStorModel._parse_str, None),
        'MTU': (OceanStorModel._parse_str, None),
        'BONDNAME': (OceanStorModel._parse_str, None),
        'PORTSWITCH': (OceanStorModel._parse_enable_disable, None),
        'numberOfInitiators': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_eth_ports()


class OceanStorFCPort(OceanStorModel):
    relname = 'oceanStorFCPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorFCPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'WWN': (OceanStorModel._parse_str, None),
        'RUNSPEED': (OceanStorModel._parse_str, None),
        'MAXSPEED': (OceanStorModel._parse_str, None),
        'FCRUNMODE': (OceanStorModel._parse_str, None),
        'PORTSWITCH': (OceanStorModel._parse_enable_disable, None),
        'numberOfInitiators': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_fc_ports()


class OceanStorFCoEPort(OceanStorModel):
    relname = 'oceanStorFCoEPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorFCoEPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'LOCATION': (OceanStorModel._parse_str, None),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'WWN': (OceanStorModel._parse_str, None),
        'RUNSPEED': (OceanStorModel._parse_str, None),
        'MAXSPEED': (OceanStorModel._parse_str, None),
        'PORTSWITCH': (OceanStorModel._parse_enable_disable, None),
        'numberOfInitiators': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_fcoe_ports()


class OceanStorBondPort(OceanStorModel):
    relname = 'oceanStorBondPorts'
    modname = 'ZenPacks.community.OceanStor.OceanStorBondPort'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'HEALTHSTATUS': (OceanStorModel._parse_health_status, None),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'MTU': (OceanStorModel._parse_str, None),
        'numberOfPorts': (OceanStorModel._parse_member_number_of_bond_port, None),
    }

    def get_data(self, __):
        return self.cli.get_bond_ports()


class OceanStorVLAN(OceanStorModel):
    relname = 'oceanStorVLANs'
    modname = 'ZenPacks.community.OceanStor.OceanStorVLAN'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'TAG': (OceanStorModel._parse_str, None),
        'MTU': (OceanStorModel._parse_str, None),
        'PORTTYPE': (OceanStorModel._parse_vlan_port_type, None),
        'PORTID': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_vlans()


class OceanStorLIF(OceanStorModel):
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
        'MANAGEMENTACCESS': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_lifs()


class OceanStorHost(OceanStorModel):
    relname = 'oceanStorHosts'
    modname = 'ZenPacks.community.OceanStor.OceanStorHost'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'NAME': (OceanStorModel._parse_str, 'title'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'OPERATIONSYSTEM': (OceanStorModel._parse_os, None),
        'IP': (OceanStorModel._parse_str, None),
        'INITIATORNUM': (OceanStorModel._parse_str, None),
        'vstoreName': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_hosts()


class OceanStorISCSIInitiator(OceanStorModel):
    relname = 'oceanStorISCSIInitiators'
    modname = 'ZenPacks.community.OceanStor.OceanStorISCSIInitiator'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ISFREE': (OceanStorModel._parse_initiator_free, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'USECHAP': (OceanStorModel._parse_yes_no, None),
        'MULTIPATHTYPE': (OceanStorModel._parse_multipath_type, None),
        'vstoreName': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_iscsi_initiators()


class OceanStorFCInitiator(OceanStorModel):
    relname = 'oceanStorFCInitiators'
    modname = 'ZenPacks.community.OceanStor.OceanStorFCInitiator'

    FIELD_PARSER = {
        'ID': (OceanStorModel._parse_id, 'id'),
        'RUNNINGSTATUS': (OceanStorModel._parse_running_status, None),
        'ISFREE': (OceanStorModel._parse_initiator_free, None),
        'PARENTNAME': (OceanStorModel._parse_str, None),
        'MULTIPATHTYPE': (OceanStorModel._parse_multipath_type, None),
        'vstoreName': (OceanStorModel._parse_str, None),
    }

    def get_data(self, __):
        return self.cli.get_fc_initiators()


class OceanStor(PythonPlugin):
    requiredProperties = (
        'zHWOceanStorControllers',
        'zHWOceanStorUser',
        'zHWOceanStorPassword',
        'zHWOceanStorIsLocalAuthentication',
        'zHWOceanStorDomainName',
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    DEVICE_MODELERS = OrderedDict(
        [
            ('OceanStorArray', OceanStorArray),
            ('OceanStorEnclosure', OceanStorEnclosure),
            ('OceanStorPower', OceanStorPower),
            ('OceanStorFan', OceanStorFan),
            ('OceanStorBBU', OceanStorBBU),
            ('OceanStorController', OceanStorController),
            ('OceanStorDiskDomain', OceanStorDiskDomain),
            ('OceanStorDisk', OceanStorDisk),
            ('OceanStorStoragePool', OceanStorStoragePool),
            ('OceanStorLUN', OceanStorLUN),
            ('OceanStorFileSystem', OceanStorFileSystem),
            ('OceanStorSnapshot', OceanStorSnapshot),
            ('OceanStorFSSnapshot', OceanStorFSSnapshot),
            ('OceanStorNFSShare', OceanStorNFSShare),
            ('OceanStorCIFSShare', OceanStorCIFSShare),
            ('OceanStorQuotaTree', OceanStorQuotaTree),
            ('OceanStorEthPort', OceanStorEthPort),
            ('OceanStorFCPort', OceanStorFCPort),
            ('OceanStorFCoEPort', OceanStorFCoEPort),
            ('OceanStorBondPort', OceanStorBondPort),
            ('OceanStorVLAN', OceanStorVLAN),
            ('OceanStorLIF', OceanStorLIF),
            ('OceanStorHost', OceanStorHost),
            ('OceanStorISCSIInitiator', OceanStorISCSIInitiator),
            ('OceanStorFCInitiator', OceanStorFCInitiator),
        ]
    )

    def getAuthInfo(self, device):
        ips = getattr(device, 'zHWOceanStorControllers', None)
        if not ips:
            raise Exception("zHWOceanStorControllers is required for %s." % device.id)

        user = getattr(device, 'zHWOceanStorUser', None)
        if not user:
            raise Exception("zHWOceanStorUser is required for %s." % device.id)

        password = getattr(device, 'zHWOceanStorPassword', None)
        if not password:
            raise Exception("zHWOceanStorPassword is required for %s." % device.id)

        local = getattr(device, 'zHWOceanStorIsLocalAuthentication', True)
        domain = getattr(device, 'zHWOceanStorDomainName', None)
        if not local and not domain:
            raise Exception("zHWOceanStorDomainName is required for domain authentication.")

        return ips, user, password, local, domain

    @inlineCallbacks
    def collect(self, device, __):
        log.info("Modeler %s collecting data for device %s",
                 self.name(), device.id)

        try:
            ips, user, password, local, domain = self.getAuthInfo(device)
        except Exception as e:
            log.error('Get auth info error: %s', e)
            returnValue(None)

        cli = client.RestClient(ips, user, password, local, domain)

        try:
            cli.login()
        except Exception as e:
            log.error('Login array failed: %s', e)
            returnValue(None)

        results = {}

        for model in self.DEVICE_MODELERS:
            log.info("Collecting model %s data", model)

            try:
                results[model] = yield self.DEVICE_MODELERS[model](cli).get_data(results)
            except Exception as e:
                log.error('Exception occurred while collecting model data: %s', e)
            else:
                log.info("Collect model %s data done", model)

        cli.logout()
        returnValue(results)

    def process(self, device, results, __):
        log.info("Modeler %s processing data for device %s",
                 self.name(), device.id)

        rm = []
        for model in self.DEVICE_MODELERS:
            if model not in results:
                continue

            cls = self.DEVICE_MODELERS[model]
            oms = cls.process_result(results[model])

            for compname in oms:
                rm.append(RelationshipMap(
                    relname=cls.relname,
                    compname=compname,
                    modname=cls.modname,
                    objmaps=oms[compname],
                ))

        return rm
