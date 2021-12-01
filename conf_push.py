import json
from os import path
if __name__ == "__main__":
    print('Début')

    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
        print(data['routers'])
    # there is a file to push for each router to configure
    j = 0
    for i in data['routers']:
        print("VOila le i \n", i)
        path = "projet/"
        path += str(i['name'])
        fichier = open(path+".cfg", 'w+')
        fichier.write("\nConfig test "+str(j))
        j = j+1
        fichier.close()

    path = "projet/"
    path += "node_id_1"
    print(path)

    print(fichier.readline())
