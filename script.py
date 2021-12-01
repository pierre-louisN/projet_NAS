import json
import getpass
import telnetlib

def config_telnet():
    HOST = "192.0.0.1"
    user = input("Enter your telnet username: ")
    password = getpass.getpass()
    #on doit recuperer le area id mais pour l'instant il est à 0
    area_id = 0
    tn = telnetlib.Telnet(HOST)
    interfaces=[]
    process_id= 3
    tn.read_until("Username: ")
    tn.write(user + "\n")
    tn.read_until("Password: ")
    if password:
        #on configure OSPF
        #attention on construit le  router id sur le dernier octet de l'ip
        # si on a plusieurs sous reseau alors certains se retrouveront avec le meme router id
        tn.write(password + "\n")
        host_parse = HOST.split(".")
        router_id_base = host_parse[3]
        tn.write("enable\n")
        tn.write("cisco\n")
        tn.write("configure t\n")
        tn.write("router ospf "+process_id)
        router_id = router_id_base+"."+router_id_base+"."+router_id_base+"."+router_id_base
        tn.write("router-id"+router_id)
        tn.write("end\n")
        #on active ospf
        for interface in interfaces:
            tn.write("conf t")
            tn.write("interface "+interface)
            tn.write("ip ospf "+process_id+"area "+aread_id)
            tn.write("exit\n")


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

