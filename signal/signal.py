#!/usr/bin/env python

import datetime
import pexpect
import getpass
import re
import sys

def sort_ap(elem):
    if elem['clients'] == 0:
        return 1000
    else:
        return round(float(elem['total_signal']) / elem['clients'], 2)
def sort_user(elem):
    return elem['Signal']    

def main():
    p = pexpect.spawn('ssh 10.3.7.253')
    p.expect('Please login:')
    p.sendline(input('Please login: '))  # Usename
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
        name = re.findall('Description= (\S*)\r\r\n', entry)[0]
        user = []
        for arg in sys.argv:
            if (name == arg) or (len(sys.argv) == 1): 
                aps.append({
                    'mac': mac,
                    'name': name,
                    'total_signal': 0,
                    'clients': 0,
                    'user_info': user
                })
                break


    p.sendline('show current-active-clients all')
    p.expect('Current Active Clients:')
    p.expect('Last 300 Events/Activities:')
    data = p.before
    p.expect('ruckus#')
    entries = re.split('Clients:\r\r\n', data.decode('utf-8'))[1:]
    for entry in entries:
        access_point = re.findall('Access Point= (\S+)\r\r\n', entry)[0]
        signal = int(re.findall('Signal= (\d+)\r\r\n', entry)[0])
        for ap in aps:
            if access_point == ap['mac']:
                ap['total_signal'] += signal
                ap['clients'] += 1
                try:
                    ap['user_info'].append({
                        'Mac Address': re.findall('Mac Address= (\S*)\r\r\n', entry)[0], 
                        'OS/Type': re.findall('OS/Type= (.*)\r\r\n', entry)[0],
                        'Host Name': re.findall('Host Name= (.*)\r\r\n', entry)[0],
                        'User/IP': re.findall('User/IP= (\S*)\r\r\n', entry)[0],
                        'User/IPv6': re.findall('User/IPv6= (\S*)\r\r\n', entry)[0],
                        'Role': re.findall('Role= (\S*)\r\r\n', entry)[0],
                        'BSSID': re.findall('BSSID= (\S*)\r\r\n', entry)[0],
                        'Connect Since': re.findall('Connect Since=(.*)\r\r\n', entry)[0],
                        'Auth Method': re.findall('Auth Method= (\S*)\r\r\n', entry)[0],
                        'WLAN': re.findall('WLAN= (\S*)\r\r\n', entry)[0],
                        'VLAN': re.findall('VLAN= (\S*)\r\r\n', entry)[0],
                        'Channel': re.findall('Channel= (\S*)\r\r\n', entry)[0],
                        'Radio': re.findall('Radio= (\S*)\r\r\n', entry)[0],
                        'Signal': signal,
                        'Status': re.findall('Status= (\S*)\r\r\n', entry)[0],
                        })
                except:
                    pass
                break

    p.sendline('show wlan name csie stations')
    p.expect('Clients List:')
    p.expect('ruckus#')
    data = p.before
    entries = re.split('Client:\r\r\n', data.decode('utf-8'))[1:]
    for entry in entries:
        access_point = re.findall('Access Point= (\S*)\r\r\n', entry)[0]
        mac_add = re.findall('MAC Address= (\S*)\r\r\n', entry)[0]
        user_name = re.findall('User Name= (.*)\r\r\n', entry)[0]
        for ap in aps:
            if access_point == ap['mac']:
                for find_user in ap['user_info']:
                    if mac_add == find_user['Mac Address']:
                        find_user['User Name'] = user_name
                        break
                break

    p.sendline('show wlan name csie-5G stations')
    p.expect('Clients List:')
    p.expect('ruckus#')
    data = p.before
    entries = re.split('Client:\r\r\n', data.decode('utf-8'))[1:]
    for entry in entries:
        access_point = re.findall('Access Point= (\S*)\r\r\n', entry)[0]
        mac_add = re.findall('MAC Address= (\S*)\r\r\n', entry)[0]
        user_name = re.findall('User Name= (.*)\r\r\n', entry)[0]
        for ap in aps:
            if access_point == ap['mac']:
                for find_user in ap['user_info']:
                    if mac_add == find_user['Mac Address']:
                        find_user['User Name'] = user_name
                        break
                break

#sorting    
    for sort in sorted(aps, key=sort_ap):
            if sort['clients'] == 0:
                print("\tap name: ", sort['name'])
                print("\tap mac: ", sort['mac'])
                print("\taverage signal: no client")
                print()
            else:
                print("\tap name: ", sort['name'])
                print("\tap mac: ", sort['mac'])
                print("\taverage signal: ",  round(float(sort['total_signal']) / sort['clients'], 2))
                for print_user in sorted(sort['user_info'], key=sort_user):
                    for keys in print_user:
                        print("\t\t", keys, ":", print_user[keys])
                    print()

    p.sendline('exit')
    p.close()

if __name__ == '__main__':
    print(datetime.datetime.now().isoformat(), 'Start')
    try:
        main()
    except pexpect.TIMEOUT:
        print('Timeout.')
    print(datetime.datetime.now().isoformat(), 'End')
