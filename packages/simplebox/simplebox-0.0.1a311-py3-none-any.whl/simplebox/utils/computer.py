#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import socket
from collections.abc import KeysView
from decimal import Decimal, ROUND_HALF_UP
from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
from typing import TypeVar, Union, Any

from psutil import *

from collections.abc import Callable
from ..converter import StorageUnit

P = TypeVar("P", bound=Union[Path, str])


class Network(object):
    """
    Network information
    """

    def __init__(self):
        self.__host__name: str = self.__get_host_name()
        self.__ip: str = self.__get_ip()
        self.__mac: str = self.__get_mac()
        self.__addresses: dict = net_if_addrs()
        self.__network_adapter_names: KeysView = self.__addresses.keys()

    @property
    def host_name(self) -> str:
        """
        get hostname
        """
        return self.__host__name

    @property
    def ip(self) -> str:
        """
        Get the IP address
        """
        return self.__ip

    @property
    def mac(self) -> str:
        """
        Get the MAC address
        Applies to a single NIC, if multiple NICs may be inconsistent with expectations
        """
        return self.__mac

    @property
    def network_adapter_names(self) -> list:
        """
        Gets the names of all network adapters
        """
        return list(self.__network_adapter_names)

    def mac_by_adapter_name(self, name: str) -> str:
        """
        Get the MAC by the name of the network adapter
        """
        return self.__get_mac_by_adapter_name(name)

    def mac_by_ipv4(self, ip: str) -> str:
        """
        When you have multiple network cards, you can obtain a MAC based on the IP address
        """
        return self.__get_mac_by_ip(ip)

    def macs_by_ipv4(self, ip_prefix: str) -> str:
        """
        When you have multiple network cards, you can obtain a MAC based on the IP address
        """
        return self.__get_mac_by_ip(ip_prefix, True)

    def ipv4_by_mac(self, mac: str) -> str:
        """
        When multi-NIC, you can obtain an IP address based on the MAC address
        """
        return self.__get_ip_by_mac(mac, "AF_INET")

    def ipv4s_by_mac(self, mac_prefix: str) -> str:
        """
        When multi-NIC, prefix IP according to MAC, return list
        """
        return self.__get_ip_by_mac(mac_prefix, "AF_INET", True)

    def ipv6_by_mac(self, mac: str) -> str:
        return self.__get_ip_by_mac(mac, "AF_INET6")

    def ipv6s_by_mac(self, mac_prefix: str) -> str:
        return self.__get_ip_by_mac(mac_prefix, "AF_INET6", True)

    def mac_by_ipv6(self, ip: str) -> str:
        """
        When you have multiple network cards, you can obtain a MAC based on the IP address
        """
        return self.__get_mac_by_ip(ip)

    def macs_by_ipv6(self, ip_prefix: str) -> str:
        """
        When you have multiple network cards, you can obtain a MAC based on the IP address
        """
        return self.__get_mac_by_ip(ip_prefix, True)

    def ipv4_by_adapter_name(self, name: str) -> str:
        """
        Get IPv4 by the name of the network adapter
        """
        return self.__get_ipv4_by_adapter_name(name)

    def ipv6_by_adapter_name(self, name: str) -> str:
        """
        Get IPv6 by the name of the network adapter
        """
        return self.__get_ipv6_by_adapter_name(name)

    def net4_to_ip4(self, ip: int) -> str:
        """
        number ip transformer to string.
        3232235521 => 192.168.0.1
        """
        return self.__net2ip(ip)

    def ip4_to_net4(self, ip: str) -> int:
        """
        string ip transformer to number.
        192.168.0.1 => 3232235521
        """
        return self.__ip2net(ip)

    def net6_to_ip6(self, ip: int, exploded: bool = True) -> str:
        """
        number ip transformer to string.
        if exploded:
            42540766429944781121676641069932943915 => 2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b
        else:
            42540766429944781121676641069932943915 => 2001:db8:3c4d:15::1a2f:1a2b
        """
        return self.__net2ip(ip, False, exploded)

    def ip6_to_net6(self, ip: str) -> int:
        """
        string ip transformer to number.
        2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b => 42540766429944781121676641069932943915
        """
        return self.__ip2net(ip, False)

    @staticmethod
    def __get_host_name() -> str:
        return socket.getfqdn(socket.gethostname())

    @staticmethod
    def __get_ip() -> str:
        return socket.gethostbyname(Network.__get_host_name())

    def __get_mac(self) -> str:
        return self.__get_mac_by_ip(self.ip)

    def __get_mac_by_adapter_name(self, name: str) -> str:
        return self.__get_ip_by_adapter_name_and_family(name, {'AF_LINK', 'AF_PACKET'})

    def __get_ipv4_by_adapter_name(self, name: str) -> str:
        return self.__get_ip_by_adapter_name_and_family(name, "AF_INET")

    def __get_ipv6_by_adapter_name(self, name: str) -> str:
        return self.__get_ip_by_adapter_name_and_family(name, "AF_INET6")

    @staticmethod
    def __get_ip_by_adapter_name_and_family(name: str, family: str or set) -> str:
        addresses = net_if_addrs()
        for adapter_ in addresses:
            if adapter_ == name:
                snic_list = addresses[name]
                for snic in snic_list:
                    if snic.family.name in family:
                        return snic.address

    @staticmethod
    def __get_mac_by_ip(ip: str, fuzzy: bool = False) -> str or list:
        snics = Network.__get_snic(
            lambda s, greedy: ((not greedy and s.address == ip) or (greedy and s.address.startswith(ip))), fuzzy)
        if not snics:
            return None
        if fuzzy:
            ips = []
            ips_append = ips.append
            for snic_list in snics:
                if snic_list:
                    for snic in snic_list:
                        if snic.family.name == "AF_LINK":
                            ips_append(snic.address)
            return ips
        else:
            for snic in snics:
                if snic.family.name == "AF_LINK":
                    return snic.address

    @staticmethod
    def __get_ip_by_mac(mac: str, family: str, fuzzy: bool = False) -> str or list:
        snics = Network.__get_snic(
            lambda s, greedy: ((not greedy and s.address == mac) or (greedy and s.address.startswith(mac))), fuzzy)
        if not snics:
            return None
        if fuzzy:
            ips = []
            ips_append = ips.append
            for snic_list in snics:
                if snic_list:
                    for snic in snic_list:
                        if snic.family.name == family:
                            ips_append(snic.address)
            return ips
        else:
            for snic in snics:
                if snic.family.name == family:
                    return snic.address

    @staticmethod
    def __get_snic(condition: Callable[[Any, bool], bool], greedy: bool = False) -> list:
        snics = []
        snics_append = snics.append
        addresses = net_if_addrs()
        for snic_list in addresses.values():
            for snic in snic_list:
                if condition(snic, greedy):
                    if greedy:
                        snics_append(snic_list)
                    else:
                        return snic_list
        if greedy:
            return snics

    @staticmethod
    def __net2ip(net: int, net4: bool = True, exploded: bool = True) -> str:
        if not issubclass(typ := type(net), int):
            raise TypeError(f"Expected type int, got a {typ}")
        if net4:
            return str(IPv4Address(net))
        else:
            net6 = IPv6Address(net)
            if exploded:
                return str(net6.exploded)
            else:
                return str(net6)

    @staticmethod
    def __ip2net(ip: str, net4: bool = True) -> int:
        if not issubclass(typ := type(ip), str):
            raise TypeError(f"Expected type str, got a {typ}")
        if net4:
            return int(IPv4Address(ip))
        else:
            return int(IPv6Address(ip))


