import json

from rpa_common import Env   # 环境配置
from rpa_common.library.Request import Request   # requests请求

env = Env()
request = Request()

class BillRequest():
    def __init__(self):
        super().__init__()
        self.host = env.get()['api']

    def saveOrderList(self, files):
        '''
        @Desc    : 保存pdf账单文件
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = self.host + '/api/index/uploadOss?zsit=debug'
        res = request.reques(method='POST',
                             url=url,
                             headers={},
                             files=files,
                             data={"rename": '1'},
                             timeout=30,
                             status_code=[200]
                             )
        return res