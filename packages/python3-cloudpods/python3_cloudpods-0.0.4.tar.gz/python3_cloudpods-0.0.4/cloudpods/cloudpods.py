import requests
import urllib3
import time
from log import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enter_and_leave_function(func):
    def wrapper(*args, **kwargs):
        if args:
            if kwargs:
                log.info(f"begin to run function {func.__name__},args is {args},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__},args is {args}")
        else:
            if kwargs:
                log.info(f"begin to run function {func.__name__},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__}")
        try:
            result = func(*args, **kwargs)
            log_str=f"finish run function {func.__name__},result type is {type(result)}, and result is {result}"
            log.info(log_str)
            return result
        except Exception as e:
            log.error(f"failed to run functon {func.__name__} error message is : {e}")
            raise e
    return wrapper


class CloudPods:
    def __init__(self,keystone_url,username,password):
        self.__keystone_url = keystone_url
        self.__username = username
        self.__password = password
        self.__session = self.__get_session()
        self.__endpoints = self.__get_endpoint()
        self.__compute_url = f"{self.__endpoints['region2']}/"

    @enter_and_leave_function
    def __get_session(self):
        session = requests.Session()
        headers = {
            "User-Agent": "yunioncloud-go/201708"
        }
        session.headers.update(headers)
        get_token_url = "/auth/tokens"
        url = self.__keystone_url + get_token_url
        data = {
            "auth": {
                "context": {
                    "source": "cli"
                },
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": self.__username,
                            "password": self.__password
                        }
                    }
                },
                "scope": {
                    "project": {
                        "domain": {
                            "name": "default"
                        },
                        "name": "system"
                    }
                }
            }
        }
        try:
            rs = session.post(url=url, json=data, verify=False, timeout=600)
            if rs.status_code != 200:
                log.error(f"Failed to get /auth/tokens: Error. err msg is {str(rs.text)}")
                return None
            token = rs.headers["X-Subject-Token"]
            log.info(f"Get /auth/tokens success. token is {token}")
            headers['X-Auth-Token'] = token
            session.headers.update(headers)
            return session
        except Exception as e:
            log.error(f"Failed to get /auth/tokens: Error. err msg is {str(e)}", exc_info=True)
            return None

    @enter_and_leave_function
    def __get_endpoint(self):
        try:
            get_endpoints_url = "/endpoints"
            url = self.__keystone_url + get_endpoints_url
            rs = self.__session.get(url=url, verify=False, timeout=600)
            if rs.status_code != 200:
                log.error(f"Failed to get /endpoints: Error. err msg is {str(rs.text)}")
                return None
            rs_data = rs.json()
            endpoints=dict({})
            for elem in rs_data["endpoints"]:
                if elem["service_name"] not in endpoints.keys():
                    endpoints[elem["service_name"]]=elem["url"]
            return endpoints
        except Exception as e:
            log.error(f"Failed to get /endpoints: Error. err msg is {str(e)}", exc_info=True)

    @enter_and_leave_function
    def __create_server(self, server, count=1):
        try:
            create_server_url = "/servers"
            url = self.__compute_url + create_server_url
            data = {
                "count": count,
                "server": server
            }
            rs = self.__session.post(url=url, json=data, verify=False, timeout=600)
            if rs.status_code != 201:
                log.error(f"Failed to create server: Error. err msg is {str(rs.text)}")
                return None
            return rs.json()
        except Exception as e:
            log.error(f"Failed to create server: Error. err msg is {str(e)}",exc_info=True)
            return None

    @enter_and_leave_function
    def create_server_by_guest_image(self,guest_image_id,disk_image_id,arch, disk_size, disks, nets_list, vm_name, sku,count=1,reset_new_password=""):
        if arch == "x86_64":
            bios="BIOS"
        else:
            bios="UEFI"
        nets=[]
        for net in nets_list:
            nets.append({"network": net})
        server = {
            "auto_start": True,
            "generate_name": vm_name,
            "disable_delete": False,
            "__count__": 1,
            "disks": [{"disk_type": "sys", "index": 0, "backend": "local", "size": disk_size, "image_id": disk_image_id,
                       "medium": "ssd"}],
            "sku": sku,
            "reset_password": False,
            "guest_image_id": guest_image_id,
            "deploy_telegraf": True,
            "os_arch": arch,
            "nets": nets,
            "bios": bios
        }
        if reset_new_password:
            server["password"]=reset_new_password
        for i in range(len(disks)):
            disk = dict({})
            disk["disk_type"] = "data"
            disk["index"] = i + 1
            disk["backend"] = "local"
            disk["size"] = int(disks[i]) * 1024
            disk["medium"] = "ssd"
            server["disks"].append(disk)
        res = self.__create_server(server,count)
        server_ids=[]
        if "server" in res.keys() and "id" in res["server"].keys():
            server_ids.append(res["server"]["id"])
            return server_ids
        elif "servers" in res.keys():
            for elem in res["servers"]:
                server_ids.append(elem["body"]["id"])
            return server_ids
        else:
            return server_ids

    @enter_and_leave_function
    def get_server_detail(self, server_id):
        res_data={}
        try:
            get_all_snapshots = f"/servers/{server_id}"
            url = self.__compute_url + get_all_snapshots
            res = self.__session.get(url=url, verify=False, timeout=600)
            res_data = res.json()
            log.info(f"Success to request /servers/{server_id}: OK. response data is {res_data}")
        except Exception as e:
            log.error(f"Failed to request /servers/{server_id}: Error.\rerr msg is {str(e)}",exc_info=True)
        finally:
            return res_data

    @enter_and_leave_function
    def get_server_ip(self, server_id):
        server = self.get_server_detail(server_id)
        if "server" not in server.keys():
            log.error(f"failed get server info by server name {server_id}, server info is {server}.")
            return None
        if "nics" not in server["server"].keys():
            log.error(f"nics not in server['server'], server['server'] is {server['server']}")
            return None
        if len(server["server"]["nics"])<1:
            log.error(f"server['server']['nics'] has no elem, its length is 0")
            return None
        if "ip_addr" not in server["server"]["nics"][0].keys():
            log.error(f"ip_addr do not in server['server']['nics'][0], server['server']['nics'][0] is {server['server']['nics'][0]}")
            return None
        return server["server"]["nics"][0]["ip_addr"]

    @enter_and_leave_function
    def wait_for_server_is_on(self, server_id,timeout=1800):
        time_cost=0
        running_status_count = 0
        while True:
            if time_cost>=timeout:
                log.error(f"Timeout Error: {timeout} seconds passed but server still not online: Error.")
                return False
            server_detail = self.get_server_detail(server_id)
            if "server" in server_detail.keys() and "status" in server_detail["server"].keys():
                if server_detail["server"]["status"] == "disk_fail":
                    return False
                if server_detail["server"]["status"] == "deploy_fail":
                    return False
                if server_detail["server"]["status"] == "ready":
                    return False
                if "_fail" in server_detail["server"]["status"]:
                    return False
                if server_detail["server"]["status"] == "running":
                    running_status_count += 1
                    if running_status_count > 5:
                        return True
                    else:
                        time.sleep(1)
                        time_cost+=1
                        continue
                else:
                    running_status_count = 0
                time.sleep(5)
                time_cost+=5
            else:
                log.error(f"Failed to get server_detail: Error. server_detail is: {server_detail}")
                return False

    @enter_and_leave_function
    def delete_server(self, server_id):
        try:
            delete_server_url = f"/servers/{server_id}"
            url = self.__compute_url + delete_server_url
            params = {
                "OverridePendingDelete": True
            }
            rs = self.__session.delete(url=url,params=params, verify=False, timeout=600)
            if rs.status_code == 200:
                return True
            else:
                log.error(f"Failed to delete server {server_id}: Error.\nresponse msg is {rs.text}")
                return False
        except Exception as e:
            log.error(f"Failed to delete server {server_id}: Error.\nerr msg is {str(e)}",exc_info=True)


if __name__ == '__main__':
    cloudpods = CloudPods('https://10.30.18.1:30500/v3','admin','jSj@2008')
    server_ip = cloudpods.get_server_ip("e3b76ec7-c4f9-4065-8ce2-9d833b51368c")
    print(server_ip)