class Cpu(object):
    """CPU information"""

    @property
    def count(self) -> int:
        """
        The number of physical CPUs
        """
        return cpu_count(False)

    @property
    def count_logical(self) -> int:
        """
        The number of logical CPUs
        """
        return cpu_count()

    def percent(self, interval: int = None) -> float:
        """
        Get the usage of each CPU
        :param interval: The time interval at which the data is fetched
        """
        return cpu_percent(interval, False)

    def percent_all(self, interval: int = None) -> float:
        """
        Gets the total CPU usage
        :param interval: The time interval at which the data is fetched
        """
        return cpu_percent(interval, True)

    def times(self) -> list:
        """
        获Get the usage of each CPU
        """
        return cpu_times(True)

    def times_all(self):
        """
        The total time it takes to get the CPU
        """
        return cpu_times(False)

    def times_percent(self, interval: int = None):
        """
        Get the percentage of total CPU time consumed
        :param interval: The time interval at which the data is fetched
        """
        return cpu_times_percent(interval, False)

    def times_percent_all(self, interval: int = None) -> list:
        """
        Get the proportion of time spent per CPU
        :param interval: The time interval at which the data is fetched
        """
        return cpu_times_percent(interval, True)

    def status(self):
        """
        Returns CPU statistics in the form of named tuples, including context switches, interrupts, soft interrupts,
        and system calls.
        """
        return cpu_stats()

    def freq(self):
        """
        Total CPU frequency
        """
        return cpu_freq(False)

    def freq_all(self) -> list:
        """
        The frequency of each CPU
        """
        return list(cpu_freq(True))


