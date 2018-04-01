#!/usr/bin/env python
import datetime
import pexpect
import getpass
import re
import smtplib
import time
from time import localtime, strftime
from termcolor import colored
username = ''
password = ''
fromaddr = ''
toaddrs = ''

rogue_device_detected = 0
_time = 0

log_in_account = ''
log_in_password = ''  # Password
    

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
    
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()), 'Login to ZD')
    
    p.expect('Please login:')
    p.sendline(log_in_account)  # Usename
    p.sendline(log_in_password)  # Password
    
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()), 'Login succeeded')
    
    p.expect('ruckus>')
    p.sendline('enable')    # Enable mode
    idx = p.expect(['ruckus#', 'A privileged user is already logged in.'])
    if idx != 0:    # Someone already in.
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()),
            'A privileged user is already logged in, try in the next cycle.')
        p.sendline('exit')
        p.close()
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
    
    # this line is for testing
    # valid_SSID.append('NTU')

    p.sendline('show rogue-devices')
    p.expect('Current Active Rogue Devices:\r\r\n')
    p.expect('ruckus#')
    
    data = p.before
    entries = re.split('Rogue Devices:\r\r\n', data.decode('utf-8'))[1:]
    rogue_devices = []
    for entry in entries:
        #check for empty line
        if len(re.findall('Mac Address= (\S+)\r\r\n', entry)) == 0:
            continue
        Mac = re.findall('Mac Address= (\S+)\r\r\n', entry)[0]
        Channel = re.findall('Channel= (\S+)\r\r\n',entry)[0]
        Radio = re.findall('Radio= (\S+)\r\r\n',entry)[0]
        Type = re.findall('Type= (\S+)\r\r\n',entry)[0]
        Encryption = re.findall('Encryption= (\S+)\r\r\n',entry)[0]
     	#check for empty SSID
        ###assume SSID is at most two segments seperated by spaces!!!!!
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
        if device['SSID'] in valid_SSID :
            rogue_device_detected = 1
            print(colored(strftime("%Y-%m-%d %H:%M:%S", localtime()) + ' Rogue device detected, mailing','red',attrs = ['bold']))
            try:
                mailing(device)
            except smtplib.SMTPException:
                print(colored(strftime("%Y-%m-%d %H:%M:%S", localtime())+ ' Mailing failed !!!!!!','red',attrs = ['bold']))
    
    p.sendline('exit')
    p.close()
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()), 'Logout from ZD')


if __name__ == '__main__':
            
    _time = int(raw_input('Please Enter the interval(minute) between cycles: '))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    #get zd account
    while True:
        try:
            log_in_account = raw_input('Please login: ')     # username
            log_in_password = getpass.getpass('Password: ')  # Password
            p = pexpect.spawn('ssh 10.3.7.253')
            p.expect('Please login:')
            p.sendline(log_in_account)  # Usename
            p.sendline(log_in_password)  # Password
            p.expect('ruckus>',timeout = 1)
            p.sendline('exit')
            p.close() 
            break
        except pexpect.TIMEOUT:
            print("your username or password is incorrect, please try again") 
    
    #get user gmail account,zd account
    while True:
        try:
            username = raw_input('Please Enter your Gmail Account: ')
            password = getpass.getpass('Password: ')
            server.login(username,password)
            break
        except smtplib.SMTPException:
            print("your username or password is incorrect, please try again") 
            continue
    fromaddr = 'zone director';
    toaddrs = raw_input('Please Enter your Gmail toaddr: ')
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()), 'Start')
    
    #start scanning for rogue devices
    while True:
        try:
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()), 'Start scanning for rogue devices')
            rogue_device_detected = 0
            main()
        except pexpect.TIMEOUT:
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()),'Timeout.')
        time.sleep(60*_time)
        if  rogue_device_detected == 0:
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()),'Finish scanning, no rogue device detected')
        else:
            print(colored(strftime("%Y-%m-%d %H:%M:%S", localtime())+' Finish scanning, some rogue devices detected!!!','red',attrs = ['bold']))
    
    server.quit()
    print(datetime.datetime.now().isoformat(), 'End')
