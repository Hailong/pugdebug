# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import socket

from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from pugdebug.message_parser import PugdebugMessageParser


class PugdebugServer(QThread):

    mutex = None

    sock = None

    parser = None

    action = None

    data = None

    transaction_id = 0

    xdebug_encoding = 'iso-8859-1'

    thread_finished_signal = pyqtSignal(type([]))
    server_connected_signal = pyqtSignal(type({}))
    server_stopped_signal = pyqtSignal()
    server_stepped_signal = pyqtSignal(type({}))
    server_got_variables_signal = pyqtSignal(object)
    server_set_init_breakpoints_signal = pyqtSignal(bool)
    server_set_breakpoint_signal = pyqtSignal(bool)
    server_removed_breakpoint_signal = pyqtSignal(object)
    server_listed_breakpoints_signal = pyqtSignal(type([]))

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.mutex = QMutex()
        self.parser = PugdebugMessageParser()

        self.thread_finished_signal.connect(self.handle_thread_finished)

    def run(self):
        self.mutex.lock()

        data = self.data

        if self.action == 'connect':
            response = self.__connect_server()
        elif self.action == 'stop':
            response = self.__stop()
        elif self.action == 'step_run':
            response = self.__step_run()
        elif self.action == 'step_into':
            response = self.__step_into()
        elif self.action == 'step_over':
            response = self.__step_over()
        elif self.action == 'step_out':
            response = self.__step_out()
        elif self.action == 'variables':
            response = self.__get_variables()
        elif self.action == 'init_breakpoint_set':
            response = self.__set_init_breakpoints(data)
        elif self.action == 'breakpoint_set':
            response = self.__set_breakpoint(data)
        elif self.action == 'breakpoint_remove':
            response = self.__remove_breakpoint(data)
        elif self.action == 'breakpoint_list':
            response = self.__list_breakpoints()

        self.thread_finished_signal.emit([response])

        self.mutex.unlock()

    def handle_thread_finished(self, thread_result):
        if self.action == 'connect':
            self.server_connected_signal.emit(thread_result.pop())
        elif self.action == 'stop':
            self.server_stopped_signal.emit()
        elif self.action == 'step_run':
            self.server_stepped_signal.emit(thread_result.pop())
        elif self.action == 'step_into':
            self.server_stepped_signal.emit(thread_result.pop())
        elif self.action == 'step_over':
            self.server_stepped_signal.emit(thread_result.pop())
        elif self.action == 'step_out':
            self.server_stepped_signal.emit(thread_result.pop())
        elif self.action == 'variables':
            self.server_got_variables_signal.emit(thread_result.pop())
        elif self.action == 'init_breakpoint_set':
            self.server_set_init_breakpoints_signal.emit(thread_result.pop())
        elif self.action == 'breakpoint_set':
            self.server_set_breakpoint_signal.emit(thread_result.pop())
        elif self.action == 'breakpoint_remove':
            self.server_removed_breakpoint_signal.emit(thread_result.pop())
        elif self.action == 'breakpoint_list':
            self.server_listed_breakpoints_signal.emit(thread_result.pop())

    def connect(self):
        self.action = 'connect'
        self.start()

    def is_connected(self):
        return self.sock is not None

    def disconnect(self):
        self.sock.close()
        self.sock = None

    def stop(self):
        self.action = 'stop'
        self.start()

    def step_run(self):
        self.action = 'step_run'
        self.start()

    def step_into(self):
        self.action = 'step_into'
        self.start()

    def step_over(self):
        self.action = 'step_over'
        self.start()

    def step_out(self):
        self.action = 'step_out'
        self.start()

    def get_variables(self):
        self.action = 'variables'
        self.start()

    def set_init_breakpoints(self, breakpoints):
        self.action = 'init_breakpoint_set'
        self.data = breakpoints
        self.start()

    def set_breakpoint(self, breakpoint):
        self.action = 'breakpoint_set'
        self.data = breakpoint
        self.start()

    def remove_breakpoint(self, breakpoint_id):
        self.action = 'breakpoint_remove'
        self.data = breakpoint_id
        self.start()

    def list_breakpoints(self):
        self.action = 'breakpoint_list'
        self.start()

    def __connect_server(self):
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.settimeout(None)

        response = None

        try:
            socket_server.bind(('', 9000))
            response = self.__init_connection(socket_server)
        except OSError:
            print(OSError.strerror())
            print("Socket bind failed")
        finally:
            socket_server.close()

        return response

    def __init_connection(self, socket_server):
        socket_server.listen(5)

        self.sock, address = socket_server.accept()
        self.sock.settimeout(None)
        response = self.__receive_message()

        init_message = self.parser.parse_init_message(response)

        command = 'feature_set -i %d -n max_depth -v 9' % (
            self.__get_transaction_id()
        )
        response = self.__send_command(command)

        command = 'feature_set -i %d -n max_children -v 512' % (
            self.__get_transaction_id()
        )
        response = self.__send_command(command)

        command = 'feature_set -i %d -n max_data -v 4096' % (
            self.__get_transaction_id()
        )
        response = self.__send_command(command)

        return init_message

    def __stop(self):
        command = 'stop -i %d' % self.__get_transaction_id()
        self.__send_command(command)

        return True

    def __step_run(self):
        command = 'run -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_into(self):
        command = 'step_into -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_over(self):
        command = 'step_over -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_out(self):
        command = 'step_out -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __do_step_command(self, command):
        response = self.__send_command(command)

        response = self.parser.parse_continuation_message(response)

        return response

    def __get_variables(self):
        command = 'context_names -i %d' % self.__get_transaction_id()
        response = self.__send_command(command)

        contexts = self.parser.parse_variable_contexts_message(response)

        variables = {}

        for context in contexts:
            context_id = int(context['id'])
            command = 'context_get -i %d -c %d' % (
                self.__get_transaction_id(),
                context_id
            )
            response = self.__send_command(command)

            var = self.parser.parse_variables_message(response)
            variables[context['name']] = var

        return variables

    def __set_init_breakpoints(self, breakpoints):
        all_successful = True

        for breakpoint in breakpoints:
            response = self.__set_breakpoint(breakpoint)
            if response is False:
                all_successful = False

        return all_successful

    def __set_breakpoint(self, breakpoint):
        command = 'breakpoint_set -i %d -t %s -f %s -n %d' % (
            self.__get_transaction_id(),
            'line',
            breakpoint['path'],
            breakpoint['line_number']
        )
        response = self.__send_command(command)

        return self.parser.parse_breakpoint_set_message(response)

    def __remove_breakpoint(self, breakpoint_id):
        command = 'breakpoint_remove -i %d -d %d' % (
            self.__get_transaction_id(),
            breakpoint_id
        )
        response = self.__send_command(command)

        return self.parser.parse_breakpoint_remove_message(response)

    def __list_breakpoints(self):
        command = 'breakpoint_list -i %d' % self.__get_transaction_id()
        response = self.__send_command(command)

        breakpoints = self.parser.parse_breakpoint_list_message(response)

        return breakpoints

    def __send_command(self, command):
        self.sock.send(bytes(command + '\0', 'utf-8'))
        return self.__receive_message()

    def __receive_message(self):
        length = self.__get_message_length()
        body = self.__get_message_body(length)

        return body

    def __get_message_length(self):
        length = ''

        while True:
            character = self.sock.recv(1)

            if self.__is_eof(character):
                self.close()

            if character.isdigit():
                length = length + character.decode(self.xdebug_encoding)

            if character.decode(self.xdebug_encoding) == '\0':
                if length == '':
                    return 0
                return int(length)

    def __get_message_body(self, length):
        body = ''

        while length > 0:
            data = self.sock.recv(length)

            if self.__is_eof(data):
                self.close()

            body = body + data.decode(self.xdebug_encoding)

            length = length - len(data)

        self.__get_null()

        return body

    def __get_null(self):
        while True:
            character = self.sock.recv(1)

            if self.__is_eof(character):
                self.close()

            if character.decode(self.xdebug_encoding) == '\0':
                return

    def __is_eof(self, data):
        return data.decode(self.xdebug_encoding) == ''

    def __get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
