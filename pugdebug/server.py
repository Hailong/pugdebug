# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QByteArray, pyqtSignal
from PyQt5.QtNetwork import QTcpServer, QHostAddress

class PugdebugServer(QTcpServer):

    sock = None

    last_message = ''

    xdebug_encoding = 'iso-8859-1'

    last_message_read_signal = pyqtSignal()

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.newConnection.connect(self.handle_new_connection)

    def connect(self):
        if self.isListening():
            return True

        self.listen(QHostAddress.Any, 9000)

    def cleanup(self):
        self.sock = None
        self.last_message = ''

    def handle_new_connection(self):
        if self.hasPendingConnections():
            self.sock = self.nextPendingConnection()
            self.sock.readyRead.connect(self.handle_ready_read)

    def command(self, command):
        if not self.sock is None:
            self.sock.write(bytes(command + '\0', 'utf-8'))

    def handle_ready_read(self):
        self.last_message = self.receive_message()
        self.last_message_read_signal.emit()

    def read_last_message(self):
        self.last_message = self.receive_message()

    def get_last_message(self):
        return self.last_message

    def receive_message(self):
        if self.sock is None:
            return ''

        message = self.sock.readAll().data().decode(self.xdebug_encoding)

        message_parts = message.split("\0")

        if len(message_parts) == 3:
            return message_parts[1]
        return ''
