import zmq
from sparrow import MeasureTime


class Client:
    def __init__(self, port):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def run(self):
        mt = MeasureTime().start()
        for i in range(1000):
            # self.socket.send_pyobj({"message": "你好, 服务器"})
            self.socket.send_pyobj("hello")
            # self.socket.send(b"hello")
            #  Get the reply.
            message = self.socket.recv_pyobj()
            # message = self.socket.recv()
        mt.show_interval("cost:")
        print(f"Received reply: {message}")


if __name__ == "__main__":
    client = Client(5555)
    client.run()
