# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QCursor

import json
import os
import time
from lase.core import KClient, HTTPInterface


class ConnectWidget(QtGui.QWidget):
    def __init__(self, parent, ip_path=None):
        super(ConnectWidget, self).__init__()

        self.parent = parent
        self.ip_path = ip_path
        self.is_connected = False

        # IP address
        self.create_ip_layout()

        # Connect button and connection information
        self.lay_connection = QtGui.QHBoxLayout()
        self.connect_button = QtGui.QPushButton()
        self.connect_button.setStyleSheet('QPushButton {color: green;}')
        self.connect_button.setText('Connect')
        self.connect_button.setFixedWidth(80)
        self.connection_info = QtGui.QLabel('')
        self.lay_connection.addWidget(self.connect_button)
        self.lay_connection.addWidget(self.connection_info)

        # Add layouts to main layout
        self.lay = QtGui.QVBoxLayout()
        self.lay.addLayout(self.lay_ip)
        self.lay.addLayout(self.lay_connection)
        self.setLayout(self.lay)

        if not os.path.exists(self.ip_path):
            os.makedirs(self.ip_path)

        if os.path.exists(self.ip_path):
            try:
                with open(os.path.join(self.ip_path, 'ip_address' + '.json')) as fp:
                    json_data = fp.read()
                    parameters = json.loads(json_data)
                    IP = parameters['TCP_IP']
            except:
                IP = ['192', '168', '1', '1']
            self.set_text_from_ip(IP)

        self.set_host_from_text()
        self.http = HTTPInterface(self.host)

        self.line[0].textChanged.connect(lambda: self.ip_changed(0))
        self.line[1].textChanged.connect(lambda: self.ip_changed(1))
        self.line[2].textChanged.connect(lambda: self.ip_changed(2))
        self.line[3].textChanged.connect(lambda: self.ip_changed(3))

        self.connect_button.clicked.connect(self.connect_onclick)
        
    def create_ip_layout(self):
        self.lay_ip = QtGui.QHBoxLayout()
        self.line = []
        for i in range(4):
            self.line.append(QtGui.QLineEdit())
            self.line[i].setFixedWidth(40)
            self.line[i].setAlignment(QtCore.Qt.AlignCenter)

        self.point = []
        for i in range(3):
            self.point.append(QtGui.QLabel('.'))

        self.lay_ip.addWidget(QtGui.QLabel('IP address: '))

        for i in range(3):
            self.lay_ip.addWidget(self.line[i])
            self.lay_ip.addWidget(self.point[i])
        self.lay_ip.addWidget(self.line[3])

    def set_text_from_ip(self, ip):
        for i in range(4):
            self.line[i].setText(str(ip[i]))

    def set_host_from_text(self):
        self.host = ''
        for i in range(3):
            self.host += self.line[i].text() + '.'
        self.host += self.line[3].text()
        self.host = str(self.host)

    def get_ip_from_text(self):
        ip = []
        for i in range(4):
            ip.append(str(self.line[i].text()))
        return ip

    def ip_changed(self, index):
        self.set_host_from_text()
        parameters = {}
        parameters['TCP_IP'] = self.get_ip_from_text()
        if not os.path.exists(self.ip_path):
            os.makedirs(self.ip_path)
        with open(os.path.join(self.ip_path, 'ip_address' + '.json'), 'w') as fp:
            json.dump(parameters, fp)
        if self.line[index].cursorPosition() == 3 and index < 3:
            self.line[index+1].setFocus()
            self.line[index+1].selectAll()

    def connect_to_tcp_server(self):
        self.client = KClient(self.host, verbose=False)
        n_steps_timeout = 100
        cnt_timeout = 0

        while not self.client.is_connected:
            time.sleep(0.015)
            cnt_timeout += 1

            if cnt_timeout > n_steps_timeout:
                self.connection_info.setText(
                    'Failed to connect to host\nCheck IP address')
                self._set_disconnect()
                QApplication.restoreOverrideCursor()
                return False
        QApplication.restoreOverrideCursor()
        return True

    def _set_disconnect(self):
        self.is_connected = False
        self.connect_button.setStyleSheet('QPushButton {color: green;}')
        self.connect_button.setText('Connect')
        self.available_instruments = {}
        self.parent.set_disconnected()
        
    def connect_onclick(self):
        if not self.is_connected: # Connect
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.connection_info.setText('Disconnected')
            self._set_disconnect()
            self.connection_info.setText('Connecting to ' + self.host + ' ...')
        
            try:
                self.available_instruments = self.http.get_local_instruments()
            except:
                self.connection_info.setText('Cannot send requests to host\nCheck IP address')
                QApplication.restoreOverrideCursor()
                return

            if not "oscillo" in self.available_instruments:
                self.connection_info.setText("Instrument oscillo not available on host")
                QApplication.restoreOverrideCursor()
                return
                
            if not "spectrum" in self.available_instruments:
                self.connection_info.setText("Instrument spectrum not available on host")
                QApplication.restoreOverrideCursor()
                return
                
            # We load by default the oscillo instrument 
            # and connect with tcp-server to check the connection
            if not self.parent.install_instrument("oscillo"):
                return            
            
            self.connection_info.setText('Connected to ' + self.host)
            self.is_connected = True
            self.connect_button.setStyleSheet('QPushButton {color: red;}')
            self.connect_button.setText('Disconnect')
            self.parent.set_connected()
            QApplication.restoreOverrideCursor()
        else: # Disconnect
            if hasattr(self, 'client'):
                self.client.__del__()
            self.connection_info.setText('Disconnected')
            self._set_disconnect()
