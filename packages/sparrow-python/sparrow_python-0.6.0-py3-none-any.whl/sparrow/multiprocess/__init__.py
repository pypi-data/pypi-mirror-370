import os
from subprocess import Popen, PIPE
from pathlib import Path
from sparrow.multiprocess.config import Config
from sparrow.multiprocess.server import DataManager, register_server_methods
from sparrow.multiprocess.kill_pid import kill_ports_cross_platform
from typing import Tuple, Union, List


def start_server(port=50001, deque_maxlen=None):
    """
    Create a remote manage server.
    port: 50001
    deque_maxlen: None
    """
    print(f"🚀start success! server port:{port}")
    config = Config(port=port)
    register_server_methods()
    manager = DataManager(address=(config.host, config.port),
                          authkey=config.authkey)
    manager.set_data_deque(maxlen=deque_maxlen)
    manager.get_server().serve_forever()


def run(cmd, **env):
    cmd = cmd.split(' ') if isinstance(cmd, str) else cmd
    p = Popen(cmd, cwd=str(Path(__file__).parent), env={**os.environ, **env})
    return p


def start_server_old():
    server_dir = os.path.dirname(os.path.realpath(__file__))

    p = run(f"python {server_dir}/server.py")
    print('pid:', p.pid)
    print(f"service start at {Config()}")
    p.communicate()
    return p


def stop_server(p: Popen):
    p.kill()


def kill(ports: Union[Tuple[int], int], view=False):
    """
    Kill process by port.
    """
    kill_ports_cross_platform(ports=ports, just_view=view)
