# projet_NAS
Projet de NAS, 1er semestre 2021 4ème année



Le projet est divisé en plusieurs éléments : 
 - un fichier .gns3 qui est constitué de notre topologie sans aucune configuration.
 - un fichier .json qui représente notre configuration sous un format spécifique.
 - plusieurs facons de mettre à jour la configuration de notre réseau avec une nouvelle configuration

1ère facon de faire :

branche samitest 
-On utilise script.py qui a deux modes de configuration : 

`$ script.py 0`
permet de mettre la configuration olddata_test2.json sur la topologie non-configuré du réseau.


`$ script.py 1`
permet de mettre à jour la configuration avec le fichier newdata_test.json.

Précision sur le format utilisé et les maj possibles :

1) on est dans la théorie de la configuration parfaite en supposant que l'opérateur en question ne s'est pas trompé dans le .json. Par exemple, on ne peut pas avoir deux fois le même routeur ou deux fois la même interface pour un routeur.
2) Lorsqu'un champ "type","type_as","port","ospf_area_id","ospf_process_id","bgp_as": "110" d'un routeur change alors il faut automatiquement changer l'id du routeur en question. Pareil dans interface, si un champ change alors c'est nécessairement que la donnée dans "link" doit aussi changer. Ceci est dû au fait que script.py se base sur le changement de ces champs pour détecter une modification du fichier.
3) On a des actions limités sur la configuration du réseau : on peut supprimer un routeur ou une interface, en ajouter un ou changer un champ à condition de respecter le 2). Par contre, le programme ne détecte pas si on change seulement les protocoles sur une interface.
