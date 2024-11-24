# MegaPi (FastAPI)

Megapi est un backend complet FastAPI pour le projet music-sim. Il fournit une API RESTful pour que le frontend puisse interagir avec. Il sert également un modèle de ML pour prédire les genres musicaux. Il se connecte à une base de données PostgreSQL pour stocker les données des utilisateurs et les métadonnées musicales. Il utilise MinIO pour stocker les fichiers musicaux et Milvus pour stocker les embeddings musicaux. Il utilise également l'API Cyanite pour comparer les services de recommandation musicale, ainsi qu'une autre API pour récupérer les paroles des chansons lorsque disponibles. Le projet est containerisé à l'aide de Docker et peut être déployé avec docker compose.

## Technologies Utilisées

- FastAPI
- PostgreSQL
- MinIO
- Milvus (hébergé par Zilliz)
- API Cyanite
- OpenL3

## Documentation

La documentation complète est généré à l'aide de MKDocs et est disponible à l'adresse suivante : [https://hatchi-kin.github.io/megapi/](https://hatchi-kin.github.io/megapi/)

## Lancer le projet avec Docker

Pour lancer le projet, utilisez les commandes suivantes :

```bash
docker compose up -d
```

Pour vérifier les conteneurs en cours d'exécution :
```bash
docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Names}}'
```

```bash
NAMES                           PORTS

megapi-megapi-1                 8000:8000
megapi-minio-1                  9000:9001
megapi-postgre-1                5432:5432

react-music-sim-web-1           3000:3000

monitoring-stack-mlflow-1       5000:5000
monitoring-stack-mlflowdb-1     3306/tcp
monitoring-stack-prometheus-1   9090:9090
grafana                         3030:3030

nginx-proxy-app-1               80:81, 443:443
portainer-portainer-1           9443:9443,8008:8000, 9009:9009
```
 





## Secrets GitHub

`PI_SSH_KNOWN_HOST_KEY`: Clé d'hôte SSH pour votre Raspberry Pi.
`PI_SSH_PRIVATE_KEY`: Clé privée de la paire de clés SSH utilisée pour se connecter à votre Raspberry Pi.
`SSH_PI_USERNAME`: Nom d'utilisateur utilisé pour se connecter en SSH à votre Raspberry Pi.
`SSH_PI_HOST_LIVEBOX_IP`: Nom d'hôte ou adresse IP de votre Raspberry Pi.
`SSH_PI_PORT`: Port d'écoute SSH de votre Raspberry Pi.

## Configuration SSH pour GitHub
Pour permettre au Raspberry Pi de se connecter à GitHub via SSH, créez un fichier de configuration dans /home/pi/.ssh/config avec le contenu suivant :

- `PI_SSH_KNOWN_HOST_KEY`: This is the SSH host key for your Raspberry Pi. It's used to verify the identity of the Raspberry Pi when establishing an SSH connection. You can find it in your `known_hosts` file on the machine you use to SSH into your Raspberry Pi. The host key is the entire line in the `known_hosts` file that corresponds to your Raspberry Pi.
To obtain the host key, you can rename your existing `known_hosts` file to `known_hosts_BACKUP` on your local machine, then SSH into your Raspberry Pi. This will create a new `known_hosts` file. The content of this new file is the `PI_SSH_KNOWN_HOST_KEY` secret.

- `PI_SSH_PRIVATE_KEY`: This is the private key of the SSH key pair that you use to connect to your Raspberry Pi. You can find it in your .ssh directory on the machine you use to SSH into your Raspberry Pi. It's typically named id_rsa, id_ed25519, or similar.

- `SSH_PI_USERNAME`: This is the username that you use to SSH into your Raspberry Pi. 

- `SSH_PI_HOST_LIVEBOX_IP`: This is the hostname or IP address of your Raspberry Pi. In our setup, it actually is the ip of the LIVEBOX that redirects to the raspberry's ip at `SSH_PI_PORT` usually the default for ssh is port 22

- `SSH_PI_PORT`: This is the port that your Raspberry Pi listens on for SSH connections. If you're using the default SSH configuration on your Raspberry Pi, this is likely 22. If you've changed the SSH port on your Raspberry Pi, use the port you've changed it to.

## Le workflow gh action

pour que le pi puisse ssh into gh

creer un fichier config dans `/home/pi/.ssh/config` avec:
```
Host github-megapi
	HostName github.com 
    AddKeysToAgent yes 
    PreferredAuthentications publickey 
    IdentityFile ~/.ssh/id_ed25519_gh_megapi
```
et une clé privée nommé `id_ed25519_gh_megapi`

## Structure du Projet

```bash
.
├── app.py
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── mkdocs.yml
├── README.md
│
├── core
│   ├── data
│   │   ├── mtg_jamendo_genre.json
│   │   └── music.db
│   ├── __init__.py
│   ├── database.py
│   ├── extract_openl3_embeddings.py
│   ├── config.py
│   └── extract_openl3_embeddings.py
│
├── docs
│   ├── index.md
│   ├── endpoints
│   └── services
│
├── gui
│   └── templates
│       └── index.html
│
├── models
│   ├── __init__.py
│   ├── favorites.py
│   ├── milvus.py
│   ├── minio.py
│   ├── music.py
│   ├── openl3.py
│   ├── spotinite.py
│   ├── uploaded.py
│   └── users.py
│
├── routes
│   ├── __init__.py
│   ├──  auth.py
│   ├── elo.py
│   ├── favorites.py
│   ├── lyrics.py
│   ├── milvus.py
│   ├── minio.py
│   ├── monitoring.py
│   ├── music_net.py
│   ├── music.py
│   ├── openl3.py
│   ├── spotinite.py
│   └── uploaded.py
│
├── services
│   ├── __init__.py
│   ├── auth.py
│   ├── favorites.py
│   ├── lyrics.py
│   ├── milvus.py
│   ├── minio.py
│   ├── monitoring.py
│   ├── music_net.py
│   ├── music.py
│   ├── openl3.py
│   ├── spotinite.py
│   └── uploaded.py
│
├── site
│   └── ...
│
└── tests
    ├── __init__.py
    ├── test_auth.py
    ├── test_favorites.py
    ├── test_files.py
    ├── test_milvus.py
    └── test_minio.py
```