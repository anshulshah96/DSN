# Oracle Service

### Setup

  - Install Docker.
  - ```docker run --rm -d -p 8900:8900 -p 8545:8545 --name oracle anshulshah96/oracle:latest```
  - For Debugging ```docker exec -it oracle bash```
  - Stop the container using ```docker stop oracle```

## Demo links

  - ```http://localhost:8900/list```
  - ```http://localhost:8900/challenge?adds=0xea0b1d06ee5393635436f1e542ea418ff719e15a&size=10```
  - ```http://localhost:8900/issue?adds=0xea0b1d06ee5393635436f1e542ea418ff719e15a&sol=10```

## TestRPC Command

  - ```testrpc -m "web head biology poet unfold fetch danger tonight sick random version expand" -g 2000 -l 9000000```