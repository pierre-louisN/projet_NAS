import json
import getpass
import telnetlib
import os
import time 
import sys
#from jsondiff import diff

def get_routerID(router_num) :
    router_id_base=router_num.encode('ascii')
    router_id = router_id_base+b'.'+router_id_base+b'.'+router_id_base+b'.'+router_id_base
    return router_id

# 
def get_subnet_num(link_num,router_name,data):
        for link in data['links']:
            if(link['num']==link_num):
                if(link['router1']==router_name):
                    return 1
                else :
                    return 2


def config_interface(tn,interface_name,link_num,router_name,data, subnets):
    router_num = router_name[1:]
    tn.write(b'configure terminal \r')
    
    tn.write(b'interface '+interface_name.encode('ascii')+b' \r')
    
    if(interface_name=="Loopback0"):
        tn.write(b'ip address '+get_routerID(router_num)+b' 255.255.255.255 \r')
        (subnets[router_name]).append([get_routerID(router_num),b"255.255.255.255"])
    else :
        subnet_num = str(get_subnet_num(link_num,router_name,data))
        #print("dernier chiffre = "+subnet_num)
        tn.write(b'ip address 10.10.'+link_num.encode('ascii')+b'.'+subnet_num.encode('ascii')+b' 255.255.255.0 \r')
        (subnets[router_name]).append([b'10.10.'+link_num.encode('ascii')+b'.0',b"255.255.255.0"])
    tn.write(b'no shutdown \r')
    tn.write(b'end \r')
    time.sleep(1)
    tn.write(b' \r ')


#active OSPF sur le routeur 
def router_activate_OSPF(tn,router_name,router_type,process_id):
    tn.write(b'configure t \r')
    tn.write(b'router ospf '+process_id.encode('ascii')+b' \r')
    router_id = get_routerID(router_name[1:])
    tn.write((b'router-id ')+router_id+b' \r')
    if(router_type!="PEc"):
        tn.write(b'network '+router_id+b' 0.0.0.0 area 0\r')
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

#retourne le nom de tous les voisins (ceux qui ont le même numéro d'AS et les PEc qui sont reliés)


def get_neighbors(as_number,router_name,router_type, data):
    tab = []
    for router in data["routers"]:
        if(router['name']!=router_name and router["bgp_as"]==as_number):
            tab.append([get_routerID(router['name'][1:]),as_number,router["type"]])  
        
        if(router_type=="PE"):
            for link in data["links"] :
                if(link["router1"]==router_name and router["name"]==link["router2"] and router["type"]=="PEc") :
                    subnet_num = str(get_subnet_num(link['num'],router["name"],data))
                    #tab.append([(b'10.10.'+link['num'].encode('ascii')+b'.'+subnet_num.encode('ascii')),router["bgp_as"],router["type"]]) 
                    tab.append([get_routerID(router['name'][1:]),router["bgp_as"],router["type"],link["num"]])

        if(router_type=="PEc"):
            for link in data["links"] :
                if(link["router2"]==router_name and router["name"]==link["router1"] and router["type"]=="PE") :
                    subnet_num = str(get_subnet_num(link['num'],router["name"],data))
                    tab.append([get_routerID(router['name'][1:]),router["bgp_as"],router["type"],link["num"]])
                    #tab.append([(b'10.10.'+link['num'].encode('ascii')+b'.'+subnet_num.encode('ascii')),router["bgp_as"],router["type"]]) 

    return tab


