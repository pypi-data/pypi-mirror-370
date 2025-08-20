import torch


class MemoryInfo:
    def __init__(self):
        self.last_memory = 0

    @staticmethod
    def get_memory_total():
        return torch.cuda.memory_allocated() / 1024 / 1024

    def get_memory_diff(self):
        total = self.get_memory_total()
        diff = total - self.last_memory
        self.last_memory = total
        return diff, total
