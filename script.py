import json



def read_json():

    with open('data.json') as json_file:
        data = json.load(json_file)
        for p in data['routers']: # ici changer les champs 
            # print('Name: ' + p['name'])
            # print('Website: ' + p['website'])
            # print('From: ' + p['from'])
            # print('')
            for i in p['interfaces']
            if(i['protocol'] == "OSPF") :
                #generate config
                print('Name of router : \n' + p['name'])
            


if __name__ == "__main__":
    print("Début main")
    read_json()
    print("Fin main")

