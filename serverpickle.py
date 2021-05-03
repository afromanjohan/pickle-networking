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
        self.transport.write(pickle.dumps("Hello from server!"))


    def update_everyone(self, data, event):
        for value in self.users.values():
            value.transport.write(pickle.dumps(f':::{data} has {event} to the server:::'))

    def add_user(self, data):
        #data = decoded string
        if data in self.users:
            self.transport.write(pickle.dumps("The name is already taken"))
        else:
            self.name = data
            self.users[data] = self
            self.update_everyone(data, "connected")       


    def dataReceived(self, data):
        data = pickle.loads(data)
        if not self.name:
            self.add_user(data)
        else:
            if data == "status":
                self.transport.write(pickle.dumps(f'{len(self.users)}'))
            elif data == "members":
                package = []
                for client in self.users:
                    package.append(client)
                self.transport.write(pickle.dumps(package))
            else:
                for client in self.users:
                    if self.users[client] != self:
                        self.users[client].transport.write(pickle.dumps(f':::{self.name}::: {data} '))

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