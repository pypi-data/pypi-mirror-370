import argparse
import os
import pathlib
import sys
import struct
import time
import zlib
import ctypes

import serial
import serial.tools.list_ports as list_ports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


DEFAULT_TIMEOUT = 3      # timeout for most flash operations
MAX_TIMEOUT = 300        # longest any command can run

# errorcode
PROTOCOL_RESULT_SUCCESS = 0x01
PROTOCOL_RESULT_WRONG_COMMAND = 0xFD
PROTOCOL_RESULT_UNKNOWN_ERROR = 0xFE
PROTOCOL_RESULT_UNDEFINE_COMMAND = 0xFF

# command
CMD_GET_VERSION = 0x01
CMD_GET_DEVICE_ID = 0x0B
CMD_CONNECT = 0x10
CMD_GET_MEMORY_INFO = 0x11
CMD_INIT_DOWNLOAD_NSEC = 0x12
CMD_DOWNLOAD_DATA_NSEC = 0x13
CMD_GET_CRYPTO_METHOD = 0x14
CMD_VERIFY_DATA = 0x15
CMD_UPLOAD_DATA_NSEC = 0x16
CMD_RUN_IMAGE = 0x18
# new
CMD_RUN_IMAGE_PRO = 0x22
CMD_INIT_DOWNLOAD_NSEC_PRO = 0x23
CMD_SET_REGISTER_VAL = 0x24
CMD_GET_REGISTER_VAL = 0x25
CMD_DO_REBOOT = 0x26


def print_overwrite(message, last_line=False):
    if sys.stdout.isatty():
        print("\r%s" % message, end='\n' if last_line else '')
        sys.stdout.flush()
    else:
        print(message)


class UnsupportedCommandError(RuntimeError):
    """
    Wrapper class for when ROM loader returns an invalid command response.
    Usually this indicates the loader is running in Secure Download Mode.
    """
    def __init__(self, cct, op):
        msg = "Invalid (unsupported) command 0x%x" % op
        RuntimeError.__init__(self, msg)


def to_size(size):
    if size < 1024:
        return '{}'.format(size)
    elif size < 1024 * 1024:
        return '%6.1fKB' % (size / 1024)
    elif size < 1024 * 1024 * 1024:
        return '%6.1fMB' % (size / 1024 / 1024)
    elif size < 1024 * 1024 * 1024 * 1024:
        return '%6.1fGB' % (size / 1024 / 1024 / 1024.0)
    return '{}'.format(size)


# CRYPTO METHOD
CRYPTO_METHODS = {'checksum': 0, 'crc16': 1, 'crc32': 2}


