# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.
* `mkdocs gh-deploy` - Deploy the documentation to GitHub Pages.

## Project layout

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
