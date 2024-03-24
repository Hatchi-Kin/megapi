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
 
###################################################

```bash
docker-compose logs -f
```





```bash
.
├── app.py
├── docker-compose.yaml
├── Dockerfile
├── readme.md
├── requirements.txt
└── source
    ├── data
    │   ├── migrate_data.py
    │   ├── music.db
    ├── __init__.py
    ├── models
    │   ├── embedding_512.py
    │   ├── music.py
    │   └── users.py
    ├── __pycache__
    │   └── __init__.cpython-310.pyc
    ├── routes
    │   ├── auth.py
    │   ├── milvus.py
    │   ├── music_library.py
    ├── settings
    │   ├── config.py
    └── templates
        └── index.html

```