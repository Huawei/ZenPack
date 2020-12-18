from HTMLParser import HTMLParser
from twisted.internet.defer import inlineCallbacks, returnValue
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSourcePlugin,
)
from ZenPacks.community.OceanStor.lib import client
import math
import logging

log = logging.getLogger('zen.Storage.Huawei.OceanStor')


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
        'FILE_READ_BANDWIDTH': 770,
        'FILE_WRITE_BANDWIDTH': 771,
        'CONTROLLER_FILE_OPS': 476
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
        for_range = int(math.ceil(float(count) / 100))
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
