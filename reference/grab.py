#!/usr/bin/env python

import datetime
import getpass
import pexpect
from peewee import *


db = SqliteDatabase('activity.db')


class ActivityModel(Model):
    class Meta:
        database = db
        indexes = ((('timestamp',), False), (('user',), False))

    timestamp = DateTimeField()
    level = CharField()
    user = CharField(null=True)
    info = TextField()


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
    p.sendline('show events-activities')
    p.expect('Last 300 Events/Activities:\r\r\n')
    p.expect('ruckus#')
    data = p.before # Get events-activities
    p.sendline('exit')
    p.close()

    db.connect()
    try:
        db.create_tables([ActivityModel])   # Try to create table.
    except OperationalError:
        pass
        
    try:
        q = ActivityModel.select(ActivityModel.timestamp).order_by(
                ActivityModel.timestamp.desc()).get()
        lastdt = q.timestamp
    except:
        lastdt = datetime.datetime.fromtimestamp(0)

    entries = data.decode('utf-8').split('Activity:\r\r\n')
    objs = []
    hit = False
    for entry in entries:
        entry = entry.lstrip(' ').rstrip(' ')
        table = entry.split('\r\n')
        obj = {}
        for row in table:
            row = row.lstrip(' \r\n').rstrip(' \r\n')
            if row.startswith('Date/Time= '):
                dt = datetime.datetime.strptime(row[len('Date/Time= '):],
                        '%Y/%m/%d %H:%M:%S')
                obj['timestamp'] = dt
            elif row.startswith('Severity= '):
                obj['level'] = row[len('Severity= '):]
            elif row.startswith('User='):   # Some activities have no user.
                if row.startswith('User= '):
                    obj['user'] = row[len('User= '):]
                else:
                    obj['user'] = None
            elif row.startswith('Activities= '):
                obj['info'] = row[len('Activities= '):]
        if len(obj) != 4:
            continue

        if obj['timestamp'] >= lastdt:
            objs.append(obj)
            if obj['timestamp'] == lastdt:
                hit = True  # Little check if miss. (May have false positive)
    
    if lastdt == datetime.datetime.fromtimestamp(0) or hit:
        q = ActivityModel.delete().where(ActivityModel.timestamp >= lastdt)
        q.execute()
    else:
        print(datetime.datetime.now().isoformat(), 'Some data is missing.')
    q = ActivityModel.insert_many(objs)
    q.execute()


if __name__ == '__main__':
    print(datetime.datetime.now().isoformat(), 'Start')
    try:
        main()
    except pexpect.TIMEOUT:
        print('Timeout.')
    print(datetime.datetime.now().isoformat(), 'End')
