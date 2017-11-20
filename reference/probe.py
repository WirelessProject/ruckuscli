import datetime
import pexpect
import re
from peewee import *


def parse_phyerr(data):
    total, ofdm, cck = re.findall('(\d+) PHY errors since clearing all stats \(rx_phyerr\)\r\n    (\d+) phy ofdm group\r\n    (\d+) phy cck group', data)[0]
    print(int(total), int(ofdm), int(cck))


def main():
    p = pexpect.spawn('ssh wifi.csie.ntu.edu.tw')
    p.expect('Please login:')
    p.sendline(input('Please login: '))  # Usename
    p.sendline(input('Password: '))  # Password
    p.expect('ruckus>')
    p.sendline('enable')    # Enable mode
    idx = p.expect(['ruckus#', 'A privileged user is already logged in.'])
    if idx != 0:    # Someone already in.
        print(datetime.datetime.now().isoformat(),
            'A privileged user is already logged in.')
        return

    p.sendline('debug')    # Debug mode
    p.expect('You have all rights in this mode.\r\r\n')
    p.expect('ruckus\(debug\)# ')

    p.sendline('remote_ap_cli -a 30:87:d9:31:52:c0 get radiostats wlan0')
    p.expect('ruckus\(debug\)# ')
    data = p.before.decode('utf-8')
    phydata = re.findall('------------ PHY Error Stats ------------\r\n(.*)------------ Airtime Stats ------------\r\n', data, flags=re.DOTALL)[0]
    parse_phyerr(phydata)

    p.sendline('quit')
    p.sendline('exit')
    p.close()


if __name__ == '__main__':
    print(datetime.datetime.now().isoformat(), 'Start')
    try:
        main()
    except pexpect.TIMEOUT:
        print('Timeout.')
    print(datetime.datetime.now().isoformat(), 'End')
