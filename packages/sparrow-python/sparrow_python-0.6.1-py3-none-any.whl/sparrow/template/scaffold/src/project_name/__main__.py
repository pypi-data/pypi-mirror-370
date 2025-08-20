import fire


class Cli:
    def run(self):
        ...

def main():
    fire.Fire(Cli)
