# Используем минимальный образ Ubuntu
FROM ubuntu:latest

# Обновляем список пакетов и устанавливаем apt
RUN apt-get update
RUN apt install -y python3 python3-dev python3-pip python3-venv
RUN apt install -y git

RUN python3 -m venv /venv
RUN bash -c "source venv/bin/activate && pip install --upgrade pip"

RUN git config --global credential.helper store
RUN echo "http://qwen-enginer:13eqqedgbc@git.mstat.kz" > ~/.git-credentials

VOLUME ["/project"]

WORKDIR /project
