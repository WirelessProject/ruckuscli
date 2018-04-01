#!/usr/bin/env python

import datetime
import pexpect
import getpass
import re
import sys
import time
import datetime

def main():
	p = pexpect.spawn('ssh 10.3.7.253')
	p.expect('Please login:')
	p.sendline(input('Please login: '))  # Usename
	p.sendline(getpass.getpass('Password: '))  # Password
	p.expect('ruckus>')
	p.sendline('enable')	# Enable mode
	idx = p.expect(['ruckus#', 'A privileged user is already logged in.'])
	if idx != 0:	# Someone already in.
		print(datetime.datetime.now().isoformat(),
			'A privileged user is already logged in.')
		return


	MacList = [['30:87:d9:31:79:e0', '30:87:d9:31:7f:20', '30:87:d9:31:52:40', '30:87:d9:31:97:40', '30:87:d9:31:6b:a0'], ['30:87:d9:31:83:00', '30:87:d9:31:99:40', '30:87:d9:31:59:80', '30:87:d9:31:96:e0', '30:87:d9:31:55:40', '30:87:d9:31:98:c0']]
	index = (datetime.datetime.today().weekday()) % 2
	for ApMac in MacList[index]:
		p.sendline('debug')	# Debug Mode
		p.expect('You have all rights in this mode.')
		p.expect('#')
		RestartCommand = "restart-ap " + ApMac
		print ("restarting " + ApMac)
		p.sendline(RestartCommand)
		p.expect("The command was executed successfully.")
		print ("command executed")
		time.sleep(160)
		print("after restart, checking status...")
		p.sendline("quit")
		p.expect("ruckus#")
		CheckCommand = "show ap mac " + ApMac
		p.sendline(CheckCommand)
		try:
			p.expect("LAN Port:", timeout=10)
			print('restart succeeded')
		except pexpect.TIMEOUT:
			print('timeout, restart failed')
		



if __name__ == '__main__':
	print(datetime.datetime.now().isoformat(), 'Start')
	try:
		main()
	except pexpect.TIMEOUT:
		print('Timeout.')
	print(datetime.datetime.now().isoformat(), 'End')