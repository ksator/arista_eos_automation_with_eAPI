import yaml
from jinja2 import Template
import os
from jsonrpclib import Server
import time 

username = "arista"
password = "arista"

# Devices inventory 
inventory_f=open('inventory.yml', 'r')
inventory_s=inventory_f.read()
inventory_f.close()
inventory=yaml.load(inventory_s, Loader=yaml.FullLoader)

# Printing some details regarding the devices
for device in inventory:
    print ('-'*60)
    print ('Printing some details regarding the device ' + device)
    ip = inventory[device]['ip']
    url = "http://" + username + ":" + password + "@" + ip + "/command-api"
    switch = Server(url)
    result=switch.runCmds(version=1,cmds=["sh ver"], format='json', autoComplete=True)
    print('model is ' + result[0]['modelName'])
    print('version is ' + result[0]['version'])

# Template to generate devices configuration 
f=open('templates/config.j2')
s=f.read()
f.close()
eos_template=Template(s)

# Directory to save the generated devices configuration 
cwd = os.getcwd()
config_directory = os.path.dirname(cwd + "/config/")
if not os.path.exists(config_directory):
    os.makedirs(config_directory)

# Genrating the devices configuration
for device in inventory:
    print ('-'*60)
    print ('Generating the configuration for device ' + device)
    f=open(inventory[device]['vars'])
    s=f.read()
    f.close()
    vars = yaml.load(s, Loader=yaml.FullLoader)
    conf = open(config_directory + '/' + device + '.txt','w')
    conf.write(eos_template.render(vars))
    conf.close()
    print ('The generated device configuration is now saved in the config directory')

# configuring the devices
for device in inventory:
    print ('-'*60)
    print ('configuring the device ' + device)
    ip = inventory[device]['ip']
    url = "http://" + username + ":" + password + "@" + ip + "/command-api"
    switch = Server(url)
    f = open(config_directory + '/' + device + '.txt','r')
    conf_list = f.read().splitlines()
    f.close() 
    conf = switch.runCmds(version=1,cmds=conf_list, autoComplete=True)
    print ('Done') 




