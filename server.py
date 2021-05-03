from twisted.internet import reactor, protocol
from twisted.internet.protocol import ServerFactory as ServFactory, connectionDone
from twisted.internet.endpoints import TCP4ServerEndpoint
import pickle

class Server(protocol.Protocol):
    def __init__(self, users):
        self.users = users
        self.name = ""

    def connectionMade(self):
        print(f"Connection was made with: {self}")
        self.transport.write("Hello from server!".encode("utf-8"))


    def update_everyone(self, data, event):
        for value in self.users.values():
            value.transport.write(f':::{data} has {event} to the server:::'.encode("utf-8"))

    def add_user(self, data):
        #data = decoded string
        if data in self.users:
            self.transport.write("The name is already taken".encode("utf-8"))
        else:
            self.name = data
            self.users[data] = self
            self.update_everyone(data, "connected")       


    def dataReceived(self, data):
        data = data.decode("utf-8")
        if not self.name:
            self.add_user(data)
        else:
            if data == "status":
                self.transport.write(f'{len(self.users)}'.encode("utf-8"))
            else:
                for client in self.users:
                    if self.users[client] != self:
                        self.users[client].transport.write(f':::{self.name}::: {data} '.encode("utf-8"))

    def connectionLost(self, reason=connectionDone):
        self.disconnect()

    def disconnect(self):
        print(f"<{self.name} disconnected from the server>")
        self.update_everyone(self.name, "diconnected")
        del self.users[self.name]


class ServerFactory(ServFactory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return Server(self.users)


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 12345)
    endpoint.listen(ServerFactory())
    reactor.run()