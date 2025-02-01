import container
from initial_scenarios.FastApiWebsite import FastApiWebsite
from pathlib import Path
from modules import ShellModule
from chat import Chat
from config import Config


def new_container(manager):
    name = input("Название проекта(en):\n>>> ")
    name = name.replace(" ", "-")
    container = manager.new(name)
    return container


with container.ContainerManager() as manager:
    config = Config.load("./")
    containers = manager.list()
    while True:
        print(f"Выберите проект(1-{len(containers) + 1}):")
        for i, container in enumerate(containers, start=1):
            print(f"{i} - {container.name}")
        print(f"{len(containers) + 1} - Создать новый")
        index = input(">>> ")
        if index.isdigit():
            index = int(index)
            if 0 < index < len(containers) + 1:
                container = containers[index - 1]
                break
            elif index == len(containers) + 1:
                container = new_container(manager)
                break
            else:
                print("Проект не найден")
        else:
            print("Ожидается номер проекта(число)")
    print(container.name)
    manager.start(container)
    with Chat(0, manager.to_path(container), config, scenario=FastApiWebsite()) as chat:
        while True:
            inp = input("(exit or question)>>>")
            if inp == "exit":
                break
            for s in chat.process(inp):
                print(s, sep="", end="")
            print()
    #print(container.name)
    #manager.new()
    #ShellModule(Path("/home/bobah/QwenProjects/qed1-test-1738061654"))
