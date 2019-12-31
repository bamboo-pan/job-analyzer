from common.yaml_functions import read_yaml,insert_yaml,save_yaml
from common.logger import Logger
import requests
import os,random,re
from common.alibaba import Aliyun_basic,Aliyun_basic_advanced
from common.generate_config import Config


class WEB():
    def __init__(self,url=""):
        self.url=url
        self.encoding="utf-8"
        self.proxy=None
        self.header=None
        self.enable_proxy = False
        self.timeout=10

    def get(self):
        response = requests.get(self.url, headers=self.header, proxies=self.proxy, timeout=self.timeout)
        return response

    def get_txt(self):
        response=self.get()
        response.encoding=self.encoding
        return response.text


class AGENT:
    def __init__(self):
        self.agent_file=os.path.abspath(r".\data\agent.yaml")
        self.agent_list=[]
        self.load_agent()

    def check_file(self):
        if not os.path.exists(self.agent_file):
            with open(self.agent_file, "w") as f:
                pass

    def load_agent(self):
        self.check_file()
        self.agent_list = read_yaml(self.agent_file)
        if self.agent_list is None:
            self.agent_list=[]

    def save_agent(self):
        save_yaml(self.agent_list,self.agent_file)

    def get_random_agent(self):
        self.load_agent()
        return random.choice(self.agent_list)


class PROXY:
    def __init__(self):
        self.proxy_file=os.path.abspath(r".\data\proxy.yaml")
        self.proxy_list=[]
        self.check_pass_proxy_list=[]
        self.check_fail_proxy_list=[]
        self.load_proxy()

    def check_file(self):
        if not os.path.exists(self.proxy_file):
            with open(self.proxy_file, "w") as f:
                pass

    def load_proxy(self):
        self.check_file()
        self.proxy_list = read_yaml(self.proxy_file)
        if self.proxy_list is None:
            self.proxy_list=[]

    def save_proxy(self):
        save_yaml(self.proxy_list,self.proxy_file)

    def get_random_proxy(self):
        self.load_proxy()
        select_proxy= random.choice(self.proxy_list)
        proxies={}
        proxies['http'] = select_proxy
        proxies['https'] = select_proxy
        return proxies

    @staticmethod
    def check_single_proxy(proxy_ip,time_out=0.5):
        url_test = WEB("https://www.baidu.com")
        url_test.proxy = {}
        url_test.proxy["http"] = proxy_ip
        url_test.proxy["https"] = proxy_ip
        url_test.timeout = time_out
        try:
            url_test.get()
            return True
        except Exception as e:
            return False

    def check_all_proxy(self):
        for proxy in self.proxy_list:
            if self.check_single_proxy(proxy):
                self.check_pass_proxy_list.append(proxy)
                Logger()("check {} pass".format(proxy))
            else:
                self.check_fail_proxy_list.append(proxy)
                Logger()("check {} fail".format(proxy))


class CollectFreeProxy(PROXY):
    def __init__(self):
        super().__init__()
        self.proxy_pages=[]
        self.prepare_pages()

    def prepare_pages(self):
        for page in range(1, 4):
            self.proxy_pages.append("https://www.xicidaili.com/nn/" + str(page))
            self.proxy_pages.append("https://www.xicidaili.com/nt/" + str(page))
            self.proxy_pages.append("https://www.xicidaili.com/wn/" + str(page))
            self.proxy_pages.append("https://www.xicidaili.com/wt/" + str(page))

    def get_proxy_on_single_page(self,proxy_page):
        agent_test = AGENT()
        url_test1 = WEB(proxy_page)
        url_test1.encoding = "utf-8"
        url_test1.header = {'Upgrade-Insecure-Requests': '1', 'User-Agent': agent_test.get_random_agent()}
        # proxy=PROXY()
        # url_test1.proxy=proxy.get_random_proxy()
        a = re.findall(
            r'<td class="country">.*?<img.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>.*?</td>.*?<td class="country">.*?</td>.*?<td>(.*?)</td>',
            url_test1.get_txt(), re.S)
        for i in a:
            self.proxy_list.append((i[2] + "://" + i[0] + ":" + i[1]).lower())

    def collect_proxy(self):
        self.proxy_list.clear()
        for page in self.proxy_pages:
            Logger()("collecting proxy on {}".format(page))
            self.get_proxy_on_single_page(page)

class CollectAliyunProxy(PROXY):
    def __init__(self,count):
        super().__init__()
        self.max_threads=5
        self.target_count=count

    def prepare(self):
        config_instance = Config()
        configs = config_instance.configs
        credentials = configs.get("credentials")
        config = configs.get("config")
        credentials['my_region']='cn-qingdao'
        config['script']=os.path.join(os.getcwd(), "data", "proxy.sh")
        config['count']=self.target_count
        my_aliyun = Aliyun_basic_advanced(credentials.get("my_id"), credentials.get("my_token"),
                                          credentials.get("my_region"))
        my_aliyun.max_threads = self.max_threads
        status, instances_info_list = my_aliyun.create_instances_with_script(**config)
        if status:
            Logger()("success create proxy")
            Logger()(instances_info_list)
            ips = []
            for i in instances_info_list:
                ips.append(r'http://' + i[2] + ':6800')
            self.proxy_list.clear()
            self.proxy_list.extend(ips)
            self.save_proxy()
        else:
            Logger()("fail create proxy")

    def release(self):
        config_instance = Config()
        configs = config_instance.configs
        credentials = configs.get("credentials")
        config = configs.get("config")
        credentials['my_region']='cn-qingdao'
        config['script']=os.path.join(os.getcwd(), "data", "proxy.sh")
        config['count']=0
        my_aliyun = Aliyun_basic_advanced(credentials.get("my_id"), credentials.get("my_token"),
                                          credentials.get("my_region"))
        my_aliyun.max_threads = self.max_threads
        status, instances_info_list = my_aliyun.create_instances_with_script(**config)



