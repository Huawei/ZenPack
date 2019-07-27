import logging
log = logging.getLogger('zen.Storage.Huawei.OceanStor')

from HTMLParser import HTMLParser
import math
from twisted.internet.defer import inlineCallbacks, returnValue

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSourcePlugin,
)

from ZenPacks.community.OceanStor.lib import client
from ZenPacks.community.OceanStor.lib import utils


class OceanStorDS(PythonDataSourcePlugin):
    PERFORMANCE_OBJECT = None
    PERFORMANCE_DATA_POINTS = ()
    PERFORMANCE_INDICATOR = {
        'BLOCK_BANDWIDTH': 21,
        'TOTAL_IOPS': 22,
        'READ_BANDWIDTH': 23,
        'READ_IOPS': 25,
        'WRITE_BANDWIDTH': 26,
        'WRITE_IOPS': 28,
        'AVG_CPU_USAGE': 68,
        'OPS': 182,
        'READ_OPS': 232,
        'WRITE_OPS': 233,
        'AVG_IO_RESPONSE_TIME': 370,
        'AVG_READ_OPS_RESPONSE_TIME': 524,
        'AVG_WRITE_OPS_RESPONSE_TIME': 525,
        'FILE_BANDWIDTH': 511,
    }

    def __init__(self):
        self.cli = None

    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            context.id,
            datasource.plugin_classname,
        )

    @classmethod
    def params(cls, datasource, context):
        return {
            'ips': context.zHWOceanStorControllers,
            'user': context.zHWOceanStorUser,
            'password': context.zHWOceanStorPassword,
            'local': context.zHWOceanStorIsLocalAuthentication,
            'domain': context.zHWOceanStorDomainName,
        }

    @classmethod
    def _get_component(cls, objs, component, id_key):
        for i in objs:
            if component == prepId(i[id_key]):
                return i

        return None

    def init_client(self, config):
        ips = config.datasources[0].params['ips']
        if not ips:
            raise Exception("zHWOceanStorControllers is required for %s." % config.id)

        user = config.datasources[0].params['user']
        if not user:
            raise Exception("zHWOceanStorUser is required for %s." % config.id)

        password = config.datasources[0].params['password']
        if not password:
            raise Exception("zHWOceanStorPassword is required for %s." % config.id)

        local = config.datasources[0].params['local']
        domain = config.datasources[0].params['domain']
        if not local and not domain:
            raise Exception("zHWOceanStorDomainName is required for domain authentication.")

        self.cli = client.RestClient(ips, user, password, local, domain)
        self.cli.login()

    def release_client(self):
        self.cli.logout()

    @property
    def client(self):
        return self.cli

    @inlineCallbacks
    def collect(self, config):
        data = self.new_data()

        try:
            self.init_client(config)
        except Exception as e:
            log.error('Login array failed: %s', e)
            returnValue(None)

        try:
            collected = yield self._get_data(config)
        except Exception as e:
            log.error('Collect datasource %s failed: %s', config, e)
            returnValue(None)
        finally:
            self.release_client()

        log.info('Collected data %s', collected)
        data.update(collected)
        returnValue(data)

    def _get_performance_data(self, datasource):
        data = {}

        performance_datas = self.client.get_performance_data(self.PERFORMANCE_OBJECT, datasource.component)
        if len(performance_datas) <= 0:
            return None

        performance_data = performance_datas[0]

        for datapoint_id in self.PERFORMANCE_DATA_POINTS:
            indicator = self.PERFORMANCE_INDICATOR[datapoint_id]
            if indicator not in performance_data.get('indicators', []):
                continue

            index = performance_data['indicators'].index(indicator)
            value = performance_data['indicator_values'][index]

            dpname = '_'.join((datasource.datasource, datapoint_id))
            data[dpname] = (value, 'N')

        return data


