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
│   ├── music.py
│   └── users.py
│
├── routes
│   ├── __init__.py
│   ├── auth.py
│   ├── milvus.py
│   └── music.py
│
├── services
│   ├── __init__.py
│   ├── auth.py
│   └── milvus.py
│
└── tests
    ├── __init__.py
    └── test_files.py
```