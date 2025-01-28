import docker
import time
from typing import List, Dict
from pathlib import Path


class ContainerManager:
    __self__ = None
    
    __docker: docker.DockerClient
    main_image = "bobahpyt/qwen-enginer"
    base_urls = ["unix:///var/run/docker.sock", "npipe:////./pipe/docker_engine"]
    __containers: List[docker.models.containers.Container]
    
    def __init__(self):
        self.__containers = []
        
        for url in self.base_urls:
            try:
                self.__docker = docker.DockerClient(base_url=url)
                self.__docker.ping()
                break
            except:
                print(f"Не удалось подключиться к docker через {url}")
        else:
            try:
                self.__docker = docker.from_env()
                self.__docker.ping()
            except:
                print(f"Не удалось подключиться к docker. Проверьте установку docker.")
                quit()

    def __new__(cls, *args, **kwargs):
        if cls.__self__ is None:
            cls.__self__ = super().__new__(cls, *args, **kwargs)
        return cls.__self__

    def close(self):
        for container in self.__containers:
            try:
                container.stop()
            except:
                pass
        self.__docker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get(self, container) -> docker.models.containers.Container:
        if not isinstance(container, docker.models.containers.Container):
            for c in self.list():
                if container in (c.name, c.id, c.short_id) or c.name.startswith(f"qed1-{container}"):
                    return c
        return container

    def list(self):
        return list(filter(lambda x: "qed1-" in x.name, self.__docker.containers.list(all=True)))

    def new(self, name):
        name = f"qed1-{name}-{int(time.time())}"
        dirname = Path(f"~/QwenProjects/{name}").expanduser()
        dirname.mkdir(parents=True, exist_ok=True)
        
        container = self.__docker.containers.run(self.main_image, detach=True, name=name, volumes={str(dirname): {"bind": "/project", "mode": "rw"}}, command="sleep infinity")
        self.__containers.append(container)
        
        return container

    def start(self, container):
        container = self.get(container)
        container.start()
        self.__containers.append(container)
        return container

    def remove(self, container):
        container = self.get(container)
        if container.status != "exited":
            container.stop()
        container.remove()

    def exec(self, container, cmd):
        container = self.get(container)
        exec_id = self.__docker.api.exec_create(container.id, cmd, stdin=True, tty=True)['Id']
        sock = self.__docker.api.exec_start(exec_id, socket=True)._sock
        return sock

    def to_path(self, container):
        container = self.get(container)
        dirname = Path(f"~/QwenProjects/{container.name}").expanduser()
        return dirname