class Alarms(OceanStorDS):
    severity_map = {
        3: 3,
        5: 4,
        6: 5,
    }

    def __init__(self):
        super(Alarms, self).__init__()
        self.parser = HTMLParser()

    def _get_data(self, config):
        total_alarms = []

        count = self.client.get_alarm_count()
        for_range = int(math.ceil(float(count)/100))
        for i in range(for_range):
            alarms = self.client.get_alarms(i * 100, (i + 1) * 100)
            for alarm in alarms:
                if alarm['alarmStatus'] == 1:
                    severity = self.severity_map.get(alarm['level'], 2)
                else:
                    severity = 0

                total_alarms.append(
                    {
                        'device': config.id,
                        'severity': severity,
                        'eventKey': "huawei-oceanstor-event-%s-%s" % (alarm['eventID'], alarm['sequence']),
                        'eventClassKey': 'huawei-oceanstor-event',
                        'summary': self.parser.unescape(alarm['description']),
                        'message': 'Details: %s\nSuggestion: %s' % (
                            self.parser.unescape(alarm['detail']),
                            self.parser.unescape(alarm['suggestion'])),
                    }
                )

        return {'events': total_alarms}


class Array(OceanStorDS):
    def _get_data(self, config):
        om_data = []
        dp_data = {}
        system = self.client.get_system()

        for datasource in config.datasources:
            om_data.append(
                ObjectMap({
                    'relname': 'oceanStorArrays',
                    'modname': 'ZenPacks.community.OceanStor.OceanStorArray',
                    'id': datasource.component,
                    'TOTALCAPACITY': utils.convert_capacity(system['TOTALCAPACITY']),
                    'USEDCAPACITY': utils.convert_capacity(system['USEDCAPACITY']),
                    'STORAGEPOOLCAPACITY': utils.convert_capacity(system['STORAGEPOOLCAPACITY']),
                    'STORAGEPOOLFREECAPACITY': utils.convert_capacity(system['STORAGEPOOLFREECAPACITY']),
                })
            )

            dp_data[datasource.component] = {}

            dpname = '_'.join((datasource.datasource, 'SYSTEM_CAPACITY_USAGE'))
            value = float(system['USEDCAPACITY']) * 100 / float(system['TOTALCAPACITY'])
            dp_data[datasource.component][dpname] = (value, 'N')

            dpname = '_'.join((datasource.datasource, 'STORAGE_POOLS_CAPACITY_USAGE'))
            value = float(system['STORAGEPOOLUSEDCAPACITY']) * 100 / float(system['STORAGEPOOLCAPACITY'])
            dp_data[datasource.component][dpname] = (value, 'N')

        return {'maps': om_data,
                'values': dp_data}


class Enclosure(OceanStorDS):
    def _get_data(self, config):
        data = {}
        enclosures = self.client.get_enclosures()

        for datasource in config.datasources:
            log.info('Collecting component %s.%s', datasource.datasource, datasource.component)

            enclosure = self._get_component(enclosures, datasource.component, 'ID')
            if not enclosure:
                continue

            dpname = '_'.join((datasource.datasource, 'TEMPERATURE'))
            data[datasource.component] = {
                dpname: (enclosure.get('TEMPERATURE', 0), 'N'),
            }

            log.info('Collected component %s.%s data: %s',
                     datasource.datasource, datasource.component, data[datasource.component])

        return {'values': data}


class Controller(OceanStorDS):
    def _get_controller_data(self, controllers, datasource):
        controller = self._get_component(controllers, datasource.component, 'ID')
        if not controller:
            return None

        data = {}
        for datapoint_id in ('CPUUSAGE', 'MEMORYUSAGE'):
            dpname = '_'.join((datasource.datasource, datapoint_id))
            data[dpname] = (controller.get(datapoint_id, 0), 'N')

        return data

    def _get_performance_data(self, performance_datas, datasource):
        performance_data = self._get_component(performance_datas, datasource.component, 'object_id')
        if not performance_data:
            return None

        data = {}
        for datapoint_id in ('BLOCK_BANDWIDTH', 'TOTAL_IOPS'):
            indicator = self.PERFORMANCE_INDICATOR[datapoint_id]
            if indicator not in performance_data.get('indicators', []):
                continue

            index = performance_data['indicators'].index(indicator)
            value = performance_data['indicator_values'][index]

            dpname = '_'.join((datasource.datasource, datapoint_id))
            data[dpname] = (value, 'N')

        return data

    def _get_data(self, config):
        data = {}

        controllers = self.client.get_controllers()
        performance_datas = self.client.get_performance_data('207')

        for datasource in config.datasources:
            log.info('Collecting component %s.%s', datasource.datasource, datasource.component)

            data[datasource.component] = {}

            controller_data = self._get_controller_data(controllers, datasource)
            if controller_data:
                data[datasource.component].update(controller_data)

            performance_data = self._get_performance_data(performance_datas, datasource)
            if performance_data:
                data[datasource.component].update(performance_data)

            log.info('Collected component %s.%s data: %s',
                     datasource.datasource, datasource.component, data[datasource.component])

        return {'values': data}


