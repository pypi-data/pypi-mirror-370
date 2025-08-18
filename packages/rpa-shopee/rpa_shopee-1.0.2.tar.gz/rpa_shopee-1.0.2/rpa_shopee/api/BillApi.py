import json
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse
from io import StringIO, BytesIO
import zipfile
import uuid
from undetected_chromedriver import Chrome as unChrome

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common import Common   # 公共库
from rpa_common import Env   # 环境配置
from rpa_common.library.Request import Request   # requests请求
from rpa_common.request import ShopRequest   # 店铺信息获取并操作
from rpa_common.service.ExecuteService import ExecuteService  # 请求
from rpa_common.exceptions import *
from rpa_common.request.TaskRequest import TaskRequest  # 任务数据保存

from rpa_shopee.api.ShopApi import ShopApi   # shopee店铺信息获取
from rpa_shopee.request.BillRequest import BillRequest  # 保存上传账单pdf功能

env = Env()
request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()
shopRequest = ShopRequest()
shopApi = ShopApi()
billRequest = BillRequest()

class BillApi():
    def __init__(self):
        super().__init__()
        self.host = env.get()['api']

    def getNoNativeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单 非本土】')
        print('options', options)
        start_time = options.get('start_time', '')  # 开始时间 格式 2025-04-03
        end_time = options.get('end_time', '')  # 结束时间  格式 2025-04-03
        merchant_id = str(shop_data.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        if not start_time:
            start_time = '2025-06-01'
            end_time = '2025-06-29'

        # 参数检测
        shopApi.TaskParamsException('非本土获取账单', start_time, end_time, merchant_id, shop_id)

        shop_at = None
        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver=driver, options=options)
            common.print_('shop_at', shop_at)

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        # ————————————请求获取所有账单的 payout_id
        data_payout_id = None
        if shop_at:
            params = {
                "SPC_CDS": "--",
                "SPC_CDS_VER": "2",
                "cnsc_shop_id": str(shop_at['data']['at']['shop_id']),
                "cbsc_shop_region": ""
            }
            common.print_('params', params)
            url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_overview/get_available_payout_detail_list"
            res = executeService.request(driver=driver, headers=headers, url=url, params=params, method="GET")
            res = json.loads(res)
            common.print_('payout_id-请求返回信息', res)
            # 提取出 payout_id
            data_payout_id = res.get('data', {}).get('list', [])
            if not data_payout_id:
                return common.back(status=1, message='账单数据为空')

        # 50个账单起步
        data = {
            "source_type": 0,
            "income_category": 2,
            "pagination_info": {
                "limit": 50,
                "direction": 0
            }
        }
        if not shop_at:
            raise UnknownException('中国商家店铺获取账单payout_id出错，无法继续')
        # 转换为 10 位时间戳
        timestamp = common.lambda_set()['date_to_timestamp']

        # 提取 payout_id
        data['cb_query_condition'] = {
             "payout_ids": sum([[r['payout_id'] for r in _['payout_records']]
                                for _ in data_payout_id
                                if timestamp(start_time) <= timestamp(_['payout_date']) <= timestamp(end_time) and _.get('payout_records')], [])
        }
        if not data['cb_query_condition']['payout_ids']:
            return common.back(status=1, message='账单数据为空')
        page_number = 1
        while True:
            common.print_('页面请求开始', data)
            # ——————————【使用默认的请求获取账户数据】，如果返回了next_page信息，说明还有下一页，反之则无
            url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_overview/get_income_detail"
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            bill = json.loads(res)
            common.print_('获取账单', bill)
            list_count = bill.get('data', {}).get('list', [])
            if len(bill.get('data', {}).get('list', [])) == 0:
                return common.back(status=1, message='没有数据')

            request_id = str(uuid.uuid4())

            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = page_number   # 页码
            options['page_size'] = data['pagination_info']['limit']   # 每页数量
            options['list_count'] = len(list_count)  # 当前数据列表数据长度
            options['total_count'] = 0    # 总数据量
            options['response'] = res
            taskRequest.save(options)

            # 继续请求
            next_page = bill.get('data', {}).get('next_page', {})
            # 如果没有翻页，则直接停止即可
            if next_page:
                data['pagination_info'] = next_page
                page_number += 1
            else:
                break

            time.sleep(random.uniform(1, 3))

    def getNativeBill(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单 本土】')
        print('options', options)
        start_time = options.get('start_time', '')  # 开始时间 格式 2025-04-03
        end_time = options.get('end_time', '')      # 结束时间  格式 2025-04-03
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        site = options.get("site").upper()

        if not start_time:
            start_time = '2025-06-01'
            end_time = '2025-06-29'

        # 参数检测
        shopApi.TaskParamsException('本土获取账单', start_time, end_time, shop_id, site)

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'本土获取账单 - 未匹配到该站点url {site}')

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        data = {
            "source_type": 0,
            "income_category": 2,
            "pagination_info": {
                "limit": 50,
                "direction": 0
            },
            "local_query_condition": {
                "start_date": start_time,
                "end_date": end_time
            }
        }
        page_number = 1
        while True:
            common.print_('页面请求开始|data', data)
            # ——————————【使用默认的请求获取账户数据】，如果返回了next_page信息，说明还有下一页，反之则无
            url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_overview/get_income_detail"
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            bill = json.loads(res)
            common.print_('获取账单|正文', bill)
            list_count = bill.get('data', {}).get('list', [])
            if len(bill.get('data', {}).get('list', [])) == 0:
                return common.back(status=1, message='没有数据')

            request_id = str(uuid.uuid4())

            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = page_number  # 页码
            options['page_size'] = data['pagination_info']['limit']  # 每页数量
            options['list_count'] = len(list_count)  # 当前数据列表数据长度
            options['total_count'] = 0  # 总数据量
            options['response'] = res
            taskRequest.save(options)

            # 继续请求
            next_page = bill.get('data', {}).get('next_page', {})
            # 如果没有翻页，则直接停止即可
            if next_page:
                data['pagination_info'] = next_page
                page_number += 1
            else:
                break

            time.sleep(random.uniform(1, 3))

    def getNoNativeBillDetails(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单详情（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单详情 非本土】')
        print('options', options)
        order_id_list = options.get('order_id_list')
        merchant_id = str(shop_data.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        # 参数检测
        shopApi.TaskParamsException('非本土获取账单详情', order_id_list, merchant_id, shop_id)

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver=driver, options=options)
            common.print_('shop_at', shop_at)

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        for order_id in order_id_list:
            data = {
                "order_id": int(order_id),
                "components": [2, 3, 4]
            }
            url = f'https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_detail/get_order_income_components'
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            bill = json.loads(res)
            common.print_(f'获取账单详情|{order_id}', bill)
            if not bill: raise UnknownException('获取账单详情失败')

            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = res
            taskRequest.save(options)

            time.sleep(random.uniform(1, 3))

    def getNativeBillDetails(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单详情（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单详情 本土】')
        print('options', options)
        order_id_list = options.get('order_id_list')
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        site = options.get("site").upper()

        # 参数检测
        shopApi.TaskParamsException('本土获取账单详情', order_id_list, shop_id, site)

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'本土获取账单详情 - 未匹配到该站点url {site}')

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        for order_id in order_id_list:
            data = {
                "order_id": int(order_id),
                "components": [2, 3, 4]
            }
            url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_detail/get_order_income_components"
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            bill = json.loads(res)
            common.print_(f'获取账单详情|{order_id}', bill)
            if not bill: raise UnknownException('获取账单详情失败')

            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = res
            taskRequest.save(options)

            time.sleep(random.uniform(1, 3))

    def getNoNativeBillTime(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单详细日期（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单详细日期 非本土】')
        print('options', options)
        order_id_list = options.get('order_id_list')
        merchant_id = str(shop_data.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        # 参数检测
        shopApi.TaskParamsException('非本土获取账单详细日期', order_id_list, merchant_id, shop_id)

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver=driver, options=options)
            common.print_('shop_at', shop_at)

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        for order_id in order_id_list:
            url = f"https://seller.shopee.cn/api/v3/order/get_one_order?order_id={order_id}"
            res = executeService.request(driver=driver, headers=headers, url=url, method="GET")
            bill = json.loads(res)
            common.print_(f'获取账单详细日期|{order_id}', bill)
            if not bill: raise UnknownException('获取账单详细日期失败')

            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = res
            taskRequest.save(options)

            time.sleep(random.uniform(1, 3))

    def getNativeBillTime(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取账单详细日期（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取账单详细日期 本土】')
        print('options', options)
        order_id_list = options.get('order_id_list')
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        site = options.get("site").upper()

        # 参数检测
        shopApi.TaskParamsException('本土获取账单详细日期', order_id_list, shop_id, site)

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'本土获取账单详细日期 - 未匹配到该站点url {site}')

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        for order_id in order_id_list:
            url = f"https://seller.{map_url}/api/v3/order/get_one_order?order_id={order_id}"
            res = executeService.request(driver=driver, headers=headers, url=url, method="GET")
            bill = json.loads(res)
            common.print_(f'获取账单详细日期|{order_id}', bill)
            if not bill: raise UnknownException('获取账单详细日期失败')

            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = res
            taskRequest.save(options)

            time.sleep(random.uniform(1, 3))

    def getNoNativeBillPdf(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取进账报表pdf并上传（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取进账报表pdf并上传 非本土】')
        print('options', options)
        start_time = options.get('start_time', '')  # 开始时间 格式 2025-04-03
        end_time = options.get('end_time', '')  # 结束时间  格式 2025-04-03
        site = options.get('site', '').upper()
        merchant_id = str(shop_data.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        if not start_time:
            start_time = '2025-06-01'
            end_time = '2025-06-29'

        # 参数检测
        shopApi.TaskParamsException('非本土获取进账报表pdf并上传', site, start_time, end_time, merchant_id, shop_id)

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver=driver, options=options)
            common.print_('shop_at', shop_at)

        # 检测是否有报表
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        # 转换为 10 位时间戳
        timestamp = common.lambda_set()['date_to_timestamp_fill']

        data = {
            "statement_type": "fixed_date",
            "start_time": timestamp(start_time, 1, 0),
            "end_time": timestamp(end_time, 1, 86399),
            "pagination_info": {
                "direction": 0,
                "limit": 50
            }
        }
        url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_statement/get_generatable_income_statements"
        pdf_data_map = {}
        while True:
            # 获取所有报表的文件名称和文件的起始和结束时间
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            pdf_bill = json.loads(res)
            common.print_('获取进账报表pdf账单', pdf_bill)
            filename_data = pdf_bill.get('data', {}).get('list', [])
            for file in filename_data:
                pdf_data_map[file['filename']] = file
            next_page = pdf_bill.get('data', {}).get('next_page', {})
            if not next_page:  # 没有下一页
                break
            # 继续下一页
            data['pagination_info'] = next_page
            time.sleep(random.uniform(1, 3))

        if not pdf_data_map:
            return common.back(status=1, message='没有进账报表pdf账单可以下载')

        # 生成下载pdf的id
        url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_statement/request_income_statement_batch_generate"
        data = {
            "statement_type": "fixed_date",
            "start_time": start_time.replace('-', ''),  # 20250601
            "end_time": end_time.replace('-', '')  # 20250620
        }
        # 生成下载pdf的id
        res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
        pdf_bill_id = json.loads(res)
        document_id = pdf_bill_id.get('document_id')
        common.print_('生成下载pdf的id', document_id)

        # 持续检测报表状态【如果报表只有一个，则下载的是pdf,如果有多个，则是zip压缩包】
        url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_statement/get_generated_income_statements_by_ids"
        data = {"document_ids": [document_id] }
        pdf_file_name = ''   # 文件名称 （检测一下是pdf还是zip压缩包）
        i = 1
        time_start = int(time.time())
        # 循环监测pdf是否已经整理完成，是否可以开始下载 固定时间监测 5分钟
        while int(time.time()) - time_start < 5 * 60:
            # 下载表格
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            pdf_res = json.loads(res)
            pdf_res = pdf_res.get('list', [])
            common.print_(f'[{i}][↓{5 * 60 - (int(time.time()) - time_start)}s]当前状态信息', res)
            # 处理完成，可以下载表格了   1：处理中   2：可以下载
            if pdf_res[0].get('status') == 2:
                pdf_file_name = pdf_res[0].get('file_name')
                break
            time.sleep(random.uniform(3, 5))
            i += 1

        # 获取cookie
        SPC_CNSC_SESSION = common.getCookie(driver, 'SPC_CNSC_SESSION')
        common.print_('获取的cookie-SPC_CNSC_SESSION', SPC_CNSC_SESSION)
        if not SPC_CNSC_SESSION:
            raise UnknownException('SPC_CNSC_SESSION cookie获取失败，无法下载pdf报表')

        # 开始下载pdf或zip压缩包
        headers = {
            "accept": "*/*",
            "accept-language": "zh-HK,zh-TW;q=0.9,zh;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_statement/download_income_statement_file"
        params = {"document_id": document_id}
        # 结果
        pdf_data_list = []
        response_table = request.reques(method='GET',
                                        url=url,
                                        headers=headers,
                                        cookies={"SPC_CNSC_SESSION": SPC_CNSC_SESSION},
                                        params=params,
                                        timeout=30)
        if '.zip' in pdf_file_name:
            common.print_('zip压缩包名称', pdf_file_name)
            # 使用 BytesIO 读取 response.content（模拟文件）
            with zipfile.ZipFile(BytesIO(response_table.content)) as zip_file:
                # 遍历 ZIP 文件中的所有文件
                for file_name in zip_file.namelist():
                    common.print_('遍历|zip压缩包内pdf文件', file_name)
                    # 检查是否是 pdf 文件（不区分大小写）
                    if file_name.lower().endswith('.pdf'):
                        # ————————————-上传服务器
                        # 读取 pdf 文件内容（bytes） 然后上传到服务器
                        files = {"file": (file_name, zip_file.read(file_name), "application/pdf")}
                        # {'status': 1, 'message': '上传成功', 'data': '/uploads/task/002ec6e26ee6c59f285e20b978c409e2.pdf', 'code': 1}
                        response_server = billRequest.saveOrderList(files=files)
                        response_server = response_server.json()
                        common.print_('response_server', response_server)
                        pdf_data_list += [{
                            'url': response_server['data'],
                            'site': site,
                            **pdf_data_map[file_name]
                        }]
                    else:
                        raise UnknownException('[shopee pdf下载]zip压缩包内的数据不是pdf文件，错误！！！')
        elif '.pdf' in pdf_file_name:
            common.print_('pdf名称', pdf_file_name)
            # ————————————-上传服务器
            files = {"file": (pdf_file_name, BytesIO(response_table.content), "application/pdf")}
            # {'status': 1, 'message': '上传成功', 'data': '/uploads/task/002ec6e26ee6c59f285e20b978c409e2.pdf', 'code': 1}
            response_server = billRequest.saveOrderList(files=files)
            response_server = response_server.json()
            common.print_('response_server', response_server)
            pdf_data_list += [{
                'url': response_server['data'],
                'site': site,
                **pdf_data_map[pdf_file_name]
            }]
        else:
            raise UnknownException('[shopee pdf下载]未知的文件格式，错误！！！')
        common.print_('pdf_data_list', pdf_data_list)

        if pdf_data_list:
            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = json.dumps(pdf_data_list, ensure_ascii=False, separators=(',', ':'))
            taskRequest.save(options)

    def getNativeBillPdf(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取进账报表pdf并上传（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取进账报表pdf并上传 本土】')
        print('options', options)
        start_time = options.get('start_time', '')  # 开始时间 格式 2025-04-03
        end_time = options.get('end_time', '')  # 结束时间  格式 2025-04-03
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        site = options.get("site").upper()

        if not start_time:
            start_time = '2025-06-01'
            end_time = '2025-06-29'

        # 参数检测
        shopApi.TaskParamsException('本土获取进账报表pdf并上传', start_time, end_time, shop_id, site)

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'本土获取进账报表pdf并上传 - 未匹配到该站点url {site}')

        # 检测是否有报表
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        # 转换为 10 位时间戳
        timestamp = common.lambda_set()['date_to_timestamp_fill']

        data = {
            "statement_type": "week",
            "start_time": timestamp(start_time, 1, 3600), # 01:00:00
            "end_time": timestamp(end_time, 1, 89999),  # 多一天 00:59:59
            "pagination_info": {
                "direction": 0,
                "limit": 50
            }
        }
        url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_statement/get_generatable_income_statements"
        pdf_data_map = {}
        while True:
            # 获取所有报表的文件名称和文件的起始和结束时间
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            pdf_bill = json.loads(res)
            common.print_('获取进账报表pdf账单', pdf_bill)
            filename_data = pdf_bill.get('data', {}).get('list', [])
            for file in filename_data:
                pdf_data_map[file['filename']] = file
            next_page = pdf_bill.get('data', {}).get('next_page', {})
            if not next_page:  # 没有下一页
                break
            # 继续下一页
            data['pagination_info'] = next_page
            time.sleep(random.uniform(1, 3))

        if not pdf_data_map:
            return common.back(status=1, message='没有进账报表pdf账单可以下载')

        # 生成下载pdf的id
        url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_statement/request_income_statement_batch_generate"
        data = {
            "statement_type": "week",
            "start_time": start_time.replace('-', ''),  # 20250601
            "end_time": end_time.replace('-', '')  # 20250620
        }
        # 生成下载pdf的id
        res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
        pdf_bill_id = json.loads(res)
        document_id = pdf_bill_id.get('document_id')
        common.print_('生成下载pdf的id', document_id)

        # 持续检测报表状态【如果报表只有一个，则下载的是pdf,如果有多个，则是zip压缩包】
        url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_statement/get_generated_income_statements_by_ids"
        data = {"document_ids": [document_id] }
        pdf_file_name = ''   # 文件名称 （检测一下是pdf还是zip压缩包）
        i = 1
        time_start = int(time.time())
        # 循环监测pdf是否已经整理完成，是否可以开始下载 固定时间监测 5分钟
        while int(time.time()) - time_start < 5 * 60:
            # 下载表格
            res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
            pdf_res = json.loads(res)
            pdf_res = pdf_res.get('list', [])
            common.print_(f'[{i}][↓{5 * 60 - (int(time.time()) - time_start)}s]当前状态信息', res)
            # 处理完成，可以下载表格了   1：处理中   2：可以下载
            if pdf_res[0].get('status') == 2:
                common.print_('pdf_res', pdf_res)
                pdf_file_name = pdf_res[0].get('file_name')
                break
            time.sleep(random.uniform(3, 5))
            i += 1

        # 获取cookie
        SPC_SC_SESSION = common.getCookie(driver, 'SPC_SC_SESSION')
        SPC_EC = common.getCookie(driver, 'SPC_EC')
        common.print_('获取的cookie|SPC_SC_SESSION|SPC_EC', SPC_SC_SESSION, SPC_EC)
        if not (SPC_SC_SESSION and SPC_EC):
            raise UnknownException('SPC_SC_SESSION|SPC_EC cookie获取失败，无法下载pdf报表')

        # 开始下载pdf或zip压缩包
        headers = {
            "accept": "*/*",
            "accept-language": "zh-HK,zh-TW;q=0.9,zh;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_statement/download_income_statement_file"
        params = {"document_id": document_id}
        # 结果
        pdf_data_list = []
        response_table = request.reques(method='GET',
                                        url=url,
                                        headers=headers,
                                        cookies={"SPC_SC_SESSION": SPC_SC_SESSION,"SPC_EC": SPC_EC},
                                        params=params,
                                        timeout=30)
        if '.zip' in pdf_file_name:
            common.print_('zip压缩包名称', pdf_file_name)
            # 使用 BytesIO 读取 response.content（模拟文件）
            with zipfile.ZipFile(BytesIO(response_table.content)) as zip_file:
                # 遍历 ZIP 文件中的所有文件
                for file_name in zip_file.namelist():
                    common.print_('遍历|zip压缩包内pdf文件', file_name)
                    # 检查是否是 pdf 文件（不区分大小写）
                    if file_name.lower().endswith('.pdf'):
                        # ————————————-上传服务器
                        # 读取 pdf 文件内容（bytes） 然后上传到服务器
                        files = {"file": (file_name, zip_file.read(file_name), "application/pdf")}
                        # {'status': 1, 'message': '上传成功', 'data': '/uploads/task/002ec6e26ee6c59f285e20b978c409e2.pdf', 'code': 1}
                        response_server = billRequest.saveOrderList(files=files)
                        response_server = response_server.json()
                        common.print_('response_server', response_server)
                        pdf_data_list += [{
                            'url': response_server['data'],
                            'site': site,
                            **pdf_data_map[file_name]
                        }]
                    else:
                        raise UnknownException('[shopee pdf下载]zip压缩包内的数据不是pdf文件，错误！！！')
        elif '.pdf' in pdf_file_name:
            common.print_('pdf名称', pdf_file_name)
            # ————————————-上传服务器
            files = {"file": (pdf_file_name, BytesIO(response_table.content), "application/pdf")}
            # {'status': 1, 'message': '上传成功', 'data': '/uploads/task/002ec6e26ee6c59f285e20b978c409e2.pdf', 'code': 1}
            response_server = billRequest.saveOrderList(files=files)
            response_server = response_server.json()
            common.print_('response_server', response_server)
            pdf_data_list += [{
                'url': response_server['data'],
                'site': site,
                **pdf_data_map[pdf_file_name]
            }]
        else:
            raise UnknownException('[shopee pdf下载]未知的文件格式，错误！！！')
        common.print_('pdf_data_list', pdf_data_list)

        if pdf_data_list:
            # 保存数据
            request_id = str(uuid.uuid4())
            options['request_id'] = request_id
            options['response'] = json.dumps(pdf_data_list, ensure_ascii=False, separators=(',', ':'))
            taskRequest.save(options)

    def getNoNativeShopAmount(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee资金申报（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取shopee资金申报 非本土】')
        print('options', options)

        site = options.get('site', '').upper()
        merchant_id = str(shop_data.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        currency = shopApi.currency.get(site)

        # 参数检测
        shopApi.TaskParamsException('非本土获取资金申报', site, merchant_id, shop_id)

        if not currency: raise UnknownException("currency 货币获取异常")

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver=driver, options=options)
            common.print_('shop_at', shop_at)


        url = "https://seller.shopee.cn/api/v4/accounting/cbpc/seller_income/income_overview/get_income_overviews"
        params = {
            "cnsc_shop_id": shop_id,
            "cbsc_shop_region": site.lower()
        }
        headers = {
            "accept": "application/json, text/plain, */*",
        }
        # 获取资金申报
        res = executeService.request(driver=driver, headers=headers, url=url, params=params, method="GET")
        amount = json.loads(res)
        common.print_('获取资金申报账单', amount)
        if amount.get('code') != 0:
            raise UnknownException('[shopee获取资金申报]获取资金申报账单异常，错误！！！')

        amount_data = {}
        for amount_dict in amount.get('list', []):
            if amount_dict['type'] == 1:
                amount_data['uncompleted_order_amount'] = amount_dict['amount']
            elif amount_dict['type'] == 2:
                amount_data['approaching'] = amount_dict['amount']

        amount_data['currency'] = currency
        amount_data['fund_declaration_amount'] = amount_data['approaching'] + amount_data['uncompleted_order_amount']
        common.print_('amount_data', amount_data)
        # 保存数据
        request_id = str(uuid.uuid4())
        options['request_id'] = request_id
        options['response'] = json.dumps(amount_data, ensure_ascii=False, separators=(',', ':'))
        taskRequest.save(options)

    def getNativeShopAmount(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 获取shopee资金申报（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print('——————————————【shopee获取shopee资金申报 本土】')
        print('options', options)

        site = options.get('site', '').upper()
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)
        currency = shopApi.currency.get(site)

        # 参数检测
        shopApi.TaskParamsException('本土获取资金申报', site, shop_id)

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'本土获取账单 - 未匹配到该站点url {site}')

        if not currency: raise UnknownException("currency 货币获取异常")

        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6",
        }
        url = f"https://seller.{map_url}/api/v4/accounting/pc/seller_income/income_overview/get_income_overviews"

        # 获取资金申报
        res = executeService.request(driver=driver, headers=headers, url=url, method="GET")
        amount = json.loads(res)
        common.print_('获取资金申报账单', amount)
        if amount.get('code') != 0:
            raise UnknownException('[shopee获取资金申报]获取资金申报账单异常，错误！！！')

        amount_data = {}
        for amount_dict in amount.get('list', []):
            if amount_dict['type'] == 9:
                amount_data['uncompleted_order_amount'] = amount_dict['amount']
                break

        amount_data['currency'] = currency
        common.print_('amount_data', amount_data)
        # 保存数据
        request_id = str(uuid.uuid4())
        options['request_id'] = request_id
        options['response'] = json.dumps(amount_data, ensure_ascii=False, separators=(',', ':'))
        taskRequest.save(options)


