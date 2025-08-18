import sparrow.multiprocess.server as multi_server
from sparrow.multiprocess.config import Config
from copy import copy


class Client:
    """
    Example:
    First start service:
    ~$ sparrow start-server
    >>> from sparrow.multiprocess._client import Client
    >>> client = Client()
    >>> client.update_dict({'a': 1, 'b': 2})
    >>> print(client.get_dict_data())
    """

    def __init__(self, port=None):
        server_config = Config()
        if port:
            server_config.port = port
        multi_server.register_client_methos()
        self._manager = multi_server.DataManager(
            address=(server_config.host, server_config.port),
            authkey=server_config.authkey)
        self._manager.connect()
        self._dict = self._manager.get_dict()
        self._list = self._manager.get_list()
        self._queue = self._manager.get_queue()
        self._deque = self._manager.get_deque()

    def update_dict(self, data: dict):
        self._dict.update(data)

    def append_to_list(self, data):
        self._list.append(data)

    def put_queue(self, data):
        self._queue.put(data)

    def append_deque(self, data):
        self._deque.append(data)

    def get_deque(self):
        return self._deque

    def get_dict_data(self):
        """Return a copy of original data."""
        return self._dict

    def get_list_data(self):
        return self._list

    def get_queue(self, block=True):
        try:
            return self._queue.get(block=block)
        except Exception as e:
            return None

    def get_raw_data(self):
        return self._dict


if __name__ == "__main__":
    import numpy as np

    client = Client()
    client.put_queue(['asdkf', 'asdf'])
    client.append_deque(['asdf'])
    client.append_deque(['asdf'])
    client.append_deque(['asdf'])
    client.update_dict({'a': 1, 'b': 100})
    client.append_to_list(np.sin(np.linspace(0, 10, 10)))
    print(client.get_deque())
    while True:
        print(client.get_queue(block=True))
        print(client.get_dict_data())
        print(client.get_list_data())
        print(client.get_deque())
        print("------------------------")
