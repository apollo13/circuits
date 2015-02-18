# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""
import itertools

from circuits.net.sockets import TCPServer
from circuits import handler, BaseComponent

from .protocol import Protocol


class Server(BaseComponent):
    """Server

    ...
    """

    channel = 'node'
    __protocols = {}

    def __init__(self, bind, channel=channel, receive_event_firewall=None,
                 send_event_firewall=None, **kwargs):
        super(Server, self).__init__(channel=channel, **kwargs)

        self.server = TCPServer(bind, channel=channel, **kwargs)
        self.server.register(self)
        self.__receive_event_firewall = receive_event_firewall
        self.__send_event_firewall = send_event_firewall

    def send(self, event, sock, noresult=False):
        iterator = self.__protocols[sock].send(event)
        if noresult:
            event.node_without_result = True
            try:
                next(iterator)
            except StopIteration:
                pass
        return iterator

    def send_to(self, event, socks):
        for sock in socks:
            self.send(event, sock, noresult=True)

    def send_all(self, event):
        self.send_to(event, list(self.__protocols))

    @handler('read')
    def _on_read(self, sock, data):
        self.__protocols[sock].add_buffer(data)

    @property
    def host(self):
        if hasattr(self, 'server'):
            return self.server.host

    @property
    def port(self):
        if hasattr(self, 'server'):
            return self.server.port

    def get_socks(self):
        return list(self.__protocols)

    @handler('connect')
    def __connect_peer(self, sock, host, port):
        self.__protocols[sock] = Protocol(
            sock=sock,
            server=self.server,
            receive_event_firewall=self.__receive_event_firewall,
            send_event_firewall=self.__send_event_firewall,
            channel=self.channel
        ).register(self)

    @handler('disconnect')
    def __disconnect_peer(self, sock):
        for s in self.__protocols.copy():
            try:
                s.getpeername()
            except:
                del(self.__protocols[s])
