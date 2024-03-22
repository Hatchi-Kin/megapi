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
├── music.db
├── readme.md
├── requirements.txt
├── source
│   ├── data
│   │   └── database.py
│   ├── dependencies
│   │   └── config.py
│   ├── models
│   │   ├── music.py
│   │   └── users.py
│   ├── routes
│   │   ├── auth.py
│   │   └── music_library.py
│   └── templates
│       └── index.html
├── populate.py
└── tests.py
```