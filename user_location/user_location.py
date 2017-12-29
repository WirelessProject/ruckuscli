#!/usr/bin/env python3

import datetime
import pexpect
import getpass
import re
import sys


wlan_list = ['csie', 'csie-5G']	# the wlans to scan through

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
	target_mac = []

	# find the access point the <target> using by `show wlan name <wlan> stations`
	for wlan in wlan_list:
		p.sendline('show wlan name {} stations'.format(wlan))
		p.expect('Clients List:')
		p.expect('ruckus#')
		data = p.before

		entries = re.split('\r\r\n  Client:\r\r\n', data.decode('utf-8'))[1:]

		for entry in entries:
			user = re.findall('User Name=(.*)\r\r\n', entry)
			mac_addr = re.findall('MAC Address=(.*)\r\r\n', entry)
			if user and user[0].strip().lower() == target.lower():
				ap_mac_addr = re.findall('Access Point=(.*)\r\r\n', entry)
				if ap_mac_addr:
					ap_used.append(ap_mac_addr[0].strip())
				if mac_addr:
					target_mac.append(mac_addr[0].strip())
	assert(len(ap_used) == len(target_mac))

	

	OS_type_list = []
	hostname_list = []

	# get the device OS type & host name by `show current-active-clients mac <device MAC addr>`

	for mac_addr in target_mac:
		p.sendline('show current-active-clients mac {}'.format(mac_addr))
		p.expect('Current Active Clients:\r\r\n  Clients:\r\r\n')
		p.expect('ruckus#')
		data = p.before.decode('utf-8')

		OS_type = re.findall('OS/Type=(.*)\r\r\n', data)
		hostname = re.findall('Host Name=(.*)\r\r\n', data)

		if OS_type:
			OS_type_list.append(OS_type[0].strip())
		if hostname:
			hostname_list.append(hostname[0].strip())

	assert(len(OS_type_list) == len(hostname_list))


	location = []

	# get the device_name(location) of each AP by `show ap mac <AP MAC addr>`
	for ap in ap_used:
		p.sendline('show ap mac {}'.format(ap))
		p.expect('AP:\r\r\n  ID:\r\r\n')
		p.expect('ruckus#')
		data = p.before.decode('utf-8')

		ap_name = re.findall('Device Name=(.*)\r\r\n', data)
		if ap_name:
			location.append(ap_name[0].strip())

	assert(len(OS_type_list) == len(location))

	data = sorted(zip(location, OS_type_list, hostname_list), key=lambda x: x[0])
	data = ["{}.\nLocation :{}\nOS/Type :{}\nHost Name :{}\n".format(i+1, *d) for i, d in enumerate(data)]

	print()
	if location:
		print("The person might be in the following location(s):", "-"*50, *(data), "-"*50, sep='\n')
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

