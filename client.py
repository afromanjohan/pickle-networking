from twisted.internet import reactor, protocol
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
import pickle


class Client(protocol.Protocol):
    def __init__(self):
        reactor.callInThread(self.send_message)

    def send_message(self):
        while True:
            self.transport.write(input().encode("utf-8"))


    def dataReceived(self, data):
        data = data.decode("utf-8")
        print(data)
        


class ClientFactory(ClFactory):
    def clientConnectionLost(self, connector, unused_reason):
        self.retry(connector)

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        self.retry(connector)

    def buildProtocol(self, addr):
        return Client()


if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 12345)
    endpoint.connect(ClientFactory())
    reactor.run()