def config_BGP(tn,as_number,router_name,data,router_type,subnets):
    tn.write(b"conf t \r")    
    tn.write(b"router bgp "+as_number.encode('ascii')+b" \r")
    tn.write(b"no sync \r")
    tn.write(b"bgp router-id "+get_routerID(router_name[1:])+b" \r")
    
    neighbors = get_neighbors(as_number,router_name,router_type,data) #récupére les voisins 
    print(neighbors)
    for neighbor in neighbors :
        tn.write(b"neighbor "+neighbor[0]+b" remote-as "+neighbor[1].encode('ascii')+b" \r")
        #if not((router_type=="PE" and neighbor[2]=="PEc") or (router_type=="PEc" and neighbor[2]=="PE")) : # si ce n'est pas un lien entre PE et CE
        tn.write(b"neighbor "+neighbor[0]+b" update-source Loopback0 \r")
        if(neighbor[1]!=as_number):
            if(neighbor[2]=="P"):
                tn.write(b'neighbor 10.10.'+(neighbor[3].encode('ascii'))+b'.2 route-map PROVIDER_IN in \r')
                tn.write(b'neighbor 10.10.'+(neighbor[3].encode('ascii'))+b'.2 route-map PROVIDER_OUT out \r')
                tn.write(b'end \r')
                tn.write(b'conf t \r')
                tn.write(b'route-map PROVIDER_OUT permit 10 \r')
                tn.write(b'match community 10 \r')
                tn.write(b'continue \r')
                tn.write(b'end \r')
                tn.write(b'conf t')
                tn.write(b'route-map PROVIDER_IN permit 30 \r')
                tn.write(b'match community 1 \r')
                tn.write(b'set local-preference 50 \r')
                tn.write(b'set community '+neighbor[1].encode('ascii')+b':5 \r')

            elif(neighbor[2]=="PE") :
                tn.write(b'neighbor 10.10.'+(neighbor[3].encode('ascii'))+b'.2 route-map PEER_IN in \r')
                tn.write(b'neighbor 10.10.'+(neighbor[3].encode('ascii'))+b'.2 route-map PEER_OUT out \r')
                tn.write(b'end \r')
                tn.write(b'conf t \r')
                tn.write(b'route-map PROVIDER_OUT permit 10 \r')
                tn.write(b'match community 10 \r')
                tn.write(b'continue \r')
                tn.write(b'end \r')
                tn.write(b'conf t \r')
                tn.write(b'route-map PEER_IN permit 30 \r')
                tn.write(b'match community 1 \r')
                tn.write(b'set local-preference 100 \r')
                tn.write(b'set community '+neighbor[1].encode('ascii')+b':100 \r')
            
            elif(neighbor[2]=="PEc") :
                tn.write(b'neighbor 10.10.'+(neighbor[3].encode('ascii'))+b'.2 route-map CLIENT in \r')
                tn.write(b'end \r')
                tn.write(b'conf t \r')
                tn.write(b'route-map CLIENT_IN permit 10 \r')
                tn.write(b'match community 1 \r')
                tn.write(b'set local-preference 150 \r')
                tn.write(b'set community '+neighbor[1].encode('ascii')+b':150 \r')
        
        tn.write(b'end \r')
        time.sleep(1)
        tn.write(b'conf t \r')
        tn.write(b"router bgp "+as_number.encode('ascii')+b" \r")
       
    if(router_type!="P"): # si le routeur courant est n'est pas un provider
        for subnets_routers in subnets[router_name] :
            print(subnets_routers)
            tn.write(b'network '+subnets_routers[0]+ b' mask '+subnets_routers[1]+b' \r')
    tn.write(b"end\r")
    time.sleep(1)
    tn.write(b' \r ')