class LUN(OceanStorDS):
    PERFORMANCE_OBJECT = '11'
    PERFORMANCE_DATA_POINTS = ('BLOCK_BANDWIDTH', 'TOTAL_IOPS', 'READ_BANDWIDTH', 'READ_IOPS',
                               'WRITE_BANDWIDTH', 'WRITE_IOPS')

    def _get_data(self, config):
        data = {}

        for datasource in config.datasources:
            log.info('Collecting component %s.%s', datasource.datasource, datasource.component)

            data[datasource.component] = {}

            try:
                performance_data = self._get_performance_data(datasource)
            except Exception as e:
                log.error('Collect component %s.%s failed: %s', datasource.datasource, datasource.component, e)
                continue

            if performance_data:
                data[datasource.component].update(performance_data)

            log.info('Collected component %s.%s data: %s',
                     datasource.datasource, datasource.component, data[datasource.component])

        return {'values': data}


class FileSystem(OceanStorDS):
    PERFORMANCE_OBJECT = '40'
    PERFORMANCE_DATA_POINTS = ('OPS', 'READ_OPS', 'WRITE_OPS',
                               'AVG_READ_OPS_RESPONSE_TIME', 'AVG_WRITE_OPS_RESPONSE_TIME')

    def _get_filesystem_data(self, datasource):
        filesystem = self.client.get_filesystem_by_id(datasource.component)

        data = {}
        for datapoint_id in ('INODE_USED_COUNT',):
            dpname = '_'.join((datasource.datasource, datapoint_id))
            data[dpname] = (filesystem.get('inodeUsedCount', 0), 'N')

        return data

    def _get_data(self, config):
        data = {}

        for datasource in config.datasources:
            log.info('Collecting component %s.%s', datasource.datasource, datasource.component)

            data[datasource.component] = {}

            try:
                filesystem_data = self._get_filesystem_data(datasource)
                performance_data = self._get_performance_data(datasource)
            except Exception as e:
                log.error('Collect component %s.%s failed: %s', datasource.datasource, datasource.component, e)
                continue

            if filesystem_data:
                data[datasource.component].update(filesystem_data)
            if performance_data:
                data[datasource.component].update(performance_data)

            log.info('Collected component %s.%s data: %s',
                     datasource.datasource, datasource.component, data[datasource.component])

        return {'values': data}


class StoragePool(OceanStorDS):
    PERFORMANCE_OBJECT = '216'
    PERFORMANCE_DATA_POINTS = ('BLOCK_BANDWIDTH', 'TOTAL_IOPS', 'READ_BANDWIDTH', 'READ_IOPS',
                               'WRITE_BANDWIDTH', 'WRITE_IOPS', 'AVG_IO_RESPONSE_TIME')

    def _get_storage_pool_data(self, datasource):
        pool = self.client.get_storage_pool_by_id(datasource.component)

        data = {}
        for datapoint_id in ('USERCONSUMEDCAPACITYPERCENTAGE',):
            dpname = '_'.join((datasource.datasource, datapoint_id))
            data[dpname] = (pool.get(datapoint_id, 0), 'N')

        return data

    def _get_data(self, config):
        data = {}

        for datasource in config.datasources:
            log.info('Collecting component %s.%s', datasource.datasource, datasource.component)

            data[datasource.component] = {}

            try:
                pool_data = self._get_storage_pool_data(datasource)
                performance_data = self._get_performance_data(datasource)
            except Exception as e:
                log.error('Collect component %s.%s failed: %s', datasource.datasource, datasource.component, e)
                continue

            if pool_data:
                data[datasource.component].update(pool_data)
            if performance_data:
                data[datasource.component].update(performance_data)

            log.info('Collected component %s.%s data: %s',
                     datasource.datasource, datasource.component, data[datasource.component])

        return {'values': data}
