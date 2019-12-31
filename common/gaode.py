import requests
import json
from common.web import WEB,PROXY,AGENT
from common.yaml_functions import read_yaml,save_yaml
import os
from common.logger import Logger

class GAODE(WEB):
    def __init__(self):
        super().__init__()
        self.proxy_instance=""
        self.agent_instance=""
        self.origin=None
        self.destination=None
        self.origin_poi = None
        self.destination_poi = None
        self.load_config()
        self.output = "&output=json"
        self.region = "&city=" + self.city
        self.poi_dict={}
        # self.load_poi()
        self.js=None

    def clear_config(self):
        self.go_type=None
        self.city=None
        self.key=None

    def generate_config(self):
        self.configs={
            "go_type":self.go_type,
            "city":self.city,
            "key":self.key
        }

    def load_config(self):
        self.configs = read_yaml(r".\config\gd_config.yml")
        self.go_type=self.configs.get("go_type")
        self.city=self.configs.get("city")
        self.key=self.configs.get("key")

    def save_config(self):
        save_yaml(self.configs,r".\config\gd_config.yml")

    def get(self):
        response = requests.get(self.url, headers=self.header, proxies=self.proxy, timeout=self.timeout)
        self.js = json.loads(response.content)
        return response

    def prepare(self):
        self.agent_instance = AGENT()
        self.proxy_instance = PROXY()

    def prepare_poi(self):
        origin_res=self.get_location(self.origin)
        destination_res=self.get_location(self.destination)
        if origin_res[0] and destination_res[0]:
            self.origin_poi=self.get_location(self.origin)[1]
            self.destination_poi=self.get_location(self.destination)[1]
            return True
        else:
            return False

    def load_poi(self):
        poi_gd = os.path.join(os.getcwd(), "data", "poi_gd")
        if not os.path.exists(poi_gd):
            with open(poi_gd, "w") as f:
                pass
        try:
            self.poi_dict = read_yaml(poi_gd)
        except Exception as e:
            Logger().get_logger().exception(str(e))
        if self.poi_dict is None:
            self.poi_dict = {}

    def insert_poi(self,target_name,str):
        if not target_name in self.poi_dict:
            Logger()("add {} poi data to {}".format(target_name, "poi_gd"))
            self.poi_dict[target_name]=str
            # self.save_poi()

    def save_poi(self):
        try:
            poi_gd = os.path.join(os.getcwd(), "data", "poi_gd")
            save_yaml(self.poi_dict, poi_gd)
        except Exception as e:
            Logger().get_logger().exception(str(e))

    def get_location(self,target_name):
        if target_name in self.poi_dict:
            Logger()("find {} poi data in {}".format(target_name, "poi_gd"))
            return True,self.poi_dict.get(target_name)

        self.url="https://restapi.amap.com/v3/place/text?keywords=" + target_name + self.region + self.output + "&offset=1&page=1" + self.key + "&extensions=all"
        self.encoding="UTF-8"
        self.header = {'User-Agent': self.agent_instance.get_random_agent()}
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()
        self.get()
        data= self.js
        if len(data.get("pois")):
            if "location" in data.get("pois")[0]:
                str = data.get("pois")[0].get("location")
                self.insert_poi(target_name, str)
                return True, str
            else:
                return False, "gd can not find location:{}".format(target_name)
        else:
            return False, "gd can not find location:{}".format(target_name)

    def get_route(self):
        self.header = {'User-Agent': self.agent_instance.get_random_agent()}
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()
        if self.go_type == "transit":
            self.url = "https://restapi.amap.com/v3/direction/transit/" + "integrated" + "?origin=" + self.origin_poi + "&destination=" + self.destination_poi + "&city=021" + self.output + self.key
        elif self.go_type == "walking":
            self.url = "https://restapi.amap.com/v3/direction/" + "walking" + "?origin=" + self.origin_poi + "&destination=" + self.destination_poi + self.output + self.key
        elif self.go_type == "driving":
            self.url = "https://restapi.amap.com/v3/direction/" + "driving" + "?origin=" + self.origin_poi + "&destination=" + self.destination_poi + "&strategy=10" + self.output + self.key
        self.encoding = "UTF-8"
        self.get()
        data = self.js
        if data.get("status") == "0":
            # Common.log(data.get("info"))
            return 0,0,0
        if self.go_type == "transit":
            selections = data.get("route").get("transits")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = int(item.get("duration"))
            min_index = min(durations, key=durations.get)
            # distance = data.get("route").get("distance")
            distance=selections[min_index].get("distance")
            walking_distance = selections[min_index].get("walking_distance")
            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0
        elif self.go_type == "walking":
            selections = data.get("route").get("paths")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = int(item.get("duration"))
            min_index = min(durations, key=durations.get)
            distance = selections[min_index].get("distance")
            walking_distance = distance
            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0
        elif self.go_type == "driving":
            selections = data.get("route").get("paths")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = int(item.get("duration"))
            min_index = min(durations, key=durations.get)
            distance = selections[min_index].get("distance")
            walking_distance = 0
            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0