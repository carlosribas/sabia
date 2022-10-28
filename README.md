# Baroni-Massad website

## Installation

1 - Clone Git repository:

  ```
  git clone https://github.com/carlosribas/sabia.git
  ```

2 - cd into the directory

  ```
  cd sabia
  ```

3 - Edit the sabia/settings/local_example.py file and rename it to local.py

4 - Run the app using [Docker](https://www.docker.com):

  ```
  docker-compose up -d --build
  docker ps
  docker exec -it <sabia_web_container_id> python manage.py migrate
  docker exec -it <sabia_web_container_id> python manage.py createsuperuser
  ```

5 - Open your browser and type ```localhost:8000/admin```



**Docker Cheat Sheet**

```
# connect to a running container
docker ps
docker exec -it <container_id> bash
```
