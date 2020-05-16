import yaml
from jsonrpclib import Server
import datetime

username = "arista"
password = "arista"

# Devices inventory and variables
inventory_f=open('inventory.yml', 'r')
inventory_s=inventory_f.read()
inventory_f.close()
inventory=yaml.load(inventory_s, Loader=yaml.FullLoader)

report = open('report.txt', 'w') 
report.write(str(datetime.datetime.now()) + "\n")

for device in inventory:
    print ("Auditing " + device)
    report.write ('-'*60 + "\n")
    report.write ('Auditing device ' + device + "\n")
    f=open(inventory[device]['vars'])
    s=f.read()
    f.close()
    vars = yaml.load(s, Loader=yaml.FullLoader)
    ip = inventory[device]['ip']
    url = "http://" + username + ":" + password + "@" + ip + "/command-api"
    switch = Server(url)
# auditing interfaces status (only the ones you configured, i.e we use the devices variables as a SoT) 
    for item in vars['topology']: 
        int = item['interface']
        command = "show interfaces " + int + " description" 
        result = switch.runCmds(version=1,cmds=[command])
        admin_status = result[0]['interfaceDescriptions'][int]['interfaceStatus']
        op_status = result[0]['interfaceDescriptions'][int]['lineProtocolStatus']
        report.write(int + ": admin status is " + admin_status + ", op status is " + op_status + "\n")
# auditing lldp
    for item in vars['topology']: 
        int = item['interface']
        command = "show lldp neighbors " + int
        result = switch.runCmds(version=1,cmds=[command])
        neighborDevice = result[0]['lldpNeighbors'][0]['neighborDevice']
        neighborPort = result[0]['lldpNeighbors'][0]['neighborPort']
        report.write(int + ': lldp neighbor is ' + neighborDevice + ", lldp remote port is " + neighborPort + "\n")
# auditing bgp (only the neghbors you configured, i.e we use the devices variables as a SoT) 
    for item in vars['topology']: 
        peer = item['ebgp_peer_ip']
        command = "show ip bgp neighbors " + peer
        result = switch.runCmds(version=1,cmds=[command])
        state = result[0]['vrfs']['default']['peerList'][0]['state']
        report.write("BGP session with " + peer + " is " + state + "\n")
        
report.close()
print('All tests done. The audit report is available in the file report.txt')