class Memory(object):

    @staticmethod
    def virtual():
        """
        Get virtual memory information
        """
        return virtual_memory()

    @staticmethod
    def swap():
        """
        Get the swap memory information
        """
        return swap_memory()


class Disk(object):

    def __init__(self, path: P = None):
        if path:
            self.__path: P = Path(path)
        else:
            self.__path: P = Path(os.sep)
        self.__partition = disk_usage(str(self.__path))

    def get_total(self, unit: StorageUnit = StorageUnit.BYTE, accuracy: int = 2) -> float:
        """
        Total
        """
        return StorageUnit.BYTE.of(self.__partition.total).to(unit).round(accuracy)

    def get_free(self, unit: StorageUnit = StorageUnit.BYTE, accuracy: int = 2) -> float:
        """
        Disk capacity remaining
        """
        return StorageUnit.BYTE.of(self.__partition.free).to(unit).round(accuracy)

    def get_used(self, unit: StorageUnit = StorageUnit.BYTE, accuracy: int = 2) -> float:
        """
        Used
        """
        return StorageUnit.BYTE.of(self.__partition.used).to(unit).round(accuracy)

    def get_used_percent(self, accuracy: int = 2) -> float:
        """
        Percentage of usage
        """
        return float(Decimal(self.__partition.percent).quantize(Decimal(f'0.{"0" * accuracy}'), rounding=ROUND_HALF_UP))

    def get_free_percent(self, accuracy: int = 2) -> float:
        """
        Percentage of free
        """
        return float(
            Decimal(100 - self.__partition.percent).quantize(Decimal(f'0.{"0" * accuracy}'), rounding=ROUND_HALF_UP))


class Process(object):
    def pids(self) -> list[int]:
        """
        Returns the currently running processes as a list
        """
        return pids()

    def pid_exists(self, pid: int) -> bool:
        """
        Determine whether the given PID exists
        """
        return pid_exists(pid)

    def process_iter(self, attrs: list[str] = None) -> list:
        """
        Iterates over the currently running process, returning the Process object for each process
        :param attrs: The process property can be filtered and is a list
        """
        return list(process_iter(attrs))

    def get_process(self, pid: int = None, pname: str = None) -> Process:
        """
        Get process information
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        for p in process_iter():
            if pid is not None and p.pid == pid:
                return p
            elif pname and p.name() == pname:
                return p

    def cmdline(self, pid: int = None, pname: str = None) -> list[str]:
        """
        Gets the command-line arguments that start the process
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.cmdline()

    def create_time(self, pid: int = None, pname: str = None) -> float:
        """
        Get the creation time of the process (timestamp format)
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.create_time()

    def num_fds(self, pid: int = None, pname: str = None) -> int:
        """
        The number of files open by the process
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.num_fds()

    def num_threads(self, pid: int = None, pname: str = None) -> int:
        """
        The number of child processes of the process
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.num_threads()

    def is_running(self, pid: int = None, pname: str = None) -> bool:
        """
        Determine if the process is running
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.is_running()

    def send_signal(self, pid: int = None, pname: str = None, kill_signal: int = 2):
        """
        Send signals to processes, similar to os.kill, etc
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        :param kill_signal: kill signal
        """
        p = self.get_process(pid, pname)
        if p:
            return p.send_signal(kill_signal)

    def kill(self, pid: int = None, pname: str = None):
        """
        Send a SIGKILL signal to end the process
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.send_signal(9)

    def terminate(self, pid: int = None, pname: str = None):
        """
        Send a SIGTEAM signal to end the process
        :param pid: When the process ID and pname exist at the same time, only pid takes effect
        :param pname: process's name
        """
        p = self.get_process(pid, pname)
        if p:
            return p.send_signal(15)


network = Network()
cpu = Cpu()
memory = Memory()
process = Process()

__all__ = [network, cpu, memory, Disk, process]
