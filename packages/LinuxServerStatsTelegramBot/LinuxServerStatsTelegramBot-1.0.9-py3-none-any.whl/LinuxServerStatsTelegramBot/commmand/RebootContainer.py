import json
import os
from typing import Any

from LinuxServerStatsTelegramBot.commmand.Command import Command


class RebootContainer(Command):
    def __init__(self, container_name: str = ""):
        self.container_name = container_name

    def execute(self) -> Any:
        print(f"Reboot container {self.container_name}")
        docker_compose_path = self.search_container_by_name(container_name=self.container_name)
        if docker_compose_path != "":
            self.down_container(docker_compose_path)
            self.up_container(docker_compose_path)
            return self.status_container(docker_compose_path)

    @staticmethod
    def down_container(docker_compose_path: str) -> None:
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml down --remove-orphans'
        os.system(command)

    @staticmethod
    def up_container(docker_compose_path: str) -> None:
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml up -d'
        os.system(command)

    @staticmethod
    def status_container(docker_compose_path: str) -> str:
        docker_status_file = "/tmp/docker-status.txt"
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml ps > {docker_status_file}'
        os.system(command)
        with open(docker_status_file, "r") as file:
            data = file.read()
        return data

    def search_container_by_name(self, container_name: str) -> str:
        applications_obj: dict = self.read_applications_list()
        for app in applications_obj:
            for container in app["containers"]:
                if container["name"] == container_name:
                    return container["dockerComposePath"]
        return ""

    def missing_container_name(self):
        text = "Missing container_name. Possibles name are:"
        text = text + self.container_list_as_text()
        return text

    def container_list_as_text(self) -> str:
        containers = ""
        try:
            containers = "\n"
            applications_obj: dict = self.read_applications_list()
            for app in applications_obj:
                for container in app["containers"]:
                    containers = containers + container["name"] + "\n"
        except Exception as error:
            print(error)
        return containers

    @staticmethod
    def read_applications_list() -> dict:
        with open("/etc/telegram-bot/applications.json", "r") as file:
            data = file.read()
        return json.loads(data)
