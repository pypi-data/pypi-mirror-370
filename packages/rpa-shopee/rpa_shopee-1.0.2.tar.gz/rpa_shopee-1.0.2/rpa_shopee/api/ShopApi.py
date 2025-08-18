import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Union, Dict, Literal, List
from undetected_chromedriver import Chrome as unChrome

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common import Common   # 公共库
from rpa_common import Env   # 环境配置
from rpa_common.library.Request import Request   # requests请求
from rpa_common.service.ExecuteService import ExecuteService  # 请求
from rpa_common.exceptions import *

env = Env()
request = Request()
common = Common()
executeService = ExecuteService()

class ShopApi():
    def __init__(self):
        super().__init__()
        self.host = env.get()['api']

    def getInfoAccountList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前店铺账号信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_session/"
        res = executeService.request(driver=driver, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取当前店铺账号信息', res)
        return res

    def getShopOrHaveHoliday(self, driver: unChrome, options: dict, map_url='shopee.cn'):
        '''
        @Desc    : 获取当前店铺是否已休假（本土、非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        休假状态的店铺无法获取 广告费和充值记录
        '''
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        url = f"https://seller.{map_url}/api/selleraccount/user_info/"
        res = executeService.request(driver=driver, params=params, url=url, method="GET")
        res = json.loads(res)
        holiday_mode_on: bool = res['data']['holiday_mode_on']
        common.print_('获取当前店铺是否已休假', res)
        # Ture 已休假  False 未休假
        return holiday_mode_on

    def getInfoList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前店铺信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        url = f"https://seller.shopee.cn/api/cnsc/selleraccount/get_or_set_shop/"
        res = executeService.request(driver=driver, url=url, params=params, data={}, method="POST")
        res = json.loads(res)
        common.print_('获取当前店铺信息', res)
        return res

    def queryShopExistCurrentCompany(self, driver: unChrome, options: dict) -> Union[bool, str]:
        '''
        @Desc    : 查询当前 shop_id 是否存在于当前公司（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_or_set_shop/"
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2"
        }
        data = {
            "cnsc_shop_id": int(options['shop_id'])
        }
        res = executeService.request(driver=driver, params=params, url=url, data=data, method="POST")
        res = json.loads(res)
        common.print_('查询当前 shop_id 是否存在于当前公司', res)
        debug_msg = True  # 此 shop_id 存在与当前公司
        if res.get('code') != 0:
            debug_msg = res.get('err_detail') or res.get('debug_message') or '[查询失败]查询当前 shop_id 是否存在于当前公司（非本土）'
        return debug_msg

    def getAllShopList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取当前公司所有店铺信息（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_merchant_shop_list/"
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2",
            "page_index": "1",
            "page_size": "50",
            "auth_codes": "\\[\"access_my_income\"\\]",
            "feature_keys": "\\[\\]",
            "show_tags": "\\[\\]"
        }
        res = executeService.request(driver=driver, headers=self._headers, params=params, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取当前公司所有店铺信息', res)
        return res

    def getMerchantList(self, driver: unChrome, options: dict) -> dict:
        '''
        @Desc    : 获取所有公司信息merchant_id（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        params = {
            "SPC_CDS": "--",
            "SPC_CDS_VER": "2",
            "page_index": "1",
            "page_size": "500",
            "merchant_name": ""
        }
        url = "https://seller.shopee.cn/api/cnsc/selleraccount/get_merchant_list/"
        res = executeService.request(driver=driver, params=params, headers=self._headers, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取所有公司信息merchant_id', res)
        return res

    def switch_store(self, driver: unChrome, options) -> dict:
        """
        @Desc     : shopee切换商家（非本土）
        @Author   : 祁国庆
        @Time     : 2025/05/26 10:51:43
        @Params   :
            - merchant_id: 公司id (非shop_id)
            - shop_id: 店铺id (shop_id)
        @Returns  : 正常返回字典数据，也会返回当前店铺商家的信息
        """
        # 账号-》公司-》店铺    三层
        print(f"——————————————————【shopee切换公司和店铺】{options}")
        merchant_id = str(options.get('merchant_id'))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id'))  # 店铺id
        site = str(options.get('site'))
        if not all(v is not None and v != '' for v in
                   [merchant_id, shop_id, site]):
            raise TaskParamsException("缺少必要参数 merchant_id, shop_id, site")

        # 获取获取当前店铺信息
        at_shop_data: dict = self.getInfoList(driver=driver, options=options)
        if at_shop_data.get('code') != 0:
            raise UnknownException(f"当前店铺商家信息-请求失败")
        # ——————将当前店铺数据和所有店铺数据打包进行返回
        shop_all = {'at': at_shop_data}
        if merchant_id == str(at_shop_data['merchant_id']) and shop_id == str(at_shop_data['shop_id']):
            return {"status": 1, "message": "无需切换", 'data': shop_all}

        # 公司id 一致则无需切换公司 直接切换店铺即可
        if merchant_id != str(at_shop_data.get('merchant_id')):
            # ——————————————————发起请求，获取新公司的cookie信息，即可自动切换页面
            data = {
                "merchant_id": int(merchant_id)
            }
            headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json;charset=UTF-8"
              }
            url = f"https://seller.shopee.cn/api/cnsc/selleraccount/switch_merchant/?SPC_CDS=--&SPC_CDS_VER=2&cnsc_shop_id={shop_id}&cbsc_shop_region={site.lower()}"
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            res = json.loads(res)
            common.print_('获取新公司的cookie信息-请求', res)
            if res.get('code') != 0:
                raise UnknownException(f"获取新公司的cookie信息-请求失败")
        # 查询 shop_id 是否存在于当前公司内
        queryShopExistCurrentCompany = self.queryShopExistCurrentCompany(driver=driver, options=options)
        if queryShopExistCurrentCompany != True:
            raise UnknownException(queryShopExistCurrentCompany)

        driver.get(f'https://seller.shopee.cn/?cnsc_shop_id={shop_id}')
        time.sleep(8)
        _ = self.switch_store(driver, options)
        _['message'] = '切换完成'
        return _

    def getNativeInfoList(self, driver: unChrome, options):
        '''
        @Desc    : 获取当前账号信息（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        成功：{'cs_token': '', 'email': 'se*****@outlook.com', 'errcode': 0, 'id': 986403319, 'language': 'en', 'phone': '*****82', 'portrait': '6c37336ba3b698a0eb0647decfe5b6c2', 'shop_name': '', 'shopid': 986247875, 'sso': '', 'sso_v2': '', 'sub_account_token': None, 'subaccount_id': None, 'token': '', 'username': '00lqjz73_c'}
        错误：{"errcode":1,"fields":null}
        '''
        map_url = self.map_url['HOST'].get(options['site'])
        url = f"https://seller.{map_url}/api/v2/login/"
        res = executeService.request(driver=driver, headers=self._headers, url=url, method="GET")
        res = json.loads(res)
        common.print_('获取当前账号信息', res)
        return res

    @property
    def _headers(self):
        return {
            "accept": "application/json, text/plain, */*",
        }

    @property
    def map_url(self):
        map_url = {
            'HOST': {
                'SG': "shopee.sg",
                'TW': "shopee.tw",
                'MY': "shopee.com.my",
                'PH': "shopee.ph",
                'TH': "shopee.co.th",
                'ID': "shopee.co.id",
                'VN': "shopee.vn",
                'BR': "shopee.com.br",
                'MX': "shopee.com.mx",
                'CO': "shopee.com.co",
                'CL': "shopee.cl",
                'AR': "shopee.com.ar",
                'FR': "shopee.fr",
                'PL': "shopee.pl",
                'ES': "shopee.es",
                'IN': "shopee.in"
            }
        }
        return map_url

    @property
    def currency(self):
        '''货币'''
        return {
            'SG': "SGD",
            'ID': "IDR",
            'MY': "MYR",
            'PH': "PHP",
            'TW': "TWD",
            'TH': "THB",
            'VN': "VND",
            'IR': "IRR",
            'MM': "MMK",
            'HK': "HKD",
            'BR': "BRL",
            'CN': "CNY",
            'MX': "MXN",
            'CO': "COP",
            'CL': "CLP",
            'AR': "ARS",
            'PL': "PLN",
            'IN': "INR",
            'US': "USD",
            'KR': "KRW",
            'JP': "JPY"
        }

    def TaskParamsException(self, name, *args):
        '''任务参数异常'''
        common.print_('开始参数检测|TaskParamsException', name)
        if not all(v is not None and str(v) != '' for v in args):
            raise TaskParamsException(f'缺少运行参数 - {name}')