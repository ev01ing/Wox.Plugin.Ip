# coding:utf-8
import os
from ipaddress import ip_address

from wox import Wox, WoxAPI
import time
import traceback
import logging
import clipboard
import sys
import requests

from common import IPCache, is_ipv4, is_ipv6

if sys.version[0] == "2":
    reload(sys)
    sys.setdefaultencoding("utf-8")

LOG_FILE = "log.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_FILE,
                    filemode='a')


class Main(Wox):
    ip = None
    ipv6 = None
    filename = ".ip_cache.json"

    def query(self, key):
        results = []

        if not key:
            cache = IPCache(self.filename)
            ipv4, ipv6, timestamp = cache.ipv4, cache.ipv6, cache.timestamp
            # logging.info(ipv4, timestamp)
            # logging.info((ipv4 and ipv6 and int(time.time()) - timestamp < 60 * 2))
            if not (ipv4 and ipv6 and int(time.time()) - timestamp < 60 * 2):
                logging.info("get ipv4 and ipv6")
                ipv4 = self.get_ipv4()
                ipv6 = self.get_ipv6()

                cache.cache_ipv4(ipv4)
                cache.cache_ipv6(ipv6)
                cache.refresh_timestamp()
                cache.write()

            # logging.info(ip, ipv6)
            self._construct_result_with_copy(ipv4, "IPv4地址", [ipv4], results)
            self._construct_result_with_copy(ipv6, "IPv6地址", [ipv6], results)
            return results
        elif self.is_number(key):
            num = int(key)
            if 0 <= num <= 4294967295:
                try:
                    ip = self.int2ip(int(key))
                    self._construct_result_with_copy(ip, "from int", [ip], results)
                    return results
                except Exception:
                    logging.error(traceback.format_exc())
            elif num > 4294967295:
                pass

        elif is_ipv4(key):
            temp = self.ip2int(key)
            self._construct_result_with_copy(temp, "转换为int", [temp], results)
            return results
        elif is_ipv6(key):
            address = ip_address(key)
            compressed = address.compressed
            self._construct_result_with_copy(compressed, "压缩方式", [compressed], results)
            exploded = address.exploded
            self._construct_result_with_copy(exploded, "全展开0", [exploded], results)
            no_zero = exploded.replace(":", "")
            self._construct_result_with_copy(no_zero, "无冒号", [no_zero], results)
            return results

        self._construct_result_with_copy(u'格式非法 : "%s"' % key, u'tips: "%s"' % key, [key], results)
        return results

    def get_ipv6(self):
        res = self.request("https://v6.ip.zxinc.org/getip")
        return res.text

    def get_ipv4(self):
        res = self.request("https://v4.ip.zxinc.org/getip")
        return res.text

    def request(self, url):
        return requests.get(url)

    @classmethod
    def _construct_result_with_copy(cls, title, subtitle, parameters, results):
        results.append({
            "Title": title,
            "SubTitle": subtitle,
            # "IcoPath": "Images/pic.png",
            "JsonRPCAction": {
                "method": "copy_to_clip",
                "parameters": parameters,
                "dontHideAfterAction": False
            }
        })

    @staticmethod
    def is_number(key):
        try:
            int(key)
            return True
        except Exception:
            return False

    @staticmethod
    def ip2int(ip):
        ip_items = ip.split(".")
        ip_long = int(ip_items[0])
        ip_long = ip_long << 8 | int(ip_items[1])
        ip_long = ip_long << 8 | int(ip_items[2])
        ip_long = ip_long << 8 | int(ip_items[3])
        return ip_long

    @staticmethod
    def int2ip(ip_int):
        ip = "." + str(ip_int % 256)
        ip_int /= 256
        ip = "." + str(int(ip_int) % 256) + ip
        ip_int /= 256
        ip = "." + str(int(ip_int) % 256) + ip
        ip_int /= 256
        return str(int(ip_int)) + ip

    def copy_to_clip(self, text):
        clipboard.copy(text)


if __name__ == "__main__":
    Main()
