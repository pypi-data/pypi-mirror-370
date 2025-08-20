from multiprocessing.managers import SyncManager, BaseManager
from typing import TypeVar, List, Dict
from queue import Queue
from collections import deque


# class QueueManager(BaseManager):
#     queue = Queue()
#
#     def get_queue(self) -> Queue:
#         pass
#
#
# DictProxy = TypeVar('DictProxy')


class DataManager(SyncManager):
    data_dict = {}
    data_queue = Queue()
    data_deque = None
    data_list = []

    @classmethod
    def set_data_deque(cls, maxlen):
        cls.data_deque = deque(maxlen=maxlen)

    def get_dict(self) -> Dict:
        ...

    def get_queue(self) -> Queue:
        ...

    def get_deque(self) -> deque:
        ...

    def get_list(self) -> List:
        ...


def register_server_methods():
    DataManager.register('get_dict', callable=lambda: DataManager.data_dict)
    DataManager.register('get_queue', callable=lambda: DataManager.data_queue)
    DataManager.register('get_deque', callable=lambda: DataManager.data_deque)
    DataManager.register('get_list', callable=lambda: DataManager.data_list)


def register_client_methos():
    DataManager.register('get_dict')
    DataManager.register('get_queue')
    DataManager.register('get_deque')
    DataManager.register('get_list')


if __name__ == "__main__":
    from sparrow.multiprocess.config import Config

    config = Config()
    register_server_methods()
    manager = DataManager(address=(config.host, config.port),
                          authkey=config.authkey)
    manager.get_server().serve_forever()
