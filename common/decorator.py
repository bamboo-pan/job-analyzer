import time
from common.logger import Logger
from functools import wraps

class class_time_record():
    def __init__(self,f):
        self.f=f
        self.complex_logger=Logger().get_logger()
        self.simple_logger=Logger()

    def __call__(self, *args, **kwargs):
        start=time.time()
        result=self.f(*args,**kwargs)
        end=time.time()
        cost=end-start
        self.simple_logger("Function:"+self.f.__name__+' Cost:'+str(cost))
        return result

def time_record(f):
    # functools.wraps，wraps本身也是一个装饰器，它能把原函数的元信息拷贝到装饰器里面的函数
    # python 3.7貌似已经不需要这个函数，函数的属性会自动保留了
    @wraps(f)
    def wrapper(*args,**kwargs):
        start=time.time()
        result=f(*args,**kwargs)
        end=time.time()
        cost = end - start
        Logger()("Function:"+f.__name__+' Cost:'+str(cost))
        return result
    return wrapper

"""
class 装饰器要在函数装饰器后面
"""
@class_time_record
@time_record
def test(t):
    time.sleep(t)
    return 1

if __name__ == '__main__':
    print(test(2))