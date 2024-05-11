## install poetry

```bash
python3 -m venv $VENV_PATH
$VENV_PATH/bin/pip install -U pip setuptools
$VENV_PATH/bin/pip install poetry
```

## activate virtual env
```bash
source $VENV_PATh/bin/activate
```

## #####
```bash
docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Names}}'
```

```bash
docker stop $(docker ps -a -q)
```

```bash
docker rm $(docker ps -a -q)
```

```bash
docker rmi $(docker images -q)
```

```bash
docker volume rm $(docker volume ls -q)
```

```bash
docker network rm $(docker network ls -q)
```

```bash
docker system prune -a --volumes
```

```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```
 
## ######

```bash
docker compose up -d
```

```bash
docker compose build --no-cache
```

```bash
docker-compose logs -f
```

```bash
.
├── app.py
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── poetry.lock
├── pyproject.toml
├── README.md
│
├── core
│   ├── __init__.py
│   ├── database.py
│   ├── config.py
│   └── data
│       └── music.db
│
├── gui
│   └── templates
│       └── index.html
│
├── models
│   ├── __init__.py
│   ├── milvus.py
│   ├── minio.py
│   ├── music.py
│   ├── spotinite.py
│   └── users.py
│
├── routes
│   ├── __init__.py
│   ├── auth.py
│   ├── lyrics.py
│   ├── milvus.py
│   ├── music.py
│   └── spotinite.py
│
├── services
│   ├── __init__.py
│   ├── auth.py
│   ├── lyrics.py
│   ├── milvus.py
│   ├── minio.py
│   └── spotinite.py
│
└── tests
    ├── __init__.py
    └── test_files.py
```


## GitHub SECRETS

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