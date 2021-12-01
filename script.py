import json
import getpass
import telnetlib

def config_telnet():
    HOST = "192.0.0.1"
    user = input("Enter your telnet username: ")
    password = getpass.getpass()

    tn = telnetlib.Telnet(HOST)
    
    tn.read_until("Username: ")
    tn.write(user + "\n")
    tn.read_until("Password: ")
    if password:
        print("ici\n")
        tn.write(password + "\n")
        tn.write("enable\n")
        tn.write("cisco\n")
        tn.write("configure t\n")

        #tn.write("int loop 0\n")
        #tn.write("ip address 111.111.111.111 255.255.255.255\n")
        tn.write("end\n")
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

