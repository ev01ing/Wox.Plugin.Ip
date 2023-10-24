"""
Create time: 2023/10/23 21:12

Author: ev01ing
"""
import json
import os
import time


def is_ipv4(value):
    groups = value.split('.')
    if len(groups) != 4 or any(not x.isdigit() for x in groups):
        return False
    return all(0 <= int(part) < 256 for part in groups)


def is_ipv6(value):
    ipv6_groups = value.split(':')
    if len(ipv6_groups) == 1:
        return False
    ipv4_groups = ipv6_groups[-1].split('.')

    if len(ipv4_groups) > 1:
        if not is_ipv4(ipv6_groups[-1]):
            return False
        ipv6_groups = ipv6_groups[:-1]
    else:
        ipv4_groups = []

    max_groups = 6 if ipv4_groups else 8
    if len(ipv6_groups) > max_groups:
        return False

    count_blank = 0
    for part in ipv6_groups:
        if not part:
            count_blank += 1
            continue
        try:
            num = int(part, 16)
        except ValueError:
            return False
        else:
            if not 0 <= num <= 65536:
                return False

    if count_blank < 2:
        return True
    elif count_blank == 2 and not ipv6_groups[0] and not ipv6_groups[1]:
        return True
    return False

    # return validators.ipv6(value)


class IPCache():

    def __init__(self, filename):
        self.filename = filename

        self.ipv4 = None
        self.ipv6 = None
        self.timestamp = None

        if os.path.exists(self.filename):
            self.ipv4, self.ipv6, self.timestamp = self.load()

    def cache_ipv4(self, ipv4):
        self.ipv4 = ipv4

    def cache_ipv6(self, ipv6):
        self.ipv6 = ipv6

    def refresh_timestamp(self):
        self.timestamp = int(time.time())

    def write(self):
        info = {"ipv4": self.ipv4, "ipv6": self.ipv6, "timestamp": self.timestamp}
        json.dump(info, open(self.filename, "w"))

    def load(self):
        try:
            info = json.load(open(self.filename))
            return info.get("ipv4", None), info.get("ipv6", None), info.get("timestamp", None)
        except:
            return None, None, int(time.time())
