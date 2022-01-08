import json
from os import path


def conf_basic(fichier, router_conf):
    fichier.write("!Config du routeur"+str(router_conf['name'])+"\n")
    fichier.write("version 15.2\n")
    fichier.write("service timestamps debug datetime msec\n")
    fichier.write("service timestamps log datetime msec\n")
    fichier.write("hostname "+str(router_conf['name']))
    fichier.write("boot-start-marker\n")
    fichier.write("boot-end-marker\n")
    fichier.write("no aaa new-model\n")
    fichier.write("no ip icmp rate-limit unreachable\n")
    fichier.write("ip cef\n")
    fichier.write("no ip domain lookup\n")
    fichier.write("no ipv6 cef\n")


def conf_mpls(fichier, router_conf):
    for interface in router_conf['interfaces']:

        # Integration de MPLS un peu tordu pour l'instant mais j'améliorerai après
        mpls = False
        if(str(interface['state']) == "up"):
            for protocol in interface['protocols']:
                if (protocol == "MPLS"):
                    mpls = True
                    fichier.write("mpls label protocol ldp\n")

            if (mpls):
                break


def conf_interfaces(fichier, router_conf, data):
    for interface in router_conf['interfaces']:
        # interface qui sont down
        fichier.write("! Config une interface \n")
        if(str(interface['state']) == "down"):
            fichier.write("! Cet interface est shutdown \n")
            fichier.write("interface "+str(interface['name'])+"\n")
            fichier.write(" no ip address\n")
            fichier.write(" shutdown\n")
            fichier.write(" duplex full\n")
            fichier.write("! Fin config d interface \n")
        # interface qui sont up
        if(str(interface['state']) == "up"):
            fichier.write("! Cet interface est up\n")
            fichier.write("interface "+str(interface['name'])+"\n")
            # Différencier Loopback des autres addresse ip
            if (interface['link'] == "0"):
                fichier.write(" ip addresse ")
                rout = router_conf['name']
                rout_num = rout[1:]
                fichier.write(rout_num+"."+rout_num+"." +
                              rout_num+"."+rout_num+"\n")
            else:
                fichier.write(" ip address 10.10.")
                for link in data['links']:
                    if(link['num'] == interface['link']):
                        fichier.write(str(link['num'])+".")
                        if(link['router1'] == router_conf['name']):
                            fichier.write("1 ")
                        if(link['router2'] == router_conf['name']):
                            fichier.write("2 ")
                        fichier.write("255.255.255.0\n")
            if("OSPF" in interface['protocols']):
                fichier.write(
                    " ip ospf " + router_conf["ospf_process_id"] + " area " + str(router_conf['ospf_area_id'])+"\n")
                if (interface['link'] != "0"):
                    fichier.write(" negotition auto")
        # if("OSPF" in interface['protocols']):


def conf_end(fichier):
    # Fin du fichier
    fichier.write("!\n")
    fichier.write("!\n")
    fichier.write("!\n")
    fichier.write("ip forward-protocol nd\n")
    fichier.write("no ip http server\n")
    fichier.write("control-plane\n")
    fichier.write("line con 0\n")
    fichier.write(" exec-timeout 0 0\n")
    fichier.write(" privilege level 15\n")
    fichier.write(" logging synchronous\n")
    fichier.write(" stopbits 1\n")
    fichier.write("line aux 0\n")
    fichier.write(" exec-timeout 0 0\n")
    fichier.write(" privilege level 15\n")
    fichier.write(" logging synchronous\n")
    fichier.write(" stopbits 1\n")
    fichier.write("line vty 0 4\n")
    fichier.write(" login\n")
    fichier.write("end")


if __name__ == "__main__":
    print('Début')

    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
        # print(data['routers'])
    # there is a file to push for each router to configure

    for router_conf in data['routers']:
        # Commentaire à enlever pour le vrai test
        path = "project-files/dynamips/"
        path += str(router_conf['id'])
        #path += "/configs"
        #path += "router "+str(router_conf['name'])+" configuration"
        fichier = open(path+"_bis.cfg", 'w+')
        conf_basic(fichier, router_conf)
        print("Routeur"+str(router_conf['name']))
        # Configure MPLS
        conf_mpls(fichier, router_conf)
        # Other basics confguration
        fichier.write("multilink bundle-name authenticated\n")
        fichier.write("ip tcp synwait-time 5\n")

        # Configuration des interfaces + addresse IP
        fichier.write("!\n")

        conf_interfaces(fichier, router_conf, data)
        conf_end(fichier)

        fichier.close()

        """"Problème d'itération quand on write sur le fichier
        le curseur va à la fin donc on ne peut pas ecrire dessus"""
