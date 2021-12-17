import json
import getpass
import telnetlib
import os
import time 

def config_telnet():
    os.system("rm /home/strack/GNS3/projects/test/project-files/dynamips/c408e2c4-a1c6-4fcd-9c09-2a86e9afc405/configs/i2_startup-config.cfg")
    
    time.sleep(5)
    HOST = "127.0.0.1"
    port = 5001
    #user = input("Enter your telnet username: ")
    #password = getpass.getpass()
    #print("password : "+password)
    #on doit recuperer le area id mais pour l'instant il est à 0
    area_id = b'0'
    #tn = telnetlib.Telnet(HOST,port)
    with telnetlib.Telnet(HOST, port) as tn:
        tn.set_debuglevel(1)
        #tn.interact()
        #b'FastEthernet 0/0',b'GigabitEthernet 1/0',
        interfaces=[b'GigabitEthernet 2/0',b'GigabitEthernet 3/0']
        process_id= b'3'
        for i in range (1,5):
            tn.write(b'\r')
        #il faut faire l'ip loopback
        #ip_loopback=""
        #tn.write("\n".encode('ascii'))
        
        
        #print("bonjour:"+tn.read_all().decode('ascii'))
        
        #tn.read_until(b"\n")
        print("ligne 23 ")
        print("on est entre username")
        #tn.write(user + "\n")
        #tn.read_until(b"Password: ")
        
        #if password:
        print("on entre dans password \n")
        #on configure OSPF
        #attention on construit le  router id sur le dernier octet de l'ip
        # si on a plusieurs sous reseau alors certains se retrouveront avec le meme router id
        #tn.write(password + "\n")
        i = 0
        while i < len(interfaces):
            tn.write(b'configure terminal \r')
            
            tn.write(b'interface '+interfaces[i]+b' \r')
            
            tn.write(b'ip address 192.0.1.'+str(i+2).encode('ascii')+b' 255.255.255.252 \r')
            tn.write(b'no shutdown \r')
            tn.write(b'end \r')
            time.sleep(1)
            tn.write(b' \r ')
            
            #tn.write(b'end \r')
            i+= 1
        #on active ospf
        host_parse = HOST.split(".")
        router_id_base = host_parse[3]
        tn.write(b'configure t \r')
        tn.write(b'router ospf '+process_id+b' \r')
        router_id_base=router_id_base.encode('ascii')
        router_id = router_id_base+b'.'+router_id_base+b'.'+router_id_base+b'.'+router_id_base

        tn.write((b'router-id ')+router_id+b' \r')
        tn.write(b"end \r")

        for interface in interfaces:
            
            tn.write(b'conf t \r')
            tn.write(b'interface '+interface+b' \r')
            tn.write((b'ip ospf ')+process_id+(b' area ')+area_id+b' \r')
           
            tn.write(b' \r ')

            
            #tn.write(b'enable cisco \r')
            tn.write(b'end \r')
            #tn.write(b'cisco\r')
            

        #loopback config 
        #tn.write(b"configure terminal \r")
        #tn.write(b"interface Loopback0 \r")
        #tn.write("ip address"+ip_loopback+"255.255.255.255")
        #tn.write(b"end \r")

        #mpls
        tn.write(b"conf t \r")
        tn.write(b"mpls ip \r")
        tn.write(b"mpls label protocol ldp \r")
        
        for interface in interfaces:
            interface_string= str(interface)
            tn.write(b"interface "+interface+b' \r')
            tn.write(b"mpls ip \r")
            tn.write(b"exit \r")
            
            time.sleep(1)
            tn.write(b' \r ')
        tn.write(b"end \r")
        time.sleep(1)
        i=0
        tn.write(b"conf t \r")
        while i < len(interfaces):

            
            tn.write(b"router bgp 110 \r")
            tn.write(b"no sync \r")
            tn.write(b"neighbor 2.2.2."+str(i+2).encode('ascii')+b" remote-as 110 \r")
            tn.write(b"neighbor 2.2.2."+str(i+2).encode('ascii')+b" update-source "+interfaces[i]+b" \r")
            tn.write(b"exit \r")
            
            time.sleep(1)
            tn.write(b' \r ')
            i = i+1
                




def read_json():

    with open('data.json') as json_file:
        data = json.load(json_file)
        for p in data['routers']: # ici changer les champs 
            # print('Name: ' + p['name'])
            # print('Website: ' + p['website'])
            # print('From: ' + p['from'])
            # print('')
            for i in p['interfaces']:
                if(i['protocol'] == "OSPF") :
                    #generate config
                    print('Generation of OSPF config on router : '+ p['name'] + ' for interface '+ i['name']+'\n')



if __name__ == "__main__":
    print("Début main")
    #read_json()
    config_telnet()
    print("Fin main")

