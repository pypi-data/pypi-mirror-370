import json
import os
from typing import Any

from LinuxServerStatsTelegramBot.commmand.Command import Command


class RebootApp(Command):
    def __init__(self, application_name: str = ""):
        self.application_name = application_name
        self.docker_status_file = "/tmp/docker-status.txt"

    def execute(self) -> Any:
        print(f"Reboot application {self.application_name}")
        containers = self.search_containers_by_application_name(application_name=self.application_name)
        if len(containers) > 0:
            self.delete_status_file()
            for container in containers:
                docker_compose_path =  container["dockerComposePath"]
                self.down_container(docker_compose_path)
                self.up_container(docker_compose_path)
                self.status_container(docker_compose_path)
            return self.read_status_file()

    @staticmethod
    def down_container(docker_compose_path: str) -> None:
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml down --remove-orphans'
        os.system(command)

    @staticmethod
    def up_container(docker_compose_path: str) -> None:
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml up -d'
        os.system(command)

    def status_container(self, docker_compose_path: str) -> str:
        command = f'docker-compose -f {docker_compose_path}/docker-compose.yml ps >> {self.docker_status_file}'
        os.system(command)

    def delete_status_file(self):
        os.system(f"rm {self.docker_status_file}")

    def read_status_file(self):
        with open(self.docker_status_file, "r") as file:
            data = file.read()
        return data

    def search_containers_by_application_name(self, application_name: str) -> list:
        applications_obj: dict = self.read_applications_list()
        for app in applications_obj:
            if app["name"] == application_name:
                return app["containers"]
        return []

    def missing_container_name(self):
        text = "Missing application_name. Possibles name are:"
        text = text + self.application_list_as_text()
        return text

    def application_list_as_text(self) -> str:
        applications = ""
        try:
            applications = "\n"
            applications_obj: dict = self.read_applications_list()
            for app in applications_obj:
                applications = applications + app["name"] + "\n"
        except Exception as error:
            print(error)
        return applications

    @staticmethod
    def read_applications_list() -> dict:
        with open("/etc/telegram-bot/applications.json", "r") as file:
            data = file.read()
        return json.loads(data)

