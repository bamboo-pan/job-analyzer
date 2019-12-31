from common.yaml_functions import read_yaml,save_yaml
import os

class Config():
    def __init__(self):
        self.clear_config()
        self.load_config()

    def generate_config(self):
        self.configs = {
            "credentials":
                {
                    "my_id": self.my_id,
                    "my_token": self.my_token,
                    "my_region": self.my_region
                },
            "config":
                {
                    "script": self.script,
                    "remove_old_all": self.remove_old_all,
                    "remove_old_instances": self.remove_old_instances,
                    "add_script": self.add_script,
                    "os_type": self.os_type,
                    "memory": self.memory,
                    "cpu_cores": self.cpu_cores,
                    "count": self.count,
                    "brand_width": self.brand_width,
                    "disksize": self.disksize,
                    "instance_sets":
                        {
                            "user": self.user,
                            "pwd": self.pwd,
                            "ssh_port": self.ssh_port,
                            "port_start": self.port_start,
                            "port_end": self.port_end,
                            "finish_flag": self.finish_flag
                        }
                }

        }

    def clear_config(self):
        self.my_id = None
        self.my_token = None
        self.my_region = None
        self.script =None
        self.remove_old_all = None
        self.remove_old_instances = None
        self.add_script = None
        self.os_type = None
        self.memory = None
        self.cpu_cores =None
        self.count = None
        self.brand_width = None
        self.disksize = None
        self.user = None
        self.pwd = None
        self.ssh_port = None
        self.port_start = None
        self.port_end = None
        self.finish_flag = None

    def default_config(self):
        pass

    def save_config(self):
        save_yaml(self.configs, r".\config\config.yml")

    def load_config(self):
        self.configs=read_yaml(r".\config\config.yml")
        self.my_id = self.configs.get("credentials").get("my_id")
        self.my_token = self.configs.get("credentials").get("my_token")
        self.my_region = self.configs.get("credentials").get("my_region")
        self.script =self.configs.get("config").get("script")
        self.remove_old_all = self.configs.get("config").get("remove_old_all")
        self.remove_old_instances = self.configs.get("config").get("remove_old_instances")
        self.add_script = self.configs.get("config").get("add_script")
        self.os_type = self.configs.get("config").get("os_type")
        self.memory = self.configs.get("config").get("memory")
        self.cpu_cores =self.configs.get("config").get("cpu_cores")
        self.count = self.configs.get("config").get("count")
        self.brand_width = self.configs.get("config").get("brand_width")
        self.disksize = self.configs.get("config").get("disksize")
        self.user = self.configs.get("config").get("instance_sets").get("user")
        self.pwd = self.configs.get("config").get("instance_sets").get("pwd")
        self.ssh_port = self.configs.get("config").get("instance_sets").get("ssh_port")
        self.port_start = self.configs.get("config").get("instance_sets").get("port_start")
        self.port_end = self.configs.get("config").get("instance_sets").get("port_end")
        self.finish_flag = self.configs.get("config").get("instance_sets").get("finish_flag")


if __name__ == '__main__':
    config=Config()
    print(config)