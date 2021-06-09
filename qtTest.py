import sys
import socket
import errno
import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication,
                               QVBoxLayout, QDialog, QLabel, QMainWindow)
from PySide6.QtCore import SIGNAL, QObject, QTimer
from testUI import Ui_MainWindow

class Chat(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.HEADER_LENGTH = 10
        self.setMaximumSize(1000,800)
        IP = "192.168.1.201"
        PORT = 8081
        self.my_username = "JourneyMage"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((IP, PORT))

        self.client_socket.setblocking(False)

        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username)

        self.chat_lines = []

        self.chat_refresh = QTimer()
        self.chat_refresh.setInterval(30)


        QObject.connect(self.chat_refresh, SIGNAL('timeout()'), self.chat_update)
        QObject.connect(self.message_line, SIGNAL('textChanged()'), self.send_message)

        self.chat_refresh.start()

    def send_message(self):
        message = self.message_line.toPlainText()
        if message.strip() and message[-1] == '\n':
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            self.chat_lines.append(f'{self.my_username} > {message}')
            message = message.encode('utf-8')
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)
            self.message_line.clear()
            self.chat_text.setText('\n'.join(self.chat_lines))
            self.chat_text.append('<a name="end">...<a>')
            self.chat_text.scrollToAnchor('end')

    def chat_update(self):
        # self.max_lines = self.chat_text.height() / (self.chat_text.fontInfo().pixelSize()+4)
        # if len(self.chat_lines) < self.max_lines:
        #     self.chat_text.setText('\n'.join(self.chat_lines))
        # else:
        #     self.chat_text.setText('\n'.join(self.chat_lines[-int(self.max_lines):]))
        # self.chat_text.setText('\n'.join(self.chat_lines))
        self.new_messages()
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
                self.chat_text.setText('\n'.join(self.chat_lines))
                self.chat_text.append('<a name="end">...<a>')
                self.chat_text.scrollToAnchor('end')
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

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    chat = Chat()
    chat.show()
    # Run the main Qt loop
    sys.exit(app.exec())
