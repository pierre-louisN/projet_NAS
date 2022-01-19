import json
from os import path
import os

if __name__ == "__main__":
    print("Début main")

    username = "plnohet"
    project_name =  "OSPF"

    with open('data_cop.json') as json_file:
        data = json.load(json_file)
        for router_conf in data['routers']: 
            os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_startup-config.cfg")
            os.system("rm /home/"+username+"/GNS3/projects/"+project_name+"/project-files/dynamips/"+router_conf['folder_name']+"/configs/i"+router_conf['name'][1:]+"_private-config.cfg")                       
    print("Fin main")
