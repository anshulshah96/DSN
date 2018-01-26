FROM node:latest

MAINTAINER Anshul Shah <shahanshul08@gmail.com>

RUN apt-get update

RUN npm install -g ethereumjs-testrpc

RUN apt-get install -y \
    python2.7 python-dev \
    python-pip \
    supervisor curl telnet libssl-dev 

RUN pip install --upgrade pip
RUN pip install virtualenv

WORKDIR /home/app

RUN virtualenv -p python2.7 pyenv
RUN /bin/bash -c "source pyenv/bin/activate"

RUN mkdir -p /home/app /home/log /home/rpcdb

# install dependencies
COPY ./requirements.txt /home/app/
RUN pip install -r /home/app/requirements.txt

# copy source code
COPY . /home/app/

COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8900
EXPOSE 8545

CMD ["supervisord", "-n"]