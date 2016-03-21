#! /usr/bin/python

import requests
import time

class HTTPInterface:
    def __init__(self, IP, port=80):
        self.port = port
        self.url = 'http://' + IP + ':' + str(port)

    def set_ip(self, IP):
        self.url = 'http://' + IP + ':' + str(self.port)

    def get_bistream_id(self):
        r = requests.get(self.url + '/api/bitstream_id')
        return r.text

    def ping(self):
        r = requests.post(self.url + '/api/ping', data={})
        
    def deploy_remote_instrument(self, name, version):
        """ Deploy a remotely available instrument
            
            Args:
                - name: Instrument name
                - version: Instrument version
        """
        zip_filename = name + '-' + version + '.zip'
        r = requests.post(self.url + '/api/deploy/remote/' + zip_filename, data={})

    def deploy_local_instrument(self, name, version):
        zip_filename = name + '-' + version + '.zip'
        print('Deploying ' + zip_filename)
        try:
            r = requests.post(self.url + '/api/deploy/local/' + zip_filename, data={} , timeout=1.0)
        except Exception,e: 
            print("[error] " + str(e))
            #print('Timeout occured')
            pass

    def remove_local_instrument(self, name, version):
        zip_filename = name + '-' + version + '.zip'
        r = requests.get(self.url + '/api/remove/local/' + zip_filename)
        return r.text

    def get_local_instruments(self):
        try:
            r = requests.get(self.url + '/api/get_local_instruments')
            return r.json()
        except Exception,e: 
            print("[error] " + str(e))
            return {}

    def install_instrument(self, instrument_name):
        instruments = self.get_local_instruments()
        if instruments:
            for name, shas in instruments.items():
                if name == instrument_name and len(shas) > 0:
                    self.deploy_local_instrument(name, shas[0])
                    time.sleep(0.5)
                    return
        raise ValueError("Instrument " + instrument_name + " not found")

if __name__ == "__main__":
    http = HTTPInterface('192.168.1.21')
    print(http.get_bistream_id())
#    http.ping()
#    http.deploy_remote_instrument('spectrum', '06ee48f')
#    http.deploy_local_instrument('oscillo', '06ee48f')
#    print(http.remove_local_instrument('oscillo', '06ee48f'))
    print(http.get_local_instruments())
#    http.install_instrument("spectrum")