class CCT:
    DEFAULT_PORT = "/dev/ttyUSB0"
    CHIP_ROM_BAUD = 115200
    timeout = DEFAULT_TIMEOUT

    def __init__(self, port=DEFAULT_PORT, baud=CHIP_ROM_BAUD, trace_enabled=True):
        self._port = None
        self._trace_enabled = trace_enabled
        self._last_trace = time.time()
        if port is None and list_ports:
            port_list = list(list_ports.comports())
            for i in port_list:
                if i.hwid != 'n/a':
                    port = i.device
                    break
        if not port:
            print("Not found serial port.")
            exit()
        if isinstance(port, str):
            try:
                self._port = serial.serial_for_url(port, baud, exclusive=False)
            except IOError:
                self._port = serial.serial_for_url(port, baud, exclusive=False, rtscts=True, dsrdtr=True)
            except Exception:
                raise Exception("could not open serial port {}".format(port))
            self._port.reset_input_buffer()
            self._port.reset_output_buffer()
        else:
            self._port = port

    def read(self, count):
        return self._port.read(count)

    def write(self, data):
        return self._port.write(data)

    def reset_input_buffer(self):
        self._port.reset_input_buffer()

    def check_sum(self, data_buf, length):
        cksum = 0
        count = 0
        for v in data_buf:
            # print(ord(v))
            val = v
            if isinstance(v, str):
                val = ord(v)

            cksum = ctypes.c_uint32(cksum + val).value
            count = count + 1
        # print("checksum: 0x%x" % cksum)
        return cksum

    def command(self, cmd, param, data=b'', timeout=None):
        if not timeout:
            timeout = self.timeout
        saved_timeout = self._port.timeout
        new_timeout = min(timeout, MAX_TIMEOUT)
        if new_timeout != saved_timeout:
            self._port.timeout = new_timeout

        try:
            c = struct.pack('!BBH', cmd, param, len(data)) + data
            w = self.write(c)
            if w != len(c):
                print("write data to device error.")
                return False, [], None
            v = self.read(4)
            if len(v) == 4:
                data = struct.unpack('!BBH', v)
                payload = self.read(data[2])

                if data[0] == cmd and data[1] >= 0:
                    return True, data, payload

                if data[1] == 0xFD:
                    raise UnsupportedCommandError(self, '错误的命令序列')
                elif data[1] == 0xFE:
                    raise UnsupportedCommandError(self, '位置错误')
                elif data[1] == 0xFF:
                    raise UnsupportedCommandError(self, '未知命令')

            if len(v) >= 4 and data[0] != cmd:
                self.trace('command[0x%02x],but[0x%02x] response error.' % (cmd, data[0]))
                return False, [], None
                # raise UnsupportedCommandError(self, cmd)
        finally:
            if new_timeout != saved_timeout:
                self._port.timeout = saved_timeout

        return False, [], None

    def connect(self, timeout=30):
        start_ticks = time.time()
        print_count = 0
        while True:
            now_tick = time.time()
            if now_tick - start_ticks > timeout:
                break

            ret, v, _ = self.command(CMD_CONNECT, 0xEF, struct.pack('!BBBB', 0x43, 0x53, 0x4B, 0x59), timeout=0.01)
            if ret and v[1] == 1:
                if print_count != 0:
                    print()
                self.trace('connect success!')

                return True
            else:
                if print_count == 0:
                    print("Wait ", end='')
                else:
                    if print_count % 10 == 0:
                        print(".", end='')
                print_count += 1
                sys.stdout.flush()

        print("\nCCT timeout, Please try again.")

        return False

    def get_version(self):
        ret, v, _ = self.command(CMD_GET_VERSION, 0x00)
        if ret:
            return v[1]

    def get_img_version(self):
        ret, v, payload = self.command(CMD_GET_VERSION, 0x20)
        if ret:
            if v[1] == 0x01:
                length = v[2]
                if length == 5:
                    vver = struct.unpack('!5B', payload)
                    return vver[4]

    def get_timeout(self):
        ret, v, _ = self.command(0x0A, 0x00)
        if ret:
            print(v)

    def get_device_id(self, param):
        ret, v, _ = self.command(CMD_GET_DEVICE_ID, param)
        if ret:
            if v[1] == 0xE0:
                self.trace('device id not exist.')

    def get_crypto_method(self):
        method = []
        ret, v, payload = self.command(CMD_GET_CRYPTO_METHOD, 0x00)
        if ret and v[1] == 1:
            length = v[2]
            fmt = "!%dB" % length
            vv = struct.unpack(fmt, payload)
            for i in range(0, length):
                for key, value in CRYPTO_METHODS.items():
                    if value == vv[i]:
                        method.append(key)
                        break
        return method

    def get_memory_info(self):
        mem = {}
        ret, v, payload = self.command(CMD_GET_MEMORY_INFO, 0x00)
        if ret and v[1] == 1:
            length = v[2]

            idx = 0
            for _ in range(0, length // 6):
                vv = struct.unpack('!BBI', payload[idx: idx + 6])
                TY = vv[0]
                if TY == 0x00:
                    mem['recv'] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': u'协议接收缓冲区'}
                elif TY == 0x01:
                    mem['send'] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': u'协议发送缓冲区'}
                elif TY == 0x02:
                    mem['ram{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'SRAM'}
                elif TY == 0x03:
                    mem['eflash{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'EFlash'}
                elif TY == 0x10:
                    mem['ddr{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'SDRAM/DDR'}
                elif TY == 0x11:
                    mem['nflash{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'NOR Flash'}
                elif TY == 0x12:
                    mem['sflash{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'SPI Flash'}
                elif TY == 0x13:
                    mem['nand{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'Nand Flash'}
                elif TY == 0x14:
                    mem['sd{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2] * 512, 'desc': 'SD Flash'}
                elif TY == 0x15:
                    mem['emmc{}'.format(vv[1])] = {
                        'type': vv[0], 'id': vv[1], 'size': vv[2] * 512, 'desc': 'eMMC Flash'
                    }
                elif TY == 0x16:
                    mem['efuse{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'e-Fuse'}
                elif TY == 0x17:
                    mem['qspi{}'.format(vv[1])] = {'type': vv[0], 'id': vv[1], 'size': vv[2], 'desc': 'QSPI Flash'}
                idx += 6

        return mem

    def download_init(self, Type, ID, offset, length):
        # Cmd	Param	Len16_H	Len16_L	    Data, Len=(Len16_H<<8 & Len16_L)
        # 0x12	0x00	0x00	1+1+4+4+N	1:Type 1: ID, 4: Offset, 4: Size, N=Data Name
        # 0x12	0x01	0x00	4+4+N	     4: Address, 4: Size, N=Image Name
        c = struct.pack('!BBII', Type, ID, offset, length)
        ret, v, _ = self.command(CMD_INIT_DOWNLOAD_NSEC, 0x00, c)

        if ret and v[1] == 1 and v[2] == 0:
            self.trace('download_init type=%d, id=%d, offset=%d, lenght=%d', Type, ID, offset, length)
        return ret

    def download_init_pro(self, abs_address, Type, ID, offset, length):
        # Cmd	Param	Len16_H	Len16_L	    Data, Len=(Len16_H<<8 & Len16_L)
        # 0x23	0x00	0x00	1+1+4+4+N	1:Type 1: ID, 4: Offset, 4: Size, N=Data Name
        # 0x23	0x01	0x00	8+4+N	    8: Address, 4: Size, N=Image Name
        param = 0x00
        if abs_address is not None:
            param = 0x01
            c = struct.pack('!QI', abs_address, length)
        else:
            c = struct.pack('!BBII', Type, ID, offset, length)
        ret, v, _ = self.command(CMD_INIT_DOWNLOAD_NSEC_PRO, param, c)
        if ret and v[1] == 1 and v[2] == 0:
            if abs_address is not None:
                self.trace('download_init_pro abs_address:0x%x, lenght=%d', abs_address, length)
            else:
                self.trace('download_init_pro type=%d, id=%d, offset=%d, lenght=%d', Type, ID, offset, length)
        return ret

    def download_data(self, flags, data):
        # Cmd	Param	Len16_H	Len16_L	Data, Len=(Len16_H<<8 & Len16_L)
        # 0x13	0x00~03	N	            N: (1~SoC Buffer Size)
        ret, v, _ = self.command(CMD_DOWNLOAD_DATA_NSEC, flags, data)
        if ret:
            if v[1] == 0x00 or v[1] == 0x01:
                pass
            else:
                if v[1] == 0xE0:
                    self.trace("写入错误")
                elif v[1] == 0xE1:
                    self.trace("单数据包长度过大")
                elif v[1] == 0xE1:
                    self.trace("超过请求下载数据长度")
                return False

        return ret

    def download(self, version, abs_address, offset, data, Type=2,
                 ID=0, block_size=512, compress=False, checksum=0):
        def chunked_bytes(data, size=512):
            for i in range(0, len(data), size):
                yield data[i:i + size]

        zdata = []
        full_size = len(data)
        data_size = 0
        for chunk in chunked_bytes(data, block_size):
            if compress:
                chunk = zlib.compress(chunk, 9)
            zdata.append(chunk)
            data_size += len(chunk)

        if compress:
            print("%d => %d %3.2f%%" % (full_size, data_size, data_size * 100.0 / full_size))

        ret = False

        if version < 4:
            self.download_init(Type, ID, offset, data_size)
        else:
            self.download_init_pro(abs_address, Type, ID, offset, full_size)

        offset = 0
        for d in zdata:
            data_len = len(d)
            checksum = checksum + self.check_sum(d)
            if offset == 0:
                ret = self.download_data(0x03, d)
            elif offset + data_len < data_size:
                ret = self.download_data(0x02, d)
            else:
                ret = self.download_data(0x00, d)
            if not ret:
                print("\nWrite Failed. ret", ret)
                return False, 0, 0
            offset += data_len
            at_addr = offset
            if abs_address is not None:
                at_addr = abs_address + offset
            print_overwrite('Writing at 0x%08x... (%d%%)' % (at_addr, 100.0 * offset / data_size))
        print()
        return ret, data_size, checksum

    def download_file(self, version, abs_address, offset, filename, Type=2,
                      ID=0, block_size=512, compress=False, checksum=0):
        data = pathlib.Path(filename).read_bytes()
        self.download(version, abs_address, offset, data, Type, ID, block_size, compress, checksum)

    def verify_data(self, method, abs_addr, offset, Type, ID, file_size, checksum):
        # Cmd	Param	Len16_H	Len16_L	    Data, Len=(Len16_H<<8 & Len16_L)
        # 0x15	0x00	0x00	1+1+4+4+1+N	1: Type, 1: ID, 4: Offset, 4: Size, 1: Verify method, N:Verify value
        print("Start to verify data with method:[%s]" % method)
        print("checksum value is: 0x%x" % checksum)
        m = CRYPTO_METHODS[method]
        if m is None:
            print("The crypto method:%s is wrong." % method)
            return False
        if abs_addr:
            print("Not support absolute address verify.")
            return False
        c = struct.pack('!BBIIBI', Type, ID, offset, file_size, m, checksum)
        ret, v, _ = self.command(CMD_VERIFY_DATA, 0x00, c)
        if ret:
            if v[1] == 0x01:
                print('读出并校验成功!')
            elif v[1] == 0xE0:
                print("数据读取失败")
            elif v[1] == 0xE1:
                print("校验失败")
            elif v[1] == 0xE2:
                print("校验算法不支持")
        return ret and v[1] == 1

    def upload_data_nsec(self):
        ret, v, payload = self.command(CMD_UPLOAD_DATA_NSEC, 0x00)
        pass

    def read_memory(self, address, size=512):
        # 0x26	0x00	0x00	1+1+4+2	1:Type 1: ID, 4: Offset, 2: Size
        # 0x26	0x01	0x00	4+2	4: Address, 2: Size
        c = struct.pack('!II', address, size)
        ret, v, _ = self.command(CMD_INIT_DOWNLOAD_NSEC, 0x01, c)
        if ret:
            print(v)

    def run_image(self, offset):
        # Cmd	Param	Len16_H	Len16_L	   Data, Len=(Len16_H<<8 & Len16_L)
        # 0x18	0x00	0x00	1+1+4+N	   1:Type 1: ID, 4: Offset
        #                                  N: Run parameters, SoC will load to (P0-P3)
        print("Start to run image...")
        c = struct.pack('!BBI', 2, 0, offset)
        ret, v, _ = self.command(CMD_RUN_IMAGE, 0x00, c)
        if ret:
            if v[1] == 0x01:
                self.trace('已准备好，立即运行!')
            elif v[1] == 0xE1:
                self.trace("设备不存在或地址不合法")
            elif v[1] == 0xE2:
                self.trace("源不可XIP执行")
            elif v[1] == 0xE3:
                self.trace("源读取失败")

        return ret and v[1] == 1

    def run_image_pro(self, ver, abs_addr, offset):
        # Cmd	Param	Len16_H	Len16_L	   Data, Len=(Len16_H<<8 & Len16_L)
        # 0x32	0x00	0x00	1+1+4+N	   1:Type 1: ID, 4: Offset
        #                                  N: Run parameters, SoC will load to (P0-P3)
        # 0x32	0x01	0x00	8+N	       8: Address, N: Run parameters, SoC will load to R0~R3
        self.trace("run_image_pro, version:%d" % ver)
        if ver < 4:
            raise UnsupportedCommandError(self, '未知命令')
        param = 0x00
        if abs_addr is not None:
            self.trace("abs_addr:0x%x" % abs_addr)
            param = 0x01
            c = struct.pack('!Q', abs_addr)
        else:
            self.trace("offset:0x%x" % offset)
            c = struct.pack('!BBI', 2, 0, offset)
        ret, v, _ = self.command(CMD_RUN_IMAGE_PRO, param, c)
        if ret:
            if v[1] == 0x01:
                self.trace('已准备好，立即运行!')
            elif v[1] == 0xE1:
                self.trace("设备不存在或地址不合法")
            elif v[1] == 0xE2:
                self.trace("源不可XIP执行")
            elif v[1] == 0xE3:
                self.trace("源读取失败")

        return ret and v[1] == 1

    def set_register_val(self, reg, val):
        # Cmd	Param	Len16_H	Len16_L	   Data, Len=(Len16_H<<8 & Len16_L)
        # 0x24	0x00	0x00	8+8	       8: register address;8：value of reg
        c = struct.pack('!QQ', reg, val)
        ret, v, payload = self.command(CMD_SET_REGISTER_VAL, 0x00, data=c)
        if ret:
            if v[1] == 0x01:
                print("Set register succeed.")
            else:
                print("Set register value failed.")

    def get_register_val(self, reg):
        # Cmd	Param	Len16_H	Len16_L	   Data, Len=(Len16_H<<8 & Len16_L)
        # 0x25	0x00	0x00	8	       8: register address
        c = struct.pack('!Q', reg)
        ret, v, payload = self.command(CMD_GET_REGISTER_VAL, 0x00, data=c)
        if ret:
            if v[1] == 0x01:
                reg_val = struct.unpack('!Q', payload)
                print("Get val: 0x%x" % reg_val)
            else:
                print("Get register value failed.")

    def do_reboot(self):
        ret, v, _ = self.command(CMD_DO_REBOOT, 0x00, timeout=0.1)
        self.trace("do_reboot,ret:0x%x" % v[1])
        if ret:
            if v[1] == PROTOCOL_RESULT_WRONG_COMMAND:
                print("Reboot failed.")
            elif v[1] == PROTOCOL_RESULT_SUCCESS:
                print("Reboot ok.")

    def trace(self, message, *format_args):
        if self._trace_enabled:
            now = time.time()
            try:

                delta = now - self._last_trace
            except AttributeError:
                delta = 0.0
            self._last_trace = now
            prefix = "TRACE +%.3f " % delta
            print(prefix + (message % format_args))


def cct_run(fd, device, data, abs_addr):
    ret = False
    cct = CCT(fd)
    if not cct.connect():
        return ret
    time.sleep(0.05)
    cct.reset_input_buffer()
    ver = cct.get_version()
    if not ver:
        print("Get version error.")
        return ret
    mem = cct.get_memory_info()

    checksum = 0
    if abs_addr:
        ret, _, _ = cct.download(ver, abs_addr, None, data, None,
                                 None, 512, False, checksum=checksum)
        if ret:
            cct.run_image_pro(ver, abs_addr, None)
    elif device in mem:
        opt_type = mem[device]['type']
        opt_id = mem[device]['id']
        print("Send data to %d:%d ..." % (opt_type, opt_id))
        ret, _, _ = cct.download(ver, None, 0, data, opt_type, opt_id,
                                 512, False, checksum=checksum)
        if ret:
            ret = cct.run_image(0)
    return ret


class Cct:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-u', dest='uart', default=None,
                                 help='CCT serial port device')
        self.parser.add_argument('-f', dest='file', default='',
                                 help='')
        self.parser.add_argument('-o', dest='offset', default=0,
                                 help='Device start address')
        self.parser.add_argument('-b', '--block', dest='block', default=512,
                                 help='')
        self.parser.add_argument('-d', '--device', dest='device', default=None,
                                 help='Device name')
        self.parser.add_argument('-c', '--compress', dest='compress', action='store_true', default=False,
                                 help='')
        self.parser.add_argument('-v', '--verify', dest='verify', default=None,
                                 help='')
        self.parser.add_argument('-i', '--image', dest='image', action='store_true', default=False,
                                 help='')
        self.parser.add_argument('-r', '--run', dest='run', action='store_true', default=False,
                                 help='')
        self.parser.add_argument('-m', '--method', dest='method', default=None,
                                 help='List crypto method')
        self.parser.add_argument('-g', '--register', dest='register', default=0,
                                 help='Register of Device')
        self.parser.add_argument('-e', '--value', dest='value', default=0,
                                 help='Value of Register')
        self.parser.add_argument('-s', '--abs_addr', dest='abs_addr', default=None,
                                 help='absolute address')
        self.parser.add_argument('-t', '--timeout', dest='timeout', default=None,
                                 help='timeout in second')
        self.parser.add_argument('-D', '--debug', dest='debug', action='store_true', default=False,
                                 help='Enable debbug trace info')

    def execute(self):
        opt, args = self.parser.parse_known_args()

        if args[0] == 'uart':
            print("uart device list:")
            if list_ports:
                port_list = list(list_ports.comports())
                for i in port_list:
                    print('  ', i)
            exit(0)

        cct = CCT(opt.uart)
        cct._trace_enabled = opt.debug
        if opt.timeout:
            cct.timeout = opt.timeout
        if not cct.connect():
            return
        time.sleep(0.05)
        cct.reset_input_buffer()
        ver = cct.get_version()
        if not ver:
            print("Get version error.")
            exit(0)
        mem = cct.get_memory_info()

        if args[0] == 'version':
            v = cct.get_version()
            print('Protocol Version: %d' % v)
            if opt.image:
                v = cct.get_img_version()
                if not v:
                    print("Get image version failed.")
                    return
                print('Image Version: %d' % v)
        elif args[0] == 'mlist':
            print("Crypto method list:")
            method = cct.get_crypto_method()
            for v in method:
                print("  %s" % v)
        elif args[0] == 'list':
            print("Memory device list:")
            for k, v in mem.items():
                if v['type'] > 1:
                    print("  dev = %-7s, size = %s" % (k, to_size(v['size'])))
        elif args[0] == 'download':
            if os.path.exists(opt.file):
                checksum = 0
                if opt.abs_addr:
                    print("Send file '%s' to 0x%x ..." % (opt.file, opt.abs_addr))
                    ret, file_size, checksum = cct.download_file(ver, opt.abs_addr, None, opt.file, None,
                                                                 None, 512, opt.compress, checksum=checksum)
                    if ret and opt.verify:
                        ret = cct.verify_data(opt.verify, opt.abs_addr, None, None, None, file_size, checksum)
                    if ret and opt.run:
                        cct.run_image_pro(ver, opt.abs_addr, None)
                elif opt.device in mem:
                    opt_type = mem[opt.device]['type']
                    opt_id = mem[opt.device]['id']
                    print("Send file '%s' to %d:%d ..." % (opt.file, opt_type, opt_id))
                    ret, file_size, checksum = cct.download_file(ver, None, opt.offset, opt.file, opt_type, opt_id,
                                                                 opt.block, opt.compress, checksum=checksum)
                    if ret and opt.verify:
                        ret = cct.verify_data(opt.verify, None, opt.offset, opt_type, opt_id, file_size, checksum)
                    if ret and opt.run:
                        cct.run_image(opt.offset)
                else:
                    print('Device `%s` not exists, please select' % opt.device)
            else:
                print("file %s not exists" % opt.file)
        elif args[0] == 'reboot' or args[0] == 'getreg' or args[0] == 'setreg':
            if ver < 4:
                print("Not support.")
                exit(0)
            if args[0] == 'reboot':
                print("Make device reboot.")
                cct.do_reboot()
            elif args[0] == 'getreg':
                if not opt.register:
                    print("Please input register address.")
                    self.Usage()
                    exit(0)
                print("Get register[0x%x]'s value:" % opt.register)
                cct.get_register_val(opt.register)
            elif args[0] == 'setreg':
                if not opt.register or not opt.value:
                    print("Please input register address and the value.")
                    self.Usage()
                    exit(0)
                print("Set register[0x%x] value[0x%x]" % (opt.register, opt.value))
                cct.set_register_val(opt.register, opt.value)
