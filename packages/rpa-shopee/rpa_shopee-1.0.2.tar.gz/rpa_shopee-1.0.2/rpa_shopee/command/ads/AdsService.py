import json
from undetected_chromedriver import Chrome as unChrome

from rpa_common import Common   # 公共库
from rpa_common.request import ShopRequest   # 店铺信息获取并操作
from rpa_common.request.TaskRequest import TaskRequest  # 任务数据保存

from rpa_shopee.api.AdvertisementBillApi import AdvertisementBillApi    # shopee ads广告类接口

common = Common()
advertisementBillApi = AdvertisementBillApi()
shopRequest = ShopRequest()
taskRequest = TaskRequest()

class AdsService():
    def __init__(self):
        super().__init__()

    def getNoNativeAdsBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告费（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee广告费（非本土）
        advertisementBillApi.getNoNativeAdsBill(driver, shop_data, options)

    def getNativeAdsBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告费（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee广告费（本土）
        advertisementBillApi.getNativeAdsBill(driver, shop_data, options)

    def getNoNativeAdsRechargeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告充值记录账单（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee广告充值记录账单（非本土）
        advertisementBillApi.getNoNativeAdsRechargeBill(driver, shop_data, options)

    def getNativeAdsRechargeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee广告充值记录账单（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('options', options)
        print('shop_data', shop_data)

        # 获取shopee广告充值记录账单（本土）
        advertisementBillApi.getNativeAdsRechargeBill(driver, shop_data, options)