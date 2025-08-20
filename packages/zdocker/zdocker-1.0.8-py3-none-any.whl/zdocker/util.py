#!/usr/bin/env python3

import hashlib
import os
import shutil
import socket
import ipaddress
from serial.tools import list_ports
import subprocess
import psutil
import logging
import signal as Signal
import sys
import errno

from http.client import HTTPConnection


logger = logging.getLogger("zbuild")


def toint(x) -> int:
    if isinstance(x, int):
        return x
    res = 0
    x = x.lower()
    if x.find('g') > 0:
        res = int(x[0:x.find('g')], 0) * 1024 * 1024 * 1024
    elif x.find('m') > 0:
        res = int(x[0:x.find('m')], 0) * 1024 * 1024
    elif x.find('k') > 0:
        res = int(x[0:x.find('k')], 0) * 1024
    else:
        res = int(x, 0)
    return res


def bytes_to_human(n, digit=1, space=0):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.*f%s%s' % (digit, value, ' ' * space, s)
    return '%s%sB' % (n, ' ' * space)


def probe_serial_device(port):
    if port is None:
        port_list = list(list_ports.comports())
        for i in port_list:
            if i.hwid != 'n/a':
                port = i.device
                break
    return port


def get_enternet_ip(ifname: str):
    try:
        ifname_netmask = ifname.split(":")
        if len(ifname_netmask) == 2:
            ipaddress.ip_address(ifname_netmask[0])
            ip = psutil._common.snicaddr(family=socket.AF_INET,
                                         address=ifname_netmask[0],
                                         netmask=ifname_netmask[1],
                                         broadcast=None, ptp=None)
            return ip, ifname_netmask
    except Exception:
        pass

    if_stat = psutil.net_if_stats()
    found = False
    for en, info in psutil.net_if_addrs().items():
        found = en == ifname or info[0].address == ifname
        # print(en, info[0].address)
        if ifname is None and if_stat[en].isup and (if_stat[en].duplex == psutil.NIC_DUPLEX_FULL and if_stat[en].speed != 0):
            found = True
        if found:
            if info[0].family == socket.AF_INET and (en[:2] != 'lo' or info[0].address != '127.0.0.1'):
                return info[0], en
    return None, None


def in_docker():
    return os.path.exists("/.dockerenv")


def has_docker():
    return shutil.which("docker")


def kill_proc(*args):
    """kill process"""
    for proc_name in args:
        for proc in psutil.process_iter(["name", "cmdline"]):
            if proc.name() == proc_name:
                if proc.status() == "zombie":
                    logger.warning(f"process: {proc} in zombie status, skip kill!")
                else:
                    proc.kill()


def subprocess_terminate(process: subprocess.Popen):
    """
    Terminate subforcess in correct way
    :param process: subprocess to be terminated
    """
    process.terminate()
    process.wait()
    try:
        os.killpg(process.pid, Signal.SIGTERM)
    except ProcessLookupError:
        logger.debug("Subprocess already killed.")


def subprocess_execute(command,
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       wait_return=True, timeout=None):
    process = subprocess.Popen(
        command,
        shell=True, close_fds=True,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        preexec_fn=os.setsid,
    )
    status = -1
    result = None
    if wait_return:
        try:
            result = process.communicate(timeout=timeout)
        except Exception as err:
            status = False
        process.terminate()
        status = process.returncode
    else:
        result = process
    return status, result


class ctext:
    R = "22;31"
    G = "22;32"
    Y = "22;33"
    B = "22;34"
    M = "22;35"
    CYAN = "22;36"
    LR = "01;31"
    LG = "01;32"
    LY = "01;33"
    LB = "01;34"
    LM = "01;35"

    @staticmethod
    def fmt(color, text):
        return f"\033[{color}m{text}\033[0m"


def http_download(server, filename):
    data = None
    conn = HTTPConnection(server[0], server[1], 60)

    conn.connect()
    conn.request("GET", "/" + filename)
    res = conn.getresponse()
    if res.status == 200:
        data = res.read()
    conn.close()
    return data


def hostname():
    return socket.gethostname().split('.')[0]


def generate_ethaddr(name):
    if not isinstance(name, bytes):
        name = name.encode()
    hash_object = hashlib.sha1(name)
    mac_raw = hash_object.hexdigest()[:8]
    return "48:da:" + ":".join([mac_raw[i:i+2] for i in range(0, len(mac_raw), 2)])


def sudo(func):
    def wrapper(*args, **kwargs):
        child_pid = os.fork()
        if child_pid == 0:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Failed to execute with sudo: {e}", file=sys.stderr)
                os._exit(1)

        _, status = os.waitpid(child_pid, 0)
        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
            if exit_code != 0:
                raise RuntimeError(f"Command failed with exit code {exit_code}")
            return None

        raise RuntimeError("Child process did not exit normally")

    return wrapper


def sudo_system(command: str):
    """执行需要 sudo 的命令"""
    pid = os.fork()

    if pid == 0:
        try:
            os.setuid(0)
            ret = os.system(command)
            os._exit(ret)
        except Exception:
            os._exit(1)
    else:
        _, status = os.waitpid(pid, 0)

        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
            if exit_code != 0:
                raise subprocess.CalledProcessError(exit_code, command)
            return exit_code == 0
        else:
            raise RuntimeError("Child process did not exit normally")


def load(path, binary=False, encoding="utf-8"):
    """ Loads a file content """
    with open(path, 'rb') as handle:
        tmp = handle.read()
        return tmp.decode(encoding)


def to_file_bytes(content, encoding="utf-8"):
    if not isinstance(content, bytes):
        content = bytes(content, encoding)
    return content


def save(path, content, only_if_modified=False, encoding="utf-8"):
    """
    Saves a file with given content
    Params:
        path: path to write file to
        content: contents to save in the file
        only_if_modified: file won't be modified if the content hasn't changed
        encoding: target file text encoding
    """
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as error:
            if error.errno not in (errno.EEXIST, errno.ENOENT):
                raise OSError("The folder {} does not exist and could not be created ({})."
                              .format(dir_path, error.strerror))
        except Exception:
            raise

    new_content = to_file_bytes(content, encoding)

    if only_if_modified and os.path.exists(path):
        old_content = load(path, binary=True, encoding=encoding)
        if old_content == new_content:
            return

    with open(path, "wb") as handle:
        handle.write(new_content)


def save_if_not_exists(path, content):
    if not os.path.exists(path):
        save(path, content)
