import requests
import json
from common.web import WEB,PROXY,AGENT
from common.yaml_functions import read_yaml,save_yaml,insert_yaml
import os
from common.logger import Logger



class BAIDU(WEB):
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
        self.region = "&region=" + self.city
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
        self.configs = read_yaml(r".\config\bd_config.yml")
        self.go_type=self.configs.get("go_type")
        self.city=self.configs.get("city")
        self.key=self.configs.get("key")

    def save_config(self):
        save_yaml(self.configs,r".\config\bd_config.yml")

    def get(self):
        response = requests.get(self.url, headers=self.header, proxies=self.proxy, timeout=self.timeout)
        self.js=json.loads(response.content)
        return response

    def prepare(self):
        self.agent_instance = AGENT()
        self.proxy_instance = PROXY()

    def load_poi(self):
        poi_bd=os.path.join(os.getcwd(),"data","poi_bd")
        if not os.path.exists(poi_bd):
            with open(poi_bd, "w") as f:
                pass
        try:
            self.poi_dict = read_yaml(poi_bd)
        except Exception as e:
            Logger().get_logger().exception(str(e))
        if self.poi_dict is None:
            self.poi_dict = {}

    def insert_poi(self,target_name,str):
        if not target_name in self.poi_dict:
            Logger()("add {} poi data to {}".format(target_name, "poi_bd"))
            self.poi_dict[target_name]=str
            # self.save_poi()

    def save_poi(self):
        try:
            poi_bd = os.path.join(os.getcwd(), "data", "poi_bd")
            save_yaml(self.poi_dict,poi_bd)
        except Exception as e:
            Logger().get_logger().exception(str(e))

    def get_location(self,target_name):

        if target_name in self.poi_dict:
            Logger()("find {} poi data in {}".format(target_name,"poi_bd"))
            return True,self.poi_dict.get(target_name)

        self.url="http://api.map.baidu.com/place/v2/search?query=" + target_name + self.region + self.output + self.key
        self.encoding="UTF-8"
        self.header = {'User-Agent': self.agent_instance.get_random_agent()}
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()
        self.get()
        js_results = self.js.get("results")
        if len(js_results):
            if "location" in js_results[0]:
                str = "{},{}".format(js_results[0].get("location").get("lat"),
                                     js_results[0].get("location").get("lng"))
                self.insert_poi(target_name,str)
                return True, str
            else:
                return False, "can not find location:{}".format(target_name)

        else:
            return False, "can not find location:{}".format(target_name)

    def prepare_poi(self):
        origin_res=self.get_location(self.origin)
        destination_res=self.get_location(self.destination)
        if origin_res[0] and destination_res[0]:
            self.origin_poi=self.get_location(self.origin)[1]
            self.destination_poi=self.get_location(self.destination)[1]
            return True
        else:
            return False


    def get_route(self):
        self.header = {'User-Agent': self.agent_instance.get_random_agent()}
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()
        if self.go_type == "transit":
            self.url = "http://api.map.baidu.com/directionlite/v1/transit?origin=" + self.origin_poi + "&destination=" + self.destination_poi + self.key
        elif self.go_type == "walking":
            self.url = "http://api.map.baidu.com/directionlite/v1/walking?origin=" + self.origin_poi + "&destination=" + self.destination_poi + self.key
        elif self.go_type == "driving":
            self.url = "http://api.map.baidu.com/directionlite/v1/driving?origin=" + self.origin_poi + "&destination=" + self.destination_poi + self.key
        self.encoding = "UTF-8"
        self.get()
        data = self.js
        if data.get("status") != 0:
            return 0,0,0
        if self.go_type == "transit":
            selections = data.get("result").get("routes")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = item.get("duration")
            min_index = min(durations, key=durations.get)
            distance = selections[min_index].get("distance")
            steps = selections[min_index].get("steps")
            walking_distance = 0
            for i in steps:
                for j in i:
                    if j.get("type") == 5:
                        walking_distance = walking_distance + j.get("distance")

            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0
        elif self.go_type == "walking":
            selections = data.get("result").get("routes")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = item.get("duration")
            min_index = min(durations, key=durations.get)
            distance = selections[min_index].get("distance")
            walking_distance = distance
            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0
        elif self.go_type == "driving":
            selections = data.get("result").get("routes")
            durations = {}
            for index, item in enumerate(selections):
                durations[index] = item.get("duration")
            min_index = min(durations, key=durations.get)
            distance = selections[min_index].get("distance")
            walking_distance = 0
            duration0 = selections[min_index].get("duration")
            return distance, walking_distance, duration0

if __name__ == '__main__':
    pass
