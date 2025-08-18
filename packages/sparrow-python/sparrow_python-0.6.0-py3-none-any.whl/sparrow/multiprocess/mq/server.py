import zmq


class Server:
    def __init__(self, port):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")

    def run(self, func, *args, **kwargs):
        while True:
            #  Wait for next request from client
            # message = self.socket.recv()
            # self.socket.send(b"world")
            message = self.socket.recv_pyobj()
            result = func(*args, **kwargs)
            self.socket.send_pyobj(result)


if __name__ == "__main__":
    server = Server(5555)


    def add(a, b):
        return a + b


    server.run(add, 1, 1)
