import json
from undetected_chromedriver import Chrome as unChrome

from rpa_common import Common   # 公共库
from rpa_common.request import ShopRequest   # 店铺信息获取并操作
from rpa_common.request.TaskRequest import TaskRequest  # 任务数据保存

from rpa_shopee.api.BillApi import BillApi     # shopee 账单类接口

common = Common()
billApi = BillApi()
shopRequest = ShopRequest()
taskRequest = TaskRequest()


class BillService():
    def __init__(self):
        super().__init__()

    def getNoNativeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单（非本土）
        billApi.getNoNativeBill(driver, shop_data, options)

    def getNativeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单（本土）
        billApi.getNativeBill(driver, shop_data, options)

    def getNoNativeBillDetails(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单详情（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单详情（非本土）
        billApi.getNoNativeBillDetails(driver, shop_data, options)

    def getNativeBillDetails(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单详情（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单详情（本土）
        billApi.getNativeBillDetails(driver, shop_data, options)

    def getNoNativeBillTime(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单时间（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单时间（非本土）
        billApi.getNoNativeBillTime(driver, shop_data, options)

    def getNativeBillTime(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee账单时间（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee账单时间（本土）
        billApi.getNativeBillTime(driver, shop_data, options)

    def getNoNativeBillPdf(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee进账报表pdf并上传（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee进账报表pdf并上传（非本土）
        billApi.getNoNativeBillPdf(driver, shop_data, options)

    def getNativeBillPdf(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee进账报表pdf并上传（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee进账报表pdf并上传（本土）
        billApi.getNativeBillPdf(driver, shop_data, options)

    def getNoNativeShopAmount(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : shopee资金申报（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee资金申报（非本土）
        billApi.getNoNativeShopAmount(driver, shop_data, options)

    def getNativeShopAmount(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : shopee资金申报（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee资金申报（本土）
        billApi.getNativeShopAmount(driver, shop_data, options)