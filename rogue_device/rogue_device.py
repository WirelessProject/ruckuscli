#!/usr/bin/env python
import datetime
import pexpect
import getpass
import re
import smtplib

username = ''
password = ''
fromaddr = ''
toaddrs = ''

def mailing(device):
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	msg = "\r\n".join([
		"From: user_me@gmail.com",
		"To: user_you@gmail.com",
		"Subject: csie Rogue Device discovered !!!",
		"Mac = %s" % (device['Mac']),
    	"Channel = %s" % (device['Channel']),
		"Radio = %s " %(device['Radio']),
		"Type = %s" % (device['Type']),
		"Encryption = %s" % (device['Encryption']),
		"SSID = %s" % (device['SSID']),
		"Last_Detected = %s" %(device['Last_Detected']),
	  ])
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()

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
    p.sendline('show wlan-group all')
    p.expect('ruckus#')
    data = p.before
    data = data.split('WLAN Service:')[1:]
    # get valid SSIDs
    valid_SSID = []
    for i in (data):
        tmp = re.findall('NAME= (\S+)\r\r\n', i)[0]
        if not tmp:
            continue
        valid_SSID.append(tmp)
    
    # valid_SSID.append('NTU')

    p.sendline('show rogue-devices')
    p.expect('Current Active Rogue Devices:\r\r\n')
    p.expect('ruckus#')
    data = p.before
    entries = re.split('Rogue Devices:\r\r\n', data.decode('utf-8'))[1:]
    rogue_devices = []
    for entry in entries:
            #empty line
        if len(re.findall('Mac Address= (\S+)\r\r\n', entry)) == 0:
            continue
        Mac = re.findall('Mac Address= (\S+)\r\r\n', entry)[0]
        Channel = re.findall('Channel= (\S+)\r\r\n',entry)[0]
        Radio = re.findall('Radio= (\S+)\r\r\n',entry)[0]
        Type = re.findall('Type= (\S+)\r\r\n',entry)[0]
        Encryption = re.findall('Encryption= (\S+)\r\r\n',entry)[0]
     	#check for empty SSID
        if len(re.findall('SSID= (\S+)\r\r\n',entry)) != 0:
            if len(re.findall('SSID= (\S+ \S+)\r\r\n',entry)) == 0:
                SSID = re.findall('SSID= (\S+)\r\r\n',entry)[0]
            else:
                SSID = re.findall('SSID= (\S+ \S+)\r\r\n',entry)[0]
        else:
            SSID = []
        Last_Detected = re.findall('Last Detected= (\S+ \S+)\r\r\n',entry)[0]
        rogue_devices.append({
                'Mac' : Mac,
                'Channel': Channel,
                'Radio' : Radio,
                'Type' : Type,
                'Encryption' : Encryption,
                'SSID' : SSID,
                'Last_Detected' : Last_Detected,
        	})
    for device in rogue_devices:
        print(device['SSID'])
        # if device['SSID'] == 'csie' or device['SSID'] == 'csie-5G':
        if device['SSID'] in valid_SSID :
            mailing(device)
        print(device['SSID'])

    p.sendline('exit')
    p.close()


if __name__ == '__main__':
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    while True:
        try:
            username = raw_input('Please Enter your Gmail Account: ')
            password = getpass.getpass('Password: ')
            server.login(username,password)
            break
        except smtplib.SMTPException:
            print("your username or password is incorrect, please try again") 
            continue
    fromaddr = username + '@gmail.com';
    toaddrs = raw_input('Please Enter your Gmail toaddr: ')
    print(datetime.datetime.now().isoformat(), 'Start')
    try:
        main()
    except pexpect.TIMEOUT:
        print('Timeout.')
    server.quit()
    print(datetime.datetime.now().isoformat(), 'End')