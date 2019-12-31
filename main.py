from common.job import JOB,SCORE
from common.baidu import BAIDU
from common.gaode import GAODE
from common.mail import send_mail_163
import os
from common.excel_xlsx import set_hyperlink_column,set_columon_width_auto
from common.web import CollectAliyunProxy
from common.yaml_functions import save_yaml


def test():
    baidu=BAIDU()
    baidu.origin="青浦新城地铁站"
    baidu.destination="金科路地铁站"
    baidu.prepare_poi()
    a=baidu.get_route()

    gaode=GAODE()
    gaode.origin="青浦新城地铁站"
    gaode.destination="金科路地铁站"
    gaode.prepare_poi()
    b=gaode.get_route()


def read_config():
    configs={}
    lf=os.path.join(os.getcwd(),"config.txt")
    if os.path.exists(lf):
        with open(lf,"r",encoding="utf-8") as f:
            a=f.read().split('\n')
            configs["keyword"]=a[0].split(":")[1].split(",")
            if a[1].split(":")[1]=="True":
                configs["enable_proxy"]=True
            else:
                configs["enable_proxy"] = False
    return configs

def run():
    try:
        configs=read_config()
    except Exception as e:
        configs={}
    if not configs:
        return
    enable_proxy=configs.get("enable_proxy")
    my_keyword = configs.get("keyword")
    if enable_proxy:
        collect_aliyun=CollectAliyunProxy(10)
        collect_aliyun.max_threads=5
        collect_aliyun.prepare()
    for keyword in my_keyword:
        my_url_parts = ["https://search.51job.com/list/020000,020000,0000,00,1,08%252C09,",
                        ",2,",
                        ".html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=04&jobterm=99&companysize="
                        "02%2C03%2C04%2C05%2C06&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=17&dibiaoid=0&"
                        "address=&line=&specialarea=00&from=&welfare="]

        origin="青浦新城地铁站"
        job_python=JOB(my_url_parts,keyword,origin)
        job_python.max_threads=10
        job_python.enable_proxy=enable_proxy
        job_python.get_job_info_on_all_page()
        job_python.add_actual_location_score_duration()
        job_python.save_poi_bd()
        job_python.save_poi_gd()
        job_python.save_score()
        job_python.save_to_excel_full()
        set_hyperlink_column(job_python.save_excel_full, 2)
        # set_columon_width_auto(job_python.save_excel_full)
        send_mail_163("finished:{}".format(keyword),"finished:{}".format(keyword),job_python.save_excel_full)
    if enable_proxy:
        collect_aliyun.release()
        print()

if __name__ == '__main__':
    run()


