# Plataforma Sabiá

## Installation

1 - Clone Git repository:

  ```
  git clone https://github.com/carlosribas/sabia.git
  ```

2 - Run the app using [Docker](https://www.docker.com):

  ```
  cd sabia
  docker build -t "sabia:Dockerfile" .
  docker images
  docker run -p 8000:8000 -d <sabia_image_id>
  docker ps
  docker exec -it <container_id> python manage.py createsuperuser
  ```

3 - Open your browser and type ```localhost:8000/admin```



**Docker Cheat Sheet**

```
# connect to a running container
docker ps
docker exec -it <container_id> bash
```
