# Oracle Service

### Setup

  - Install Docker.
  - ```docker run --rm -d -p 8900:8900 -p 8545:8545 --name oracle anshulshah96/oracle:latest```
  - For Debugging ```docker exec -it oracle bash```
  - Stop the container using ```docker stop oracle```