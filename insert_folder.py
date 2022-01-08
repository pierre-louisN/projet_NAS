import json
from os import path
import os
import sys

if __name__ == "__main__":
    print('Début')

    with open('data_cop.json', 'r') as json_file:
        data = json.load(json_file)

    path = "OSPF/project-files/dynamips/"
    foldlist = os.listdir(path)
    with open('data_cop.json', 'r') as file:
        data_bis = json.load(file)
    for fold in foldlist:
        try:
            newpath = path + str(fold)+"/configs"
            cfgfiles = os.listdir(newpath)
            cfgfile = cfgfiles[0]
            cfgfile = cfgfile[1:]
            cfgfile = cfgfile.split("_", 1)
            router_name = "R"+cfgfile[0]
            print(router_name)

            for router_conf in data_bis['routers']:
                if router_conf['name'] == router_name:
                    newdic = {"folder_name": fold}
                    router_conf.update(newdic)

        except NotADirectoryError:
            print()
    with open('data_cop.json', 'w') as file:
        json.dump(data_bis, file)
