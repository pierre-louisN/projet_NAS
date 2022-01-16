import json
from os import path

save_id = ""


def conf_basic(fichier, router_conf):
    fichier.write("!Config du routeur"+str(router_conf['name'])+"\n")
    fichier.write("version 15.2\n")
    fichier.write("service timestamps debug datetime msec\n")
    fichier.write("service timestamps log datetime msec\n")
    fichier.write("hostname "+str(router_conf['name'])+"\n")
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

            if ("protocols" in interface):
                for protocol in interface['protocols']:
                    if (protocol == "MPLS"):
                        mpls = True
                        fichier.write("mpls label protocol ldp\n")

            if (mpls):
                break


def conf_inter_down(fichier, router_conf, interface):
    fichier.write("! Cet interface est shutdown \n")
    fichier.write("interface "+str(interface['name'])+"\n")
    fichier.write(" no ip address\n")
    fichier.write(" shutdown\n")
    fichier.write(" duplex full\n")
    fichier.write("! Fin config d interface \n")


def conf_inter_up(fichier, router_conf, data, interface):
    fichier.write("! Cet interface est up\n")
    fichier.write("interface "+str(interface['name'])+"\n")
    # Différencier Loopback des autres addresse ip
    # Le routeur est-il connecté à un routeur de l'AS ou pas
    same_as = 1
    if ((interface["name"] != "Loopback0")):
        for other_router in data["routers"]:
            if (interface["router"] == other_router["name"]):
                if (other_router["bgp_as"] != router_conf["bgp_as"]):
                    same_as = 0

    if (interface['link'] == "0"):
        fichier.write(" ip addresse ")
        rout = router_conf['name']
        rout_num = rout[1:]
        loop_addr = rout_num+"."+rout_num+"." + \
            rout_num+"."+rout_num
        mask = " 255.255.255.255\n"
        fichier.write(loop_addr + mask)
        network = loop_addr + " mask"+mask
        networks.append(network)
    else:
        # Configuration différente selon même AS ou pas
        if (same_as == 0):
            fichier.write(" ip address 1.1.")
            global save_id
            save_id = "1.1."
            for link in data['links']:
                if(link['num'] == interface['link']):
                    fichier.write((link['num'])+".")
                    save_id += link['num']+"."
                    if(link['router1'] == router_conf['name']):
                        save_id += "1"
                        fichier.write("1 ")
                    if(link['router2'] == router_conf['name']):
                        save_id += "2"
                        fichier.write("2 ")
                    mask = "255.255.255.252\n"
                    fichier.write(mask)
                    network = "1.1."+(link['num'])+".0 " + "mask " + mask
                    networks.append(network)
        else:
            fichier.write(" ip address 10.10.")
            for link in data['links']:
                if(link['num'] == interface['link']):

                    fichier.write((link['num'])+".")
                    if(link['router1'] == router_conf['name']):
                        fichier.write("1 ")
                    if(link['router2'] == router_conf['name']):
                        fichier.write("2 ")
                    mask = "255.255.255.0\n"
                    fichier.write(mask)
                    network = "10.10."+(link['num'])+".0 " + "mask " + mask
                    networks.append(network)
    if ("protocols" in interface):
        if("OSPF" in interface['protocols']):
            fichier.write(
                " ip ospf " + router_conf["ospf_process_id"] + " area " + str(router_conf['ospf_area_id'])+"\n")
            if (interface['link'] != "0"):
                if (interface['name'][1] == 'F'):
                    fichier.write("duplex full\n")
                else:
                    fichier.write(" negotition auto\n")


def conf_interfaces(fichier, router_conf, data):
    for interface in router_conf['interfaces']:
        # interface qui sont down
        fichier.write("! Config une interface \n")
        if(str(interface['state']) == "down"):
            conf_inter_down(fichier, router_conf, interface)

        # interface qui sont up
        if(str(interface['state']) == "up"):
            conf_inter_up(fichier, router_conf, data, interface)


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


def conf_bgp(fichier, router_conf, data):
    # Configuration de bgp
    fichier.write("router bgp "+router_conf["bgp_as"]+"\n")
    ind = router_conf["name"]
    loop_add = ind[1:]+"."+ind[1:]+"."+ind[1:]+"."+ind[1:]
    if (router_conf["type"] != "PEc"):
        fichier.write("bgp router-id " + loop_add + "\n")
    else:
        global save_id
        fichier.write("bgp router-id " + save_id + "\n")
    fichier.write(" bgp log-neighbor-changes\n")

    for other_router in data["routers"]:
        if (router_conf["name"] != other_router["name"]) & (other_router["bgp_as"] == router_conf["bgp_as"]):
            ind = other_router["name"]
            addresses_others = ind[1:]+"."+ind[1:]+"."+ind[1:]+"."+ind[1:]
            fichier.write(" neighbor "+addresses_others +
                          " remote-as "+other_router["bgp_as"]+"\n")
            fichier.write(" neighbor "+addresses_others +
                          " update-source Loopback0\n")
        # Si c'est un routeur de bordure on doit ajouter les autres routeurs de bordure à notre config
        # if Routeur de bordure de l'AS associé à routeur de bordure d'une autre AS
        twoPE_routers = (router_conf["type"] == "PE") & (other_router["type"] == "PEc") | (
            (router_conf["type"] == "PEc") & (other_router["type"] == "PE"))
        if (twoPE_routers):
            for interface in router_conf["interfaces"]:

                if (interface['name'] != "Loopback0") & (interface['state'] == 'up'):
                    # Routers_connected
                    if interface['router'] == other_router['name']:
                        for link in data["links"]:
                            if ((link['router1'] == router_conf["name"]) & (link['router2'] == other_router['name'])):
                                address = "1.1."+link["num"]+".2"
                                fichier.write(
                                    " neighbor "+address+" remote-as "+other_router['bgp_as']+"\n")
                            elif ((link['router2'] == router_conf["name"]) & (link['router1'] == other_router['name'])):
                                address = "1.1."+link["num"]+".1"
                                fichier.write(
                                    " neighbor "+address+" remote-as "+other_router['bgp_as']+"\n")

    fichier.write("!\n")
    # Ici pour les routeurs de bordures indiqué les chemins network mask + Loopbackk
    # Les activates sont useless
    if (router_conf["type"] == "PE"):
        fichier.write("address-family ipv4\n")
        for network in networks:
            fichier.write(" "+network)

    fichier.write("exit-address-family\n")


if __name__ == "__main__":

    with open('data_cop.json', 'r') as json_file:
        data = json.load(json_file)
    # there is a file to push for each router to configure
    networks = []
    for router_conf in data['routers']:
        # Commentaire à enlever pour le vrai test
        path = "OSPF/project-files/dynamips/"
        path += router_conf["folder_name"]+"/configs/i"
        # path += "/configs"
        # path += "router "+str(router_conf['name'])+" configuration"
        path += router_conf["name"][1:]
        fichier = open(path+"_startup-config.cfg", 'w+')
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
        if "bgp_as" in router_conf:
            conf_bgp(fichier, router_conf, data)
        conf_end(fichier)

        fichier.close()
        networks.clear()
        """"Problème d'itération quand on write sur le fichier
        le curseur va à la fin donc on ne peut pas ecrire dessus"""