def config_telnet(user,project,filename):
#   os.system("rm /home/strack/GNS3/projects/test/project-files/dynamips/c408e2c4-a1c6-4fcd-9c09-2a86e9afc405/configs/i2_startup-config.cfg")
    os.system('python3 insert_folder.py')
    time.sleep(1)
    username = user
    project_name =  project
    HOST = "127.0.0.1"

    with open(filename) as json_file:
        data = json.load(json_file)

        subnets = {}
        for router_conf in data['routers']:
            #on part du principe que les routeurs sont crée les uns après les autres et dans l'ordre
            #port = 5000 + (int)(router_conf['name'][1:]) - 1 
            port = router_conf['port']
            print("Router "+router_conf['name']+" port n° : " + str(port))
            subnets[router_conf['name']] = []
            try : 
                with telnetlib.Telnet(HOST, port) as tn :
                    # 0 : enlève les write du terminal, 1 : met les print dans le terminal 
                    tn.set_debuglevel(1)
                    #if(router_conf['folder_name']) :
                    #os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
                    #time.sleep(5)

                        #pour sauter les lignes d'initialisation du terminal
                    for i in range (1,5):
                        tn.write(b'\r')        

                    for interface in router_conf['interfaces']:
                        if(interface['state'] == "up"):
                            config_interface(tn,interface['name'],interface['link'],router_conf['name'],data,subnets)
                    
                    if(router_conf["type"]!="PEc"): 
                        try : 
                            if(router_conf['ospf_area_id']) :
                                print("OSPF activated on router :",router_conf['name'])
                                router_activate_OSPF(tn,router_conf['name'],router_conf['type'],router_conf['ospf_process_id'])
                        except KeyError :
                            continue 
                    
                    MPLS_activated = False
                    for interface in router_conf['interfaces']:
                        if(interface['state'] == "up"):
                            try :
                                if(router_conf["type"]!="PEc") :

                                    for protocol in interface['protocols']:  

                                        try :     
                                            if(router_conf['ospf_area_id']) :
                                                    print('Generation of OSPF config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                                    config_OSPF(tn,interface['name'],router_conf['ospf_process_id'],router_conf['ospf_area_id'])
                                        except KeyError :
                                            print("OSPF not implented")
                                        
                                        if (protocol == "MPLS"):
                                            if(MPLS_activated==False):  #commande pour activer MPLS sur le routeur, on le fait que une seule fois
                                                router_activate_MPLS(tn,router_conf['name'])
                                                MPLS_activated = True
                                            
                                            print('Generation of MPLS config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                            config_MPLS(tn,interface['name'])
                                        
                                        try :
                                            if (router_conf["bgp_as"]): 
                                                print('Generation of BGP config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                                # pour l'instant on le met en sur 
                                                as_number = router_conf["bgp_as"] # pour l'instant, on le met en dur mais après il faudra le rajouter dans le json pour chaque routeur 
                                                config_BGP(tn,as_number,router_conf['name'],data,router_conf["type"],subnets)
                                        except KeyError :
                                            print("BGP not implented")
                                else :
                                    try :
                                        if(router_conf["bgp_as"]): 
                                            print('Generation of BGP config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                                            # pour l'instant on le met en sur 
                                            as_number = router_conf["bgp_as"] # pour l'instant, on le met en dur mais après il faudra le rajouter dans le json pour chaque routeur 
                                            config_BGP(tn,as_number,router_conf['name'],data,router_conf["type"],subnets)
                                    except KeyError :
                                        print("BGP not implented") 

                            except KeyError :
                                continue
                    #else :
                    #    return 0
                    tn.write(b'write \r') 
                    time.sleep(1)
                    tn.write(b'\r') 
            #si on arrive pas à se connecter au routeur 
            except ConnectionRefusedError:
                continue


def deconfig_OSPF(tn, interface_name,process_id,area_id):
    tn.write(b'enable \r')
    tn.write(b'conf t \r')
    tn.write(b'interface '+interface_name.encode('ascii')+b' \r')
    tn.write((b'no ip ospf ')+process_id.encode('ascii')+(b' area ')+area_id.encode('ascii')+b' \r')
    tn.write(b' \r ')
    time.sleep(1)
    tn.write(b'end \r')

def deconfig_MPLS(tn, interface_name):
    tn.write(b"conf t \r")
    tn.write(b"interface "+interface_name.encode('ascii')+b' \r')
    tn.write(b'no mpls ip \r')

def deconfig_BGP(tn,as_number,router_name):
    tn.write(b"conf t \r")
    tn.write(b"no router bgp "+as_number+"\r")

def get_ancien_json(name):
    with open(name) as json_file:
        data = json.load(json_file)
        return data

#sort json then return true if they are equal
def has_a_diff(json1, json2):
    json1 = json.dumps(json1, sort_keys=True)
    json2 = json.dumps(json2, sort_keys=True)

    return (json1==json2)

#search name in json1 group 
def search_name( json1,group,name):
   
    return [obj for obj in json1 if obj[group]==name]

def search_protocol (json1,name):
    return [obj for obj in json1 if obj==name]

def maj():
    os.system('python3 insert_folder.py')
    time.sleep(1)
    username = "sstrack"
    project_name =  "OSPF"
    HOST = "127.0.0.1"


    with open('newdata_test.json') as json_file:
        data = json.load(json_file)

        ancien_data=get_ancien_json('olddata_test.json')
        subnets= {}
        for router_conf in data['routers']:
            port = router_conf['port']
            print("Router "+router_conf['name']+" port n° : " + str(port))
            subnets[router_conf['name']] = []
                
            try:   
                with telnetlib.Telnet(HOST, port) as tn:
                    #search if a router from the new json is in the old json 
                    
                   # os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
                    #os.system("rm /home/strack/Documents/NAS/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
                    time.sleep(5)
                    
                    
                    samerouter= search_name(ancien_data['routers'],'name',router_conf['name'])
                    #if we don't find it in the old json, we create it 
                    if not(samerouter):
                        print("we create "+router_conf['name']+" in the new json \n")
                        create_router(tn,router_conf)
                        
                    else:
                        '''with telnetlib.Telnet(HOST, port) as tn:
                            tn.set_debuglevel(1)

                            for i in range (1,5):
                                    tn.write(b'\r')  '''
                        samerouter = samerouter[0]
                        print(json.dumps(samerouter, indent=4, sort_keys=True))    
                        print(json.dumps(router_conf['interfaces'][0]['link'], indent=4, sort_keys=True)) 
                        print("fini")
                        for interface in router_conf['interfaces']:
                            print(samerouter['interfaces'][0])
                            samelink = search_name(samerouter['interfaces'][0],'link',interface['link'])
                            #linkinnew = search_name(router_conf['interfaces'],'link', samerouter['interfaces'])
                            if not(samelink):
                                
                                #config new link with the new protocols 
                                print("link  "+interface['link']+" created in the new file \n")
                                config_interface(tn,interface['name'],interface['link'],router_conf['name'],data,subnets)
                            #print("samelink"+json.dumps(samelink, indent=4, sort_keys=True))
                            #print("porotocol : " +json.dumps(interface['protocols'], indent=4, sort_keys=True))
            except ConnectionRefusedError:
                continue      
                
        for router_conf in ancien_data['routers']:
            port = router_conf['port']
            print("Router "+router_conf['name']+" port n° : " + str(port))
            subnets[router_conf['name']] = []

            try:   
                with telnetlib.Telnet(HOST, port) as tn:
                    '''port = 5000 + (int)(router_conf['name'][1:]) - 1 
                    print("Router "+router_conf['name']+" port n° : " + str(port))'''
            
                   # os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
                   # time.sleep(5)
                    samerouter= search_name(data['routers'],'name',router_conf['name'])
                    #if we don't find it in the old json, we create it 
                    if not(samerouter):
                        print("we delete "+router_conf['name']+" in the new json \n")
                    else:
                        '''with telnetlib.Telnet(HOST, port) as tn:
                            tn.set_debuglevel(1)

                            for i in range (1,5):
                                    tn.write(b'\r')  '''
                        samerouter = samerouter[0]
                        #print(json.dumps(samerouter, indent=4, sort_keys=True))    
                        #print(json.dumps(router_conf['interfaces'][0], indent=4, sort_keys=True)) 
                        print("fini")
                        for interface in router_conf['interfaces']:
                            samelink = search_name(samerouter['interfaces'],'link',interface['link'])
                            #linkinnew = search_name(router_conf['interfaces'],'link', samerouter['interfaces'])
                            if not(samelink):
                                
                                #config new link with the new protocols 
                                print("link  "+interface['link']+" deleted in the new file \n")
                                interface_shutdown(tn,interface['name'])
                            #print("samelink"+json.dumps(samelink, indent=4, sort_keys=True))
                            #print("porotocol : " +json.dumps(interface['protocols'], indent=4, sort_keys=True))
            except ConnectionRefusedError:
                continue   
                            
def create_router(tn,router_conf,data,subnets):
    try : 
                  
    
        # 0 : enlève les write du terminal, 1 : met les print dans le terminal 
        tn.set_debuglevel(0)
        #if(router_conf['folder_name']) :
            #os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
            #time.sleep(5)

            #pour sauter les lignes d'initialisation du terminal
        for i in range (1,5):
            tn.write(b'\r')        

        for interface in router_conf['interfaces']:
            if(interface['state'] == "up"):
                config_interface(tn,interface['name'],interface['link'],router_conf['name'],data,subnets)

        if(router_conf['ospf_area_id']) :
            print("OSPF activated on router :",router_conf['name'])
            router_activate_OSPF(tn,router_conf['name'][1:],router_conf['ospf_process_id'])

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
                    
                    if (router_conf["bgp_as"]): # pas encore fini
                        print('Generation of BGP config on router : '+ router_conf['name'] + ' for interface '+ interface['name']+'\n')
                        # pour l'instant on le met en sur 
                        as_number = router_conf["bgp_as"] # pour l'instant, on le met en dur mais après il faudra le rajouter dans le json pour chaque routeur 
                        config_BGP(tn,as_number,router_conf['name'],data)
                    #else :
                    #    return 0
            #si on arrive pas à se connecter au routeur 
    except ConnectionRefusedError:
        pass



if __name__ == "__main__":
    print("Début main configuration Telnet")


    if len(sys.argv) >= 4 :
        username = sys.argv[1]
        project_name =  sys.argv[2]
        filename = sys.argv[3] 
        mode = sys.argv[4]
    else : #argument par défaut 
        username = "plnohet"
        project_name =  "Basic"
        filename = 'olddata_test.json'
        mode = 0
    if(mode == 0 ):
        config_telnet(username,project_name,filename)
    else :
        maj()
    print("Fin main configuration Telnet")

