import json
import logging
import requests
import six

log = logging.getLogger('zen.Storage.Huawei.OceanStor')

SOCKET_TIMEOUT = 50
PWD_EXPIRED_OR_INITIAL = (3, 4)
ERROR_CONNECT_TO_SERVER = -403
ERROR_UNAUTHORIZED_TO_SERVER = -401
HTTP_ERROR_NOT_FOUND = 404
NO_NEED_RELOGIN_ERROR = (1077949061, 1077939726, 1077949067, 1077987871, 1077949081, 1077949070, 1073793595)


class RestClient(object):
    def __init__(self, ips, username, password, local=True, domain=None):
        self.ips = ips
        self.username = username
        self.password = password
        self.local = local
        self.domain = domain

        self.url = None
        self.session = None

    def init_http_head(self):
        self.url = None
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
        })
        self.session.verify = False

    @staticmethod
    def _error_code(result):
        return result['error']['code']

    @staticmethod
    def _success(result):
        return result['error']['code'] == 0

    @staticmethod
    def _assert_result(result, msg):
        if not RestClient._success(result):
            msg = 'Error: %(err)s\nresult: %(res)s' % {
                'err': msg, 'res': result}
            log.error(msg)
            raise Exception(msg)

    def do_call(self, url, method, data=None):
        kwargs = {'timeout': SOCKET_TIMEOUT}

        if self.url:
            url = self.url + url

        if data:
            kwargs['data'] = json.dumps(data)

        func = getattr(self.session, method)

        try:
            resp = func(url, **kwargs)
        except Exception as e:
            log.error('Send request to %(url)s error: %(e)s',
                      {'url': url, 'e': e})
            return {"error": {"code": ERROR_CONNECT_TO_SERVER,
                              "description": six.text_type(e),
                              },
                    }

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error('HTTPError: %s', e)
            return {"error": {"code": e.response.status_code,
                              "description": six.text_type(e),
                              },
                    }

        result = resp.json()
        return result

    def call(self, url, method, data=None):
        result = self.do_call(url, method, data)
        if self._error_code(result) in (
                ERROR_CONNECT_TO_SERVER,
                ERROR_UNAUTHORIZED_TO_SERVER):
            try:
                self.login()
            except Exception as e:
                log.error('Relogin error: %s', e)
                return {"error": {"code": ERROR_CONNECT_TO_SERVER,
                                  "description": six.text_type(e),
                                  },
                        }

            result = self.do_call(url, method, data)

        return result

    def login(self):
        self.init_http_head()

        data = {"username": self.username,
                "password": self.password,
                "scope": "0"}

        if not self.local:
            log.info("Try to login as domain user.")
            data["scope"] = "1"
            data["domainName"] = self.domain

        for ip in self.ips:
            url = 'https://%s:8088/deviceManager/rest/xxxxx/sessions' % ip
            log.info("Try to login %s", url)

            result = self.do_call(url, "post", data)
            if self._error_code(result) in NO_NEED_RELOGIN_ERROR:
                msg = "Login %s error, error code %s" % (url, self._error_code(result))
                log.error(msg)
                raise Exception(msg)
            elif not self._success(result):
                continue

            log.info("Login %s success", url)

            self.url = 'https://%s:8088/deviceManager/rest/%s' % (ip, result['data']['deviceid'])
            self.session.headers['iBaseToken'] = result['data']['iBaseToken']

            if result['data']['accountstate'] in PWD_EXPIRED_OR_INITIAL:
                self.logout()

                msg = "Password is expired or initial, please change the password"
                log.error(msg)
                raise Exception(msg)
            else:
                self.ips.remove(ip)
                self.ips.append(ip)
                break
        else:
            msg = 'Failed to login %s' % self.ips
            log.error(msg)
            raise Exception(msg)

    def logout(self):
        result = self.do_call('/sessions', 'delete')
        if not self._success(result):
            log.warning("Failed to logout session from url %s, reason: %s.",
                        self.url, result)
        else:
            log.info("Logout %s success", self.url)

    def get_system(self):
        result = self.call("/system/", "get")
        self._assert_result(result, 'Get system info error.')
        return result['data']

    def get_alarms(self, start_range, end_range):
        url = "/alarm/currentalarm?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get current alarms error.')
        return result.get('data', [])

    def get_alarm_count(self):
        result = self.call("/alarm/currentalarm/count", "get")
        self._assert_result(result, 'Get current alarm count error.')
        return int(result['data']['COUNT'])

    def get_enclosures(self):
        result = self.call("/enclosure", "get")
        self._assert_result(result, 'Get enclosure info error.')
        return result.get('data', [])

    def get_powers(self):
        result = self.call("/power", "get")
        self._assert_result(result, 'Get power info error.')
        return result.get('data', [])

    def get_backup_powers(self):
        result = self.call("/backup_power", "get")
        self._assert_result(result, 'Get backup power info error.')
        return result.get('data', [])

    def get_controllers(self):
        result = self.call("/controller", "get")
        self._assert_result(result, 'Get controller info error.')
        return result.get('data', [])

    def get_diskdomains(self):
        result = self.call("/diskpool", "get")
        self._assert_result(result, 'Get disk domain info error.')
        return result.get('data', [])

    def get_disks(self):
        result = self.call("/disk", "get")
        self._assert_result(result, 'Get disk info error.')
        return result.get('data', [])

    def get_storage_pools(self):
        result = self.call("/storagepool", "get")
        self._assert_result(result, 'Get storage pools info error.')
        return result.get('data', [])

    def get_storage_pool_by_id(self, pool_id):
        url = "/storagepool/%s" % pool_id
        result = self.call(url, "get")
        self._assert_result(result, 'Get storage pool by id info error.')
        return result['data']

    def get_luns(self, start_range, end_range):
        url = "/lun?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get luns error.')
        return result.get('data', [])

    def get_lun_count(self):
        result = self.call("/lun/count", "get")
        self._assert_result(result, 'Get lun count error.')
        return int(result['data']['COUNT'])

    def get_fans(self):
        result = self.call("/fan", "get")
        self._assert_result(result, 'Get fans error.')
        return result.get('data', [])

    def get_filesystems(self, start_range, end_range):
        url = "/filesystem?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get filesystems error.')
        return result.get('data', [])

    def get_filesystem_count(self):
        result = self.call("/filesystem/count", "get")
        self._assert_result(result, 'Get filesystem count error.')
        return int(result['data']['COUNT'])

    def get_filesystem_by_id(self, fs_id):
        url = "/filesystem/%s" % fs_id
        result = self.call(url, "get")
        self._assert_result(result, 'Get filesystem error.')
        return result['data']

    def get_lun_snapshots(self, start_range, end_range):
        url = "/SNAPSHOT?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get SNAPSHOTs error.')
        return result.get('data', [])

    def get_lun_snapshot_count(self):
        result = self.call("/SNAPSHOT/count", "get")
        self._assert_result(result, 'Get SNAPSHOT count error.')
        return int(result['data']['COUNT'])

    def get_fs_snapshots(self, parent, start_range, end_range):
        url = "/FSSNAPSHOT?PARENTID=%s&range=[%d-%d]" % (parent, start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get FSSNAPSHOTs error.')
        return result.get('data', [])

    def get_fs_snapshot_count(self, parent):
        url = "/FSSNAPSHOT/count?PARENTID=%s" % parent
        result = self.call(url, "get")
        self._assert_result(result, 'Get FSSNAPSHOT count error.')
        return int(result['data']['COUNT'])

    def get_nfs_shares(self, start_range, end_range):
        url = "/NFSHARE?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get NFSHAREs error.')
        return result.get('data', [])

    def get_nfs_share_count(self):
        result = self.call("/NFSHARE/count", "get")
        self._assert_result(result, 'Get NFSHARE count error.')
        return int(result['data']['COUNT'])

    def get_cifs_shares(self, start_range, end_range):
        url = "/CIFSHARE?range=[%d-%d]" % (start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get CIFSHAREs error.')
        return result.get('data', [])

    def get_cifs_share_count(self):
        result = self.call("/CIFSHARE/count", "get")
        self._assert_result(result, 'Get CIFSHARE count error.')
        return int(result['data']['COUNT'])

    def get_quota_trees(self, parent, start_range, end_range):
        url = "/quotatree?PARENTTYPE=40&PARENTID=%s&range=[%d-%d]" % (parent, start_range, end_range)
        result = self.call(url, "get")
        self._assert_result(result, 'Get quotatrees error.')
        return result.get('data', [])

    def get_quota_tree_count(self, parent):
        url = "/quotatree/count?PARENTTYPE=40&PARENTID=%s" % parent
        result = self.call(url, "get")
        self._assert_result(result, 'Get quotatree count error.')
        return int(result['data']['COUNT'])

    def get_eth_ports(self):
        result = self.call("/eth_port", "get")
        self._assert_result(result, 'Get eth ports error.')
        return result.get('data', [])

    def get_fc_ports(self):
        result = self.call("/fc_port", "get")
        self._assert_result(result, 'Get fc ports error.')
        return result.get('data', [])

    def get_fcoe_ports(self):
        result = self.call("/fcoe_port", "get")
        self._assert_result(result, 'Get fcoe ports error.')
        return result.get('data', [])

    def get_bond_ports(self):
        result = self.call("/bond_port", "get")
        self._assert_result(result, 'Get bond ports error.')
        return result.get('data', [])

    def get_vlans(self):
        result = self.call("/vlan", "get")
        self._assert_result(result, 'Get vlans error.')
        return result.get('data', [])

    def get_lifs(self):
        result = self.call("/lif", "get")
        self._assert_result(result, 'Get lifs error.')
        return result.get('data', [])

    def get_hosts(self):
        result = self.call("/host", "get")
        self._assert_result(result, 'Get hosts error.')
        return result.get('data', [])

    def get_iscsi_initiators(self):
        result = self.call("/iscsi_initiator", "get")
        self._assert_result(result, 'Get iscsi initiators error.')
        return result.get('data', [])

    def get_fc_initiators(self):
        result = self.call("/fc_initiator", "get")
        self._assert_result(result, 'Get fc initiators error.')
        return result.get('data', [])

    def get_performance_data(self, object_type, object_id=None, indicators=None):
        url = "/performance_data?object_type=%s" % object_type
        if object_id:
            url += '&object_list=[%s]' % object_id
        if indicators:
            url += '&indicators=%s' % indicators

        result = self.call(url, "get")
        self._assert_result(result, 'Get performance data error.')
        return result.get('data', [])
