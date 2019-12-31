import ruamel.yaml
from common.logger import Logger

def insert_yaml(ins,path):
    with open(path,"r",encoding="utf-8") as t:
        data=ruamel.yaml.safe_load(t.read())
    if ins in data:
        Logger()("already has {}".format(ins))
    else:
        data[data.index(ins)]=ins

    with open(path,"w",encoding="utf-8") as t:
        ruamel.yaml.dump(data,t,Dumper=ruamel.yaml.RoundTripDumper)


def read_yaml(path):
    with open(path,"r",encoding="utf-8") as t:
        data=ruamel.yaml.safe_load(t.read())
        return data


def save_yaml(data,path):
    with open(path,"w",encoding="utf-8") as t:
        ruamel.yaml.dump(data,t,Dumper=ruamel.yaml.RoundTripDumper)