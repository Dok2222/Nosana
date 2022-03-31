# -*- coding: utf-8 -*-

import paramiko
import time
import re

ftp_address = 'ftp://ftpuser:ftpuser@10.10.0.198'
tftp_address = 'tftp://10.10.0.198'

class switch:
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.ssh = None
        self.connect()
        if self.ssh is None:
            raise
    
    def __del__(self):
        if self.ssh is not None:
            self.ssh.close()
        
    def connect(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname = self.address, username = self.username, password = self.password, look_for_keys=False, allow_agent=False)
        except Exception as ex:
            #print(ex)
            return None
        self.ssh = client.invoke_shell()


class rsp(switch):
    def __init__(self, address, username, password):
        switch.__init__(self, address, username, password)
        
    
    def get_config(self):
        self.ssh.send('enable\n')
        time.sleep(1)
        self.ssh.send('copy config running-config remote {}/{}.xml\n'.format(ftp_address, self.address))
        for t in range(2):
            time.sleep(10)
            result = str(self.ssh.recv(3000))
            #print(result)
            if 'OK.' in result:
                break
        print('{}.xml OK'.format(self.address))
            
        self.ssh.send('copy script running-config remote {}/{}.cli\n'.format(ftp_address, self.address))
        for t in range(2):
            time.sleep(10)
            result = str(self.ssh.recv(3000))
            #print(result)
            if 'OK.' in result:
                break
        print('{}.cli OK'.format(self.address))
    
    def get_info(self):
        self.ssh.send('show system info\n')
        time.sleep(1)
        self.ssh.send(' ')
        time.sleep(1)
        result = str(self.ssh.recv(3000))
        serial = r'Serial (N|n)umber.+?(\w+)\\r'
        model =r'(H|h)ardware (D|d)escription.+?(\w.+?)\\r'
        r = {}
        r['address'] = self.address
        r['serial'] = re.search(serial, result).group(2)
        r['model'] = re.search(model, result).group(3).split('-')[0]  
        return r
    
    def get_interfaces_statistics(self):
        dropped = r'Events with packets dropped.+?(\d+)'
        crc_align = r'CRC and align errors.+?(\d+)'
        undersized = r'Undersized packets received.+?(\d+)'
        oversized = r'Oversized packets received.+?(\d+)'
        fragments = r'Fragments packets received.+?(\d+)'
        jabbers = r'Jabbers received.+?(\d+)'
        r = []
        
        for i in range(1,49):
            self.ssh.send('show interface statistics 1/{}\n'.format(i))
            time.sleep(1)
            result = str(self.ssh.recv(3000))
            if 'Invalid command' in result:
                break
            s = {}
            s['dropped'] = int(re.search(dropped, result).group(1))
            s['undersized'] = int(re.search(undersized, result).group(1))
            s['crc_align'] = int(re.search(crc_align, result).group(1))
            s['undersized'] = int(re.search(undersized, result).group(1))
            s['oversized'] = int(re.search(oversized, result).group(1))
            s['fragments'] = int(re.search(fragments, result).group(1))
            s['jabbers'] = int(re.search(jabbers, result).group(1))
            r.append(s)
        return r
    
    def clear_port_statistics(self):
        self.ssh.send('enable\n')
        time.sleep(1)
        self.ssh.send('clear port-statistics\n')
        for t in range(2):
            time.sleep(2)
            result = str(self.ssh.recv(3000))
            if 'Are you sure (Y/N)' in result:
                self.ssh.send('y')
                break 
        
        

class mar(switch):
    def __init__(self, address, username, password):
        switch.__init__(self, address, username, password)
        
    def get_config(self):
        self.ssh.send('enable\n')
        time.sleep(1)
        self.ssh.send('copy system:running-config {}/{}.bin\n'.format(tftp_address, self.address))
        for t in range(2):
            time.sleep(5)
            result = str(self.ssh.recv(3000))
            if 'Are you sure you want to start? (y/n)' in result:
                self.ssh.send('y')
                break
        for t in range(2):
            time.sleep(10)
            result = str(self.ssh.recv(3000))
            if 'successfully.' in result:
                break
        print('{}.bin OK'.format(self.address))
    
    def get_info(self):
        self.ssh.send('show sysinfo\n')
        time.sleep(1)
        self.ssh.send(' ')
        time.sleep(1)
        result = str(self.ssh.recv(3000))
        serial = r'Serial (N|n)umber.+?(\w+)\\r'
        model =r'(H|h)ardware (D|d)escription.+?(\w.+?)\\r'
        r = {}
        r['address'] = self.address
        r['serial'] = re.search(serial, result).group(2)
        r['model'] = re.search(model, result).group(3).split('-')[0]  
        return r        
    
        
#try:
    #sw = rsp('10.10.2.1', 'login', 'password')
#except:
    #print('Не удалось создать коммутатор :(')

#del sw
#print(sw.get_info())
#sw.get_config()
#stat = sw.get_interfaces_statistics()
#for i, j in enumerate(stat, 1):
    #print(i, '-', j)
#sw.clear_port_statistics()
