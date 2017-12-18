#!/usr/bin/env python3

import datetime
import pexpect
import getpass
import re
import sys


wlan_list = ['csie', 'csie-5G']	# the wlan to scan

def main():
	p = pexpect.spawn('ssh wifi.csie.ntu.edu.tw')

	while True:
		p.expect('Please login:')
		p.sendline(input('Please login: '))  # Usename
		p.sendline(getpass.getpass('Password: '))  # Password
		idx = p.expect(['ruckus>', 'Login incorrect'])
		if idx != 0:
			print("Login incorrect\n")
		else:
			break

	p.sendline('enable')	# Enable mode
	idx = p.expect(['ruckus#', 'A privileged user is already logged in.'])
	if idx != 0:	# Someone already in.
		print(datetime.datetime.now().isoformat(),
			'A privileged user is already logged in.')
		return

	target = sys.argv[1]	# target = userid; the user whom we want to find
	ap_used = []	# the list of access point connected by the target user

	# find the access point the <target> using by `show wlan name <wlan> stations`
	for wlan in wlan_list:
		p.sendline('show wlan name {} stations'.format(wlan))
		p.expect('Clients List:')
		p.expect('ruckus#')
		data = p.before

		entries = re.split('\r\r\n  Client:\r\r\n', data.decode('utf-8'))[1:]
		# print(entries)
		for entry in entries:
			user = re.findall('User Name=\s*(\S*)\r\r\n', entry)
			if user and user[0].lower() == target.lower():
				ap = re.findall('Access Point=\s*(\S*)\r\r\n', entry)
				if ap:
					ap_used.append(ap[0])

	location = set()

	# get the device_name(location) of each AP by `show ap mac <AP MAC addr>`
	for ap in ap_used:
		p.sendline('show ap mac {}'.format(ap))
		p.expect('AP:\r\r\n  ID:\r\r\n')
		p.expect('ruckus#')
		data = p.before.decode('utf-8')

		dev_name = re.findall('Device Name=\s*(\S*)\r\r\n', data)
		if dev_name:
			location.add(dev_name[0])

	print()
	if location:
		print("The person might in the following location(s):", "-"*50, *sorted(location), "-"*50, sep='\n')
	else:
		print("Not found, the person you are looking for is not connecting", '/'.join(wlan_list), '.')

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

