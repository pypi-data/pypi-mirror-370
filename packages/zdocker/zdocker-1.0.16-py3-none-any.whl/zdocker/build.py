#!/usr/bin/env python3

import argparse
import os
import sys
import shutil
import signal
import ctypes


from zdocker import util, docker


USER_CTRL_C = 3                         # 3: Ctrl+C
ERROR_SIGTERM = 5                       # 5: SIGTERM


class Extender(argparse.Action):
    """Allows using the same flag several times in command and creates a list with the values.
    For example:
        conan install MyPackage/1.2@user/channel -o qt:value -o mode:2 -s cucumber:true
      It creates:
          options = ['qt:value', 'mode:2']
          settings = ['cucumber:true']
    """
    def __call__(self, parser, namespace, values, option_strings=None):  # @UnusedVariable
        # Need None here in case `argparse.SUPPRESS` was supplied for `dest`
        dest = getattr(namespace, self.dest, None)
        if not hasattr(dest, 'extend') or dest == self.default:
            dest = []
            setattr(namespace, self.dest, dest)
            # if default isn't set to None, this method might be called
            # with the default as `values` for other arguments which
            # share this destination.
            parser.set_defaults(**{self.dest: None})

        if isinstance(values, str):
            dest.append(values)
        elif values:
            try:
                dest.extend(values)
            except ValueError:
                dest.append(values)


class BuildCommand:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--disable-interactive', default=False,
                                 action='store_true', help="Disable docker interactive mode")
        self.parser.add_argument('--allow-root', default=False,
                                 action='store_true', help="Allow root run to zbuild")
        self.parser.add_argument('--verbose', default=False,
                                 action='store_true', help="Verbose mode, show debugging messages")
        self.parser.add_argument('--name', default=None,
                                 help="Assign a name to the container")
        self.parser.add_argument('--hostname', default="zbuild",
                                 help="Assign a hostname to the container")
        self.parser.add_argument('-e', '--env', default=[], nargs='*',
                                 action=Extender, help="Set environment variables")
        self.parser.add_argument('-d', '--device', default=[], nargs='*',
                                 action=Extender, help="Add a host device to the container")
        self.parser.add_argument('-v', '--volume', default=[], nargs='*',
                                 action=Extender, help="Bind mount a volume")
        self.parser.add_argument('-p', '--publish', default=[], nargs='*',
                                 action=Extender, help="Publish a container's ports to the host")
        self.parser.add_argument('--network', default=None, help="Connect a container to a network")

        self.parser.add_argument('command', default=[], nargs='*',
                                 help="shell command, For example: /bin/zsh")

    def run_command(self):
        argv = sys.argv[1:]

        opt = self.parser.parse_args(argv)

        if os.getuid() == 0 and not opt.allow_root:
            print(util.ctext.ctext.fmt(util.ctext.ctext.R, "Running zbuild from the root account will be disabled in the next release!"))
            print("Do not allow root to run zbuild!")
            sys.exit(1)

        if shutil.which('docker'):
            docker.DockerRunner(opt).run()
        else:
            print('You need to install the Docker or linux development environment.')

    def run(self):
        def ctrl_c_handler(_, __):
            sys.exit(USER_CTRL_C)

        def sigterm_handler(_, __):
            sys.exit(ERROR_SIGTERM)

        libc = ctypes.CDLL('libc.so.6')
        PR_SET_PDEATHSIG = 1
        if libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM) != 0:
            print("Failed to set PR_SET_PDEATHSIG")
            return

        signal.signal(signal.SIGINT, ctrl_c_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        try:
            self.run_command()
        except Exception as exc:
            exec_name = exc.__class__.__name__
            if (not os.getenv("ZB_DEBUG")) and exec_name in [
                            'ZbuildException', 'ConanException', 'FileNotFoundError',
                            'DockerException', 'KeyboardInterrupt']:
                for arg in exc.args:
                    if isinstance(arg, tuple):
                        for a in arg:
                            print(a)
                    else:
                        print(arg)
            else:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        sys.exit(0)
