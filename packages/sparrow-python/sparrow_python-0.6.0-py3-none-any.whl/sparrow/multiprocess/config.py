from attrs import define


@define
class Config:
    host: str = '0.0.0.0'
    port: int = 50001
    authkey: bytes = b'sparrow_authkey'


if __name__ == "__main__":
    config = Config(port=2222)
    print(config)
