import urllib.parse
from common.web import WEB,AGENT,PROXY
from common.logger import Logger
from common.decorator import *
import re
from common.baidu import BAIDU
from common.gaode import GAODE
from common.excel_xlsx import write_excel_xlsx_append,generate_excel_file_name,write_excel_xlsx_over_write
import threading,os
from common.yaml_functions import read_yaml,save_yaml

class JOB(WEB):
    def __init__(self,url_parts,keyword,origin):
        super().__init__("")
        self.url_parts=url_parts
        self.keyword=keyword
        self.encoding = "gbk"
        self.agent_instance=AGENT()
        self.proxy_instance = PROXY()
        self.prepare()
        self.max_threads=6
        self.origin=origin
        self.page_url_list=[]
        self.job_items_tuple=[]
        self.job_items_list=[]
        self.prepare_all_page_url()

    def prepare_all_page_url(self):
        self.page_url_list=[self.url_parts[0] + self.keyword + self.url_parts[1] + str(page) + self.url_parts[2]
                    for page in range(1,self.get_page_count()+1)]

    def prepare(self):
        self.header = {'Host': 'search.51job.com', 'Upgrade-Insecure-Requests': '1',
                            'User-Agent': self.agent_instance.get_random_agent()}
        # self.save_excel_raw=generate_excel_file_name("raw")
        self.save_excel_full = generate_excel_file_name("full_"+self.keyword)
        self.load_poi_bd()
        self.load_poi_gd()
        self.load_score()
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()

    def load_poi_gd(self):
        poi_gd = os.path.join(os.getcwd(), "data", "poi_gd")
        if not os.path.exists(poi_gd):
            with open(poi_gd, "w") as f:
                pass
        try:
            self.poi_dict_gd = read_yaml(poi_gd)
        except Exception as e:
            Logger().get_logger().exception(str(e))
        if self.poi_dict_gd is None:
            self.poi_dict_gd = {}

    def load_poi_bd(self):
        poi_bd=os.path.join(os.getcwd(),"data","poi_bd")
        if not os.path.exists(poi_bd):
            with open(poi_bd, "w") as f:
                pass
        try:
            self.poi_dict_bd = read_yaml(poi_bd)
        except Exception as e:
            Logger().get_logger().exception(str(e))
        if self.poi_dict_bd is None:
            self.poi_dict_bd = {}

    def load_score(self):
        score_file=os.path.join(os.getcwd(),"data","score")
        if not os.path.exists(score_file):
            with open(score_file, "w") as f:
                pass
        try:
            self.score_dict = read_yaml(score_file)
        except Exception as e:
            Logger().get_logger().exception(str(e))
        if self.score_dict is None:
            self.score_dict = {}

    def save_poi_bd(self):
        try:
            poi_bd = os.path.join(os.getcwd(), "data", "poi_bd")
            save_yaml(self.poi_dict_bd,poi_bd)
        except Exception as e:
            Logger().get_logger().exception(str(e))

    def save_poi_gd(self):
        try:
            poi_gd = os.path.join(os.getcwd(), "data", "poi_gd")
            save_yaml(self.poi_dict_gd, poi_gd)
        except Exception as e:
            Logger().get_logger().exception(str(e))

    def save_score(self):
        score_file=os.path.join(os.getcwd(),"data","score")
        save_yaml(self.score_dict,score_file)

    def prepare_first_page_url(self):
        return self.url_parts[0] + self.keyword + self.url_parts[1] + str(1) + self.url_parts[2]

    @staticmethod
    def seconds_to_time(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return "{:0>2d}:{:0>2d}:{:0>2d}".format(h, m, s)

    def get_job_count(self):
        self.url=self.prepare_first_page_url()
        reg = re.compile(r'共(.*?)条职位', re.S)
        txt=self.get_txt()
        res = reg.findall(txt)
        if res:
           return int(res[0])

    def get_page_count(self):
        return int(self.get_job_count()/50+1)

    def get_job_info_on_single_page(self):
        reg = re.compile(r'class="t1 ">.*? <a target="_blank" title="(.*?)".*?'
                         r'href="(.*?)".*?'
                         r'<span class="t2"><a target="_blank" title="(.*?)".*?'
                         r'<span class="t3">(.*?)</span>.*?'
                         r'<span class="t4">(.*?)</span>.*?'
                         r'<span class="t5">(.*?)</span>',
                         re.S)  # 匹配换行符
        try:
            items = re.findall(reg, self.get_txt())
        except Exception as e :
           Logger().get_logger().exception(str(e))
           items=None
        return items

    def __get_job(self,page_url):
        self.prepare()
        Logger()("Getting job on {}".format(page_url))
        self.url = page_url
        items = self.get_job_info_on_single_page()
        self.job_items_tuple.extend(items)

    @time_record
    def get_job_info_on_all_page(self):
        start_t_sum = len(threading.enumerate())
        page_url_count=len(self.page_url_list)
        for index,page_url in enumerate(self.page_url_list):
            Logger()("Starting the {} of {} ,left {} items".format(index + 1, page_url_count, page_url_count- index - 1))
            threading.Thread(target=self.__get_job,args=(page_url,)).start()
            while True:
                if len(threading.enumerate()) < start_t_sum + self.max_threads:
                    break
                else:
                    time.sleep(1)
        while True:
            if len(threading.enumerate())<=start_t_sum:
                Logger()("get_job_info_on_all_page finished")
                break
            else:
                Logger()("waitting get_job_info_on_all_page finish")
                time.sleep(1)

    def __add(self,item):
        # add actual location
        actual_location = self.add_actual_location(item[1])
        temp_list = list(item)
        temp_list.append(actual_location)
        # add score
        score = self.add_score(item[2])
        temp_list.append(score)
        # add duration
        if temp_list[6]:
            duration = self.add_duration(temp_list[6])
        else:
            duration = self.add_duration(temp_list[2])
        temp_list.append(duration)
        # add to sum
        self.job_items_list.append(temp_list)

    @time_record
    def add_actual_location_score_duration(self):
        start_t_sum = len(threading.enumerate())
        counter_to_save=100
        items_count=len(self.job_items_tuple)
        self.job_items_list.append(["JobName","URL","Company","district","Salary","Date","DetailAddress","Score","Duration"])
        for index,item in enumerate(self.job_items_tuple):
            Logger()("Starting the {} of {} ,left {} items".format(index+1,items_count,items_count-index-1))
            threading.Thread(target=self.__add,args=(item,)).start()
            counter_to_save=counter_to_save-1
            if counter_to_save==0:
                self.save_poi_bd()
                self.save_poi_gd()
                self.save_score()
                self.save_to_excel_full()
                counter_to_save=100
            while True:
                if len(threading.enumerate()) < start_t_sum + self.max_threads:
                    break
                else:
                    time.sleep(1)
        while True:
            if len(threading.enumerate())<=start_t_sum:
                Logger()("add_actual_location_score_duration finished")
                break
            else:
                Logger()("waitting add_actual_location_score_duration finish")
                time.sleep(1)

    def add_actual_location(self,job_url):
        Logger()("Getting actual loction from {}".format(job_url))
        web_instance=WEB("")
        web_instance.encoding = self.encoding
        web_instance.url = job_url
        web_instance.enable_proxy=self.enable_proxy
        web_instance.header = {'Host': 'search.51job.com', 'Upgrade-Insecure-Requests': '1',
                               'User-Agent': self.agent_instance.get_random_agent()}
        if web_instance.enable_proxy:
            web_instance.proxy=self.proxy_instance.get_random_proxy()
        reg = re.compile(r'<p class="fp">.*?<span class="label">上班地址：</span>(.*?)</p>', re.S)
        try:
            result = reg.findall(web_instance.get_txt())
        except Exception as e:
            Logger().get_logger().exception(str(e))
            result=None
        if result:
            res = re.sub(r'\t*\n*', '', result[0])
        else:
            res = None
        return res

    def add_score(self,company_name):
        Logger()("Getting score of {}".format(company_name))
        score_instance = SCORE("")
        score_instance.proxy_instance=self.proxy_instance
        score_instance.agent_instance=self.agent_instance
        score_instance.enable_proxy=self.enable_proxy
        score_instance.score_dict=self.score_dict
        score_instance.company_name = company_name
        try:
            temp_score = score_instance.get_score()
        except Exception as e:
            Logger().get_logger().exception(str(e))
            temp_score=0
        return temp_score

    def add_duration(self,destination):
        Logger()("Getting duration of {}".format(destination))
        baidu_instance= BAIDU()
        baidu_instance.agent_instance=self.agent_instance
        baidu_instance.proxy_instance=self.proxy_instance
        baidu_instance.poi_dict=self.poi_dict_bd
        baidu_instance.enable_proxy=self.enable_proxy
        baidu_instance.origin = self.origin
        baidu_instance.destination = destination
        try:
            if baidu_instance.prepare_poi():
                res_bd = baidu_instance.get_route()
            else:
                res_bd = (0, 0, 0)
        except Exception as e:
            Logger().get_logger().exception(str(e))
            res_bd=(0,0,0)

        gaode_instance=GAODE()
        gaode_instance.agent_instance=self.agent_instance
        gaode_instance.proxy_instance=self.proxy_instance
        gaode_instance.poi_dict=self.poi_dict_gd
        gaode_instance.enable_proxy=self.enable_proxy
        gaode_instance.origin = self.origin
        gaode_instance.destination = destination
        try:
            if gaode_instance.prepare_poi():
                res_gd = gaode_instance.get_route()
            else:
                res_gd = (0, 0, 0)
        except Exception as e:
            Logger().get_logger().exception(str(e))
            res_gd=(0,0,0)

        if ("fail" in res_gd) and ("fail" in res_bd):
            res = 0
        elif ("fail" in res_gd) and ("fail" not in res_bd):
            res = res_bd[2]
        elif ("fail" not in res_gd) and ("fail" in res_bd):
            res = res_gd[2]
        elif ("fail" not in res_gd) and ("fail" not in res_bd):
            duraton_bd=int(res_bd[2])
            duration_gd=int(res_gd[2])
            res = min(duraton_bd, duration_gd)
        else:
            res=0
        return self.seconds_to_time(res)

    def save_to_excel_raw(self):
        write_excel_xlsx_append(self.save_excel_raw,self.job_items_tuple)

    def save_to_excel_full(self):
        write_excel_xlsx_over_write(self.save_excel_full,self.job_items_list)

class SCORE(WEB):
    def __init__(self,company_name=""):
        super().__init__("")
        self.company_name=company_name
        self.agent_instance = ""
        self.proxy_instance = ""
        self.encoding = "gbk"
        self.score_dict={}
        # self.load_score()

    def encode_str(self,strs):
        return urllib.parse.quote_plus(strs)

    def prepare(self):
        self.agent_instance = AGENT()
        self.proxy_instance = PROXY()

    def load_score(self):
        score_file=os.path.join(os.getcwd(),"data","score")
        if not os.path.exists(score_file):
            with open(score_file, "w") as f:
                pass
        try:
            self.score_dict = read_yaml(score_file)
        except Exception as e:
            Logger().get_logger().exception(str(e))

        if self.score_dict is None:
            self.score_dict = {}

    def insert_score(self,company_name,scores):
        if not company_name in self.score_dict:
            Logger()("add {} score data to {}".format(self.company_name, "score file"))
            self.score_dict[company_name]=scores
            # self.save_score()

    def save_score(self):
        score_file=os.path.join(os.getcwd(),"data","score")
        save_yaml(self.score_dict,score_file)

    def get_score(self):
        if self.company_name in self.score_dict:
            Logger()("find {} score data in {}".format(self.company_name, "score file"))
            return self.score_dict.get(self.company_name)
        self.url = "https://www.kanzhun.com/companyl/search/?stype=&q=" + self.encode_str(self.company_name)
        self.header= {"Host": "www.kanzhun.com", "Upgrade-Insecure-Requests": "1",
                            'User-Agent': self.agent_instance.get_random_agent()}
        if self.enable_proxy:
            self.proxy=self.proxy_instance.get_random_proxy()

        reg = re.compile(r'<ul class="company_result ">.*?</ul>', re.S)
        txt=self.get_txt()
        temp = reg.findall(txt)
        if temp:
            result = re.findall(r'title=".*?".*?</i></span>(.*?)\n</dd>', temp[0], re.S)
        else:
            return 0
        for j in result[:]:
            if not re.match(r"\d", j):
                result.pop(result.index(j))
        result_list = list(map(float, result))
        if result_list:
            average_score = sum(result_list) / len(result_list)
            self.insert_score(self.company_name,average_score)
            return average_score
        else:
            return 0

if __name__ == '__main__':
    pass

