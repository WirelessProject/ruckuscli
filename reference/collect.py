#!/usr/bin/env python

import datetime
import pexpect
import getpass
import re


def main():
    p = pexpect.spawn('ssh wifi.csie.ntu.edu.tw')
    p.expect('Please login:')
    p.sendline(raw_input('Please login: '))  # Usename
    p.sendline(getpass.getpass('Password: '))  # Password
    p.expect('ruckus>')
    p.sendline('enable')    # Enable mode
    idx = p.expect(['ruckus#', 'A privileged user is already logged in.'])
    if idx != 0:    # Someone already in.
        print(datetime.datetime.now().isoformat(),
            'A privileged user is already logged in.')
        return

    p.sendline('show ap all')
    p.expect('AP:\r\r\n  ID:')
    p.expect('ruckus#')
    data = p.before
    
    entries = re.split('\r\r\n    \d+:\r\r\n', data.decode('utf-8'))[1:]
    aps = []
    for entry in entries:
        mac = re.findall('MAC Address= (\S+)\r\r\n', entry)[0]
        model = re.findall('Model= (\S+)\r\r\n', entry)[0]
        name = re.findall('Description= (\S*)\r\r\n', entry)[0]
        ip = re.findall('IP Address= (\S+)\r\r\n', entry)[0]
        aps.append({
            'mac': mac,
            'model': model,
            'name': name,
            'ip': ip,
        })

    for ap in aps:
        p.sendline('show performance ap-radio5 mac {}'.format(ap['mac']))
        p.expect('ruckus#')
        data = p.before.decode('utf-8')
        try:
            cap = int(re.findall('Estimated Capacity= (\d+)\r\r\n', data)[0])
            dl = int(re.findall('Downlink= (\d+)\r\r\n', data)[0])
            ul = int(re.findall('Uplink= (\d+)\r\r\n', data)[0])
            rf = int(re.findall('RF pollution= (\d+)\r\r\n', data)[0])
            client = int(re.findall('Authorized clients= (\d+)\r\r\n', data)[0])
            print(ap, {
                'capacity': cap,
                'downlink': dl,
                'uplink': ul,
                'rfpollution': rf,
                'client': client,
            })
        except:
            pass

    p.sendline('exit')
    p.close()


if __name__ == '__main__':
    print(datetime.datetime.now().isoformat(), 'Start')
    try:
        main()
    except pexpect.TIMEOUT:
        print('Timeout.')
    print(datetime.datetime.now().isoformat(), 'End')
