import json
import getpass
import telnetlib
import os
import time 


def get_routerID(router_num) :
    router_id_base=router_num.encode('ascii')
    router_id = router_id_base+b'.'+router_id_base+b'.'+router_id_base+b'.'+router_id_base
    return router_id

def get_subnet_num(link_num,router_name):
     with open('data.json') as json_file:
        data = json.load(json_file)
        for link in data['links']:
            if(link['num']==link_num):
                if(link['router1']==router_name):
                    return 1
                else :
                    return 2


def config_interface(tn,interface_name,link_num,router_name):
    router_num = router_name[1:]
    tn.write(b'configure terminal \r')
    
    tn.write(b'interface '+interface_name.encode('ascii')+b' \r')
    
    if(interface_name=="Loopback0"):
        tn.write(b'ip address '+get_routerID(router_num)+b' 255.255.255.255 \r')
    else :
        subnet_num = str(get_subnet_num(link_num,router_name))
        print("dernier chiffre = "+subnet_num)
        tn.write(b'ip address 10.10.'+link_num.encode('ascii')+b'.'+subnet_num.encode('ascii')+b' 255.255.255.0 \r')
    
    tn.write(b'no shutdown \r')
    tn.write(b'end \r')
    time.sleep(1)
    tn.write(b' \r ')


#active OSPF sur le routeur 
def router_activate_OSPF(tn,router_num,process_id):
    tn.write(b'configure t \r')
    tn.write(b'router ospf '+process_id.encode('ascii')+b' \r')
    router_id = get_routerID(router_num)
    tn.write((b'router-id ')+router_id+b' \r')
    time.sleep(1)
    tn.write(b"end \r")

def router_activate_MPLS(tn,router_name):
    tn.write(b'conf t \r')
    tn.write(b"mpls ip \r")
    tn.write(b"mpls label protocol ldp \r")
    tn.write(b'end \r')
    time.sleep(1)
    print("MPLS activated on router :",router_name)

#active OSPF sur l'interface
def config_OSPF(tn,interface_name,process_id,area_id):
    tn.write(b'conf t \r')
    tn.write(b'interface '+interface_name.encode('ascii')+b' \r')
    tn.write((b'ip ospf ')+process_id.encode('ascii')+(b' area ')+area_id.encode('ascii')+b' \r')
    tn.write(b' \r ')
    time.sleep(1)
    #tn.write(b'enable cisco \r')
    tn.write(b'end \r')
    #tn.write(b'cisco\r')

def config_MPLS(tn,interface_name):
    tn.write(b"conf t \r")
    tn.write(b"interface "+interface_name.encode('ascii')+b' \r')
    tn.write(b"mpls ip \r")
    tn.write(b"exit \r")
    time.sleep(1)
    tn.write(b' \r ')
    tn.write(b"end \r")

def config_BGP(tn,as_number,router_name):
    tn.write(b"conf t \r")
    tn.write(b"router bgp "+as_number+"\r")
    tn.write(b"no sync \r")
    neighbors = get_neighbors(router_name) #récupére les voisins 
    for neighbor in neighbors :
        tn.write(b"neighbor "+get_routerID(neighbor)+b" remote-as "+as_number+" \r")
        tn.write(b"neighbor "+get_routerID(neighbor)+b" update-source Loopback0 \r")
    tn.write(b"exit \r")
    time.sleep(1)
    tn.write(b' \r ')

def config_telnet():
#   os.system("rm /home/strack/GNS3/projects/test/project-files/dynamips/c408e2c4-a1c6-4fcd-9c09-2a86e9afc405/configs/i2_startup-config.cfg")
    
    username = "plnohet"
    project_name =  "Test"
    HOST = "127.0.0.1"

    with open('data.json') as json_file:
        data = json.load(json_file)
        for router_conf in data['routers']: 
            port = 5000 + (int)(router_conf['name'][1:]) - 1 
            print("Router "+router_conf['name']+" port n° : " + str(port))

            with telnetlib.Telnet(HOST, port) as tn:
                tn.set_debuglevel(1)
                if(router_conf['folder_name']) :
                    os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
                    time.sleep(5)

                    #pour sauter les lignes d'initialisation du terminal
                    for i in range (1,5):
                        tn.write(b'\r')        

                    for interface in router_conf['interfaces']:
                        if(interface['state'] == "up"):
                            config_interface(tn,interface['name'],interface['link'],router_conf['name'])

                    if(router_conf['ospf_area_id']) :
                        print("OSPF activated on router :",router_conf['name'])
                      
                        router_activate_OSPF(tn,router_conf['name'][1:],process_id)

                    MPLS_activated = False
                    for interface in router_conf['interfaces']:
                        if(interface['state'] == "up"):
                            for protocol in interface['protocols']:      
                                if(protocol == "OSPF") :
                                        print('Generation of OSPF config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                        config_OSPF(tn,interface['name'],router_conf['ospf_process_id'],router_conf['ospf_area_id'])

                                if (protocol == "MPLS"):
                                    if(MPLS_activated==False):  #commande pour activer MPLS sur le routeur, on le fait que une seule fois
                                        router_activate_MPLS(tn,router_conf['name'])
                                        MPLS_activated = True
                                    
                                    print('Generation of MPLS config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                    config_MPLS(tn,interface['name'])
                                
                                if (protocol == "iBGP"): # pas encore fini
                                    print('Generation of BGP config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                    # pour l'instant on le met en sur 
                                    as_number = "110" # pour l'instant, on le met en dur mais après il faudra le rajouter dans le json pour chaque routeur 
                                    config_BGP(tn,as_number,router_conf['name'])
                else :
                    return 0

if __name__ == "__main__":
    print("Début main")
    config_telnet()
    print("Fin main")

