import datetime
import os
import pathlib
import sys
import shutil
import atexit
import tempfile
import textwrap
import time
import socket
import configparser
import gzip
from tqdm import tqdm

import requests
import docker
import dockerpty
from docker.errors import ImageNotFound
from docker.models.containers import Container

from zdocker import util
from zdocker.util import save_if_not_exists, load, save

docker_url = "ubuntu-24.04-x86_64:v1.7.0"


def get_volume_path(path):
    paths = [f"{path}:{path}"]
    while path != "/":
        if os.path.islink(path):
            realpath = os.path.realpath(path)
            paths.append(f"{realpath}:{realpath}")
        path = os.path.dirname(path)
    return paths


def generate_temp_name():
    username = os.getlogin()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = '{:04x}'.format(abs(hash(timestamp) % (1 << 16)))
    temp_filename = f"{username}_{timestamp}_{random_part}"

    return temp_filename


def gitconfig_init(username, output_file):
    def update(conf, key, value={}):
        if key not in conf:
            conf[key] = value
        return conf[key]

    gitconfig_file = os.path.join(os.path.expanduser('~'), '.gitconfig')

    config = configparser.ConfigParser(interpolation=None, strict=False)
    if os.path.exists(gitconfig_file):
        config.read(gitconfig_file)

    user = update(config, 'user')
    alias = update(config, 'alias')
    color = update(config, 'color')
    core = update(config, 'core')
    pull = update(config, 'pull')
    push = update(config, 'push')

    update(user, 'email', f"{username}@zhcomputing.com")
    update(user, 'name', username)
    update(alias, 'st', 'status')
    update(alias, 'co', 'checkout')
    update(alias, 'br', 'branch')
    update(alias, 'ci', 'commit')
    update(alias, 'df', 'diff')
    update(alias, 'undo', 'reset HEAD~1')
    update(alias, 'lg', "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative")
    update(color, 'ui', 'true')
    update(color, 'branch', 'true')
    update(color, 'diff', 'true')
    update(color, 'status', 'true')
    update(core, 'editor', 'vim')
    update(pull, 'rebase', 'true')
    update(push, 'default', 'current')

    with open(output_file, 'w') as f:
        config.write(f)


class DockerContainer:
    def __init__(self, opt):
        uid = os.getuid()
        gid = os.getgid()

        self.name = generate_temp_name()

        custom_version = os.getenv("DOCKER_VERSION")
        if custom_version:
            custom_version = f"{docker_url.split(':')[0]}:{custom_version}"
        self.image = os.getenv("DOCKER_IMAGE") or custom_version or docker_url

        self.version = self.image.split(':')[-1].lstrip('v')
        self.working_dir = os.getenv("PWD")
        self.user = f"{uid}:{gid}"
        self.stdin_open = True
        self.volumes = get_volume_path(self.working_dir)
        home_dir = os.path.expanduser('~')
        if home_dir != self.working_dir:
            self.volumes.append(f"{home_dir}:{home_dir}")

        self.devices = []
        self.environment = []
        self.ports = {}
        self.cap_add = ['SYS_ADMIN']
        self.network_mode = None
        self.tty = sys.stdout.isatty()
        self.auto_remove = True
        self.privileged = True
        self.hostname = 'docker'
        self.set_env("DOCKER_IMAGE", self.image)
        self.set_env("DOCKER_VERSION", self.version)

        self.command = " ".join(opt.command) or "/bin/zsh"
        self.environment.extend(opt.env)
        self.devices.extend(opt.device)
        self.volumes.extend(opt.volume)
        for port in opt.publish:
            self.add_port(port)
        self.network_mode = opt.network or self.network_mode
        self.name = opt.name or self.name
        if opt.hostname == "_":
            self.hostname = socket.gethostname()
        else:
            self.hostname = opt.hostname or self.hostname

    @property
    def image_url(self):
        return os.getenv("DOCKER_URL") or "http://8.149.140.24:8082/artifactory/generic-local/docker/ubuntu-24.04-x86_64.v1.7.0.tar.gz"

    def add_port(self, publish):
        parts = publish.split(':')
        if len(parts) == 2:
            port_protocol = parts[1].split('/')
            key, val = port_protocol[0] + '/' + (port_protocol[1] if len(port_protocol) > 1 else 'tcp'), int(parts[0])
        elif len(parts) == 3:
            port_protocol = parts[2].split('/')
            key, val = port_protocol[0] + '/' + (port_protocol[1] if len(port_protocol) > 1 else 'tcp'), (parts[0], int(parts[1]))
        else:
            raise ValueError('Invalid publish format')
        self.ports[key] = val

    def set_env(self, name, value=None):
        if value is None:
            value = os.getenv(name)
        if value:
            self.environment.append(f"{name}={value}")

    def image_load(self, docker_client: docker.DockerClient):
        with requests.get(self.image_url, stream=True) as response:
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tar_file:
                file_size = int(response.headers.get('Content-Length', 0))

                progress_bar = tqdm(
                    desc=f"Download {self.image}",
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                )

                class ProgressReader:
                    def __init__(self, raw_stream):
                        self._raw = raw_stream

                    def read(self, size):
                        chunk = self._raw.read(size)
                        if chunk:
                            progress_bar.update(len(chunk))  # 更新：真实下载的压缩后字节数
                        return chunk

                decompressor = gzip.GzipFile(fileobj=ProgressReader(response.raw))
                for chunk in decompressor:
                    tar_file.write(chunk)
                progress_bar.close()
                print(f"Loading docker image {self.image} ...")
                with open(tar_file.name, "rb") as f:
                    docker_client.images.load(f)

    def run(self, verbose):
        def verbose_show(prompt, values):
            if values:
                print(util.ctext.fmt(util.ctext.B, prompt))
                if isinstance(values, list):
                    for v in values:
                        print("  ", v)
                elif isinstance(values, dict):
                    for k, v in values.items():
                        print(f"  {k}: {v}")
                elif isinstance(values, str):
                    print("  ", values)

        docker_client = docker.from_env()

        if self.network_mode == 'host':
            self.ports = None

        self.devices = list(set(self.devices))
        self.volumes = list(set(self.volumes))
        self.environment = list(set(self.environment))
        if verbose:
            verbose_show("Devices:", self.devices)
            verbose_show("Volumes:", self.volumes)
            verbose_show("Environment:", self.environment)
            verbose_show("net ports:", self.ports)
            verbose_show("kernel capabilities:", self.cap_add)
            for k, v in self.__dict__.items():
                if isinstance(v, str):
                    verbose_show(k + ':', v)

        try:
            container: Container = docker_client.containers.get(self.name)
            container.remove(force=True)
        except Exception:
            pass

        try:
            self.container: Container = docker_client.containers.create(**self.__dict__)
        except ImageNotFound:
            self.image_load(docker_client)
            docker_client = docker.from_env()
            self.container: Container = docker_client.containers.create(**self.__dict__)

        if sys.stdout.isatty():
            print("Running in Docker %s ..." % self.image)
        status_code = 0
        try:
            dockerpty.start(docker_client.api, self.container.id)
            status = self.container.wait()
            status_code = status['StatusCode']
        except Exception:
            pass
        finally:
            self.container_remove(True)
        return status_code

    def container_remove(self, force=True):
        if hasattr(self, 'container') and self.container:
            try:
                self.container.remove(force=force)
                self.container = None
            except Exception:
                pass

    def __del__(self):
        self.container_remove(True)


