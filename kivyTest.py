import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty
import socket
import errno
import sys


class ChatScreen(BoxLayout):
    widget_text = StringProperty('')


def set_focus(widget):
    widget.focus = True


class ChatApp(App):
    def build(self):
        self.HEADER_LENGTH = 10

        IP = "192.168.1.201"
        PORT = 8081
        self.my_username = "JourneyMage"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((IP, PORT))

        self.client_socket.setblocking(False)

        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username)

        kivy.require('2.0.0')

        self.chat_lines = []
        self.lines = 0

        event = Clock.schedule_interval(lambda dt: self.new_messages(), 1 / 30.)
        Clock.schedule_interval(lambda dt: self.update_chat(), 1 / 30.)
        return ChatScreen()

    def send_message(self):
        message = self.root.ids.MessageBox.text
        if message:
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            self.chat_lines.append(f'{self.my_username} > {message}')
            message = message.encode('utf-8')
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)
        self.root.ids.MessageBox.text = ''
        Clock.schedule_once(lambda dt: set_focus(self.root.ids.MessageBox), 0)

    def update_chat(self):
        self.max_lines = self.root.ids.label1.text_size[1] / (self.root.ids.label1.font_size + 3)
        if len(self.chat_lines) < self.max_lines:
            self.root.widget_text = '\n'.join(self.chat_lines)
        else:
            self.root.widget_text = '\n'.join(self.chat_lines[-int(self.max_lines):])

    def new_messages(self):
        # print(self.max_lines)
        try:
            while True:
                username_header = self.client_socket.recv(self.HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')
                message_header = self.client_socket.recv(self.HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')
                self.chat_lines.append(f'{username} > {message}')
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # We just did not receive anything

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()
        # print(self.lines < self.max_lines)
        # print(self.root.ids.MessageBox.focus)
        # print(self.root.widget_text)
        # print(chat_lines)


ChatApp().run()