class DockerRunner(object):
    def __init__(self, opt):
        self.opt = opt
        self.USER = os.getenv("DOCKER_USER") or os.getlogin()
        self.UID = os.getuid()
        self.GID = os.getgid()
        self.home = os.path.expanduser('~')

        self.docker = DockerContainer(opt)

        self.user_passwd_group()
        self.local_path()
        self.parser_opts(opt)

    def parser_opts(self, opt):
        self.docker.stdin_open = not opt.disable_interactive
        if os.path.exists('/dev/net/tun'):
            self.docker.devices.append('/dev/net/tun:/dev/net/tun')
            self.docker.cap_add.append('NET_ADMIN')
            self.docker.network_mode = 'host'

        if hasattr(opt, 'ethernet'):
            ip, _ = util.get_enternet_ip(opt.ethernet)
            if ip:
                host_ip_file = os.path.join(self.home, '.docker_local/hostconf')
                with open(host_ip_file, 'w', encoding='utf-8') as file:
                    file.write(ip.address + ':' + ip.netmask)

        if hasattr(opt, 'socat') and opt.socat:
            def kill_socat_proc():
                if hasattr(self, 'socat_proc') and self.socat_proc:
                    util.subprocess_terminate(self.socat_proc)
                    self.socat_proc.wait()
                    self.socat_proc = None

            socat = shutil.which('socat')
            if not socat:
                print('socat not found!')
                sys.exit(1)
            if os.path.exists(opt.socat):
                os.remove(opt.socat)

            qemu_pty = "qemu_pty_" + str(os.getuid())
            tmp_qemu_pty = f"/tmp/{qemu_pty}"
            if os.path.exists(tmp_qemu_pty):
                os.remove(tmp_qemu_pty)

            cmd = f'{socat} -dd pty,raw,echo=0,link={tmp_qemu_pty},ignoreeof,mode=660 ' \
                  f'pty,raw,echo=0,link={opt.socat},ignoreeof,mode=660'
            _, self.socat_proc = util.subprocess_execute(cmd, wait_return=False)
            atexit.register(kill_socat_proc)
            while True:
                if os.path.exists(tmp_qemu_pty):
                    break
                time.sleep(0.5)
            pts_1 = os.readlink(tmp_qemu_pty)
            self.docker.volumes.append(f"{pts_1}:/dev/{qemu_pty}")

        if hasattr(opt, 'env'):
            for env in opt.env:
                key, name = env.split("=")
                if 'source-path' in key:
                    source_path = os.path.realpath(os.path.expanduser(name))
                    if not os.path.exists(source_path):
                        raise Exception(f"source-path {source_path} not exists")
                    self.docker.volumes.append(f"{source_path}:{source_path}")

    def local_path(self):
        LOCAL_PATH = os.path.join(self.home, '.docker_local')
        BOARD_YML = os.path.join(self.home, '.local/board.yml')
        SSH_CFG_FILE = os.path.join(self.home, '.ssh/zbuild_sshcfg')
        BASHRC_FILE = os.path.join(LOCAL_PATH, '.bashrc')
        ZSHRC_FILE = os.path.join(LOCAL_PATH, '.zshrc')
        HOSTS_FILE = os.path.join(LOCAL_PATH, '.hosts')
        GITCONFIG_FILE = os.path.join(LOCAL_PATH, '.gitconfig')
        build_cmd_file = pathlib.Path(LOCAL_PATH, 'bin/zbuild')
        build_cmd_file.parent.mkdir(parents=True, exist_ok=True)

        self.docker.set_env('PATH', f"{self.home}/.local/bin:/usr/local/riscv-toolchain/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
        self.docker.set_env('https_proxy')
        self.docker.set_env('http_proxy')
        self.docker.set_env('http_proxy')
        self.docker.set_env('BOARD_NAME')

        for env, value in os.environ.items():
            if env.startswith("ZB_") or env in [
                "MAIN_SERVER_ADDR",
                "MAKE_PROGRAM",
                "CONAN_USER_HOME",
                "ARCH",
                "CROSS_COMPILE",
            ]:
                self.docker.set_env(env, value)
            if env.startswith("CONAN_"):
                self.docker.set_env(env, value)

        conan_user_home = os.getenv('CONAN_USER_HOME')
        if conan_user_home:
            self.docker.volumes.append(f"{conan_user_home}:{conan_user_home}")
        if os.path.exists("/home/public"):
            self.docker.volumes.append("/home/public:/home/public")

        save_if_not_exists(BASHRC_FILE, "PS1='\\[\\e[01;32m\\]\\u@\\h\\[\\e[m\\]:\\[\\e[01;34m\\]\\w\\[\\e[m\\]\\$ '\n")
        save_if_not_exists(SSH_CFG_FILE, textwrap.dedent("""\
            Host *
              StrictHostKeyChecking no
        """))
        save_if_not_exists(ZSHRC_FILE, textwrap.dedent("""\
            ZSH_DISABLE_COMPFIX=true
            source /usr/share/zsh/config/zshrc
            export PROMPT='$CYAN%n@$YELLOW$(hostname):$FG[039]$GREEN$(_fish_collapsed_pwd)%f > '
        """))
        save_if_not_exists(HOSTS_FILE, load("/etc/hosts") + "127.0.1.1 docker\n")
        gitconfig_init(self.USER, GITCONFIG_FILE)

        nvim_init = os.path.join(self.home, '.config/nvim/init.lua')
        save_if_not_exists(nvim_init, textwrap.dedent("""\
            vim.opt.runtimepath:prepend("/usr/share/nvim-config")
            require("config.lazy")
        """))
        nvim_plugins_init = os.path.join(self.home, '.config/nvim/lua/plugins/init.lua')
        save_if_not_exists(nvim_plugins_init, "return {}\n")

        self.docker.volumes.extend([
            f"/dev/null:{self.home}/.profile",
            f"{LOCAL_PATH}:{self.home}/.local",
            f"{SSH_CFG_FILE}:{self.home}/.ssh/config",
            f"{BASHRC_FILE}:{self.home}/.bashrc",
            f"{ZSHRC_FILE}:{self.home}/.zshrc",
            f"{HOSTS_FILE}:/etc/hosts",
            f"{GITCONFIG_FILE}:{self.home}/.gitconfig",
            "/schema:/schema",
            "/tmp:/tmp",
        ])

        localtime_file = os.path.realpath("/etc/localtime")
        if os.path.exists(localtime_file):
            self.docker.volumes.append(f"{localtime_file}:/etc/localtime")

        timezone_file = os.path.realpath("/etc/timezone")
        if os.path.exists(timezone_file):
            self.docker.volumes.append(f"{timezone_file}:/etc/timezone")

        if os.path.isfile(BOARD_YML):
            self.docker.volumes.append(f"{BOARD_YML}:{BOARD_YML}")

    def user_passwd_group(self):
        PASSWD_FILE = os.path.join(self.home, '.local/passwd')
        GROUP_FILE = os.path.join(self.home, '.local/group')
        save(PASSWD_FILE, textwrap.dedent(f"""\
            root:x:0:0:root:/root:/bin/bash
            {self.USER}:x:{self.UID}:{self.GID}:,,,:{self.home}:/bin/zsh
        """), only_if_modified=True)
        save(GROUP_FILE, textwrap.dedent(f"""\
            root:x:0:
            dialout:x:20:{self.USER}
            {self.USER}:x:{self.GID}:
        """), only_if_modified=True)
        self.docker.volumes.extend([
            f"{PASSWD_FILE}:/etc/passwd:ro",
            f"{GROUP_FILE}:/etc/group:ro",
            f"{GROUP_FILE}:/etc/group-:ro",
        ])

    def run(self):
        sys.exit(self.docker.run(self.opt.verbose))
