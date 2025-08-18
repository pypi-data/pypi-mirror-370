import json
import time
from urllib.parse import urlparse
from undetected_chromedriver import Chrome as unChrome

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common import Common   # 公共库
from rpa_common import Env   # 环境配置
from rpa_common.library.Request import Request   # requests请求
from rpa_common.request import ShopRequest   # 店铺信息获取并操作
from rpa_common.service.EmailService import EmailService   # 邮箱操作
from rpa_common.service.ExecuteService import ExecuteService  # 请求
from rpa_common.exceptions import *

from rpa_shopee.api.ShopApi import ShopApi   # shopee店铺信息获取


env = Env()
request = Request()
common = Common()
executeService = ExecuteService()
shopRequest = ShopRequest()
emailService = EmailService()
shopApi = ShopApi()

class ShopeeService():
    def __init__(self):
        super().__init__()
        self.host = env.get()['api']

    def login(self, driver: unChrome, shop_data, options):
        '''登陆判断'''
        options = options['params']
        if shop_data.get('is_local') == 0:
            # 非本土登录
            res = self.no_native_login(driver, shop_data, options)
            if res['status'] != 1:
                print(res['message'])
                raise LoginException(f'非本土登陆{res["message"]}')
        elif shop_data.get('is_local') == 1:
            # 本土登录
            res = self.native_login(driver, shop_data, options)
            if res['status'] != 1:
                print(res['message'])
                raise LoginException(f'本土登陆{res["message"]}')
        else:
            raise LoginException(f'shopee登陆仅支持本土和非本土 is_local|{shop_data.get("is_local")}|错误')
        time.sleep(5)

    def no_native_login(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 登录（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print("——————————————【shopee登陆 非本土】")
        print('shop_data', shop_data)
        print('options', options)

        storage_data = shop_data.get("storage_data")
        time.sleep(1)
        # 如果 storage_data 存在，注入缓存
        if storage_data:
            print("🌐 使用缓存尝试自动登录")
            self.inject_storage(driver, storage_data)
        # 访问页面
        driver.get('https://seller.shopee.cn')
        time.sleep(4)
        wait = WebDriverWait(driver, 20)
        # 等待页面加载完成
        wait.until(EC.url_contains('shopee.cn'))
        # 获取登录信息
        res = shopApi.getInfoAccountList(driver=driver, options=options)
        print("获取登录信息", res)
        if res.get('code', 1000) == 0:
            print("✅ 成功获取店铺信息，可能已登录")
            need_login = False
        else:
            print("🔒 可能未登录")
            print(res)
            need_login = True
        # 根据 need_login 决定是否执行登录逻辑
        if need_login:
            # 执行登录流程
            login_res = self.account_login(driver, shop_data, options)
            # 登录失败
            if login_res['status'] == 0:
                return login_res
        else:
            # 已登录
            print("✅ 已登录")

        if 'existing-sellers-welcome' in driver.current_url:
            raise LoginException('登陆成功，但KYC未验证，无法进行执行')

        print("✅ 登录成功")

        return common.back(1, '登录成功')

    def account_login(self, driver: unChrome, shop_data, options, login_num=1):
        '''
        @Desc    : 账号登录（非本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        shop_global_id = shop_data.get("shop_global_id")
        login_name = shop_data.get("login_name")
        password = shop_data.get("password")
        email_data = shop_data.get("email_data", {})
        email = email_data.get("email")
        auth_code = email_data.get("auth_code")

        # 参数检测
        shopApi.TaskParamsException('非本土账号登录', shop_global_id, login_name, password)

        # 访问页面
        # driver.get('https://seller.shopee.cn')
        wait = WebDriverWait(driver, 20)

        try:
            # 等待登陆页面加载完成
            wait.until(EC.url_contains('account/signin'))
        except:
            pass
        time.sleep(1)

        print("检查页面状态")
        if 'account/signin' not in driver.current_url and '/verify/' not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            time.sleep(5)
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        if '/verify/' in driver.current_url:
            raise LoginException('登陆失败 始终停留验证页面 /verify/')

        input_user = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')  # 账户输入框
        input_user.send_keys(login_name)
        print("✅ 账号已填写")
        time.sleep(1)

        input_password = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')  # 密码输入框
        input_password.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(1)

        # 如果有记住密码的复选框，可以通过以下代码进行勾选：
        input_checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')  # 记住密码复选框
        if not input_checkbox.is_selected():
            # 使用 JavaScript 来点击复选框
            driver.execute_script("arguments[0].click();", input_checkbox)
            print("✅ 记住密码复选框已勾选")
            time.sleep(1)

        # 找到页面中的所有按钮
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        # 遍历按钮，查找第一个非空文本按钮并点击
        for button in buttons:
            if button.text.strip() != '':
                button.click()
                print("✅ 点击了登录按钮")
                break
        time.sleep(1)

        # 获取当前URL
        current_url = driver.current_url
        print('[当前url] --> ', current_url)

        print("等待15秒")
        time.sleep(15)

        print("检查页面状态")
        if 'account/signin' not in driver.current_url and "/verify/" not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            time.sleep(5)
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        # 执行 JavaScript
        js_code = """
        const text_innerText = document.body.innerText;   // web文本内容 公用
        console.log("[定时器检测中][捕获错误] -> ",window.data_info_0x294312)
        const login_error = document.querySelector('.login-error') || document.querySelector('div[role="alert"]');     // 登录错误的异常信息
        const email_error = document.querySelector('.pov-modal__title');  // 邮箱验证码验证
        const email_url_verify = document.querySelector('button[aria-label="Verify by Email Link"]');  // 邮箱链接验证
        const email_url_verify_th = document.querySelector('button[aria-label="ยืนยันตัวตนผ่านลิงก์"], button[aria-label="ยืนยันตัวตนด้วยลิงก์ในอีเมล"]');    // 邮箱链接验证（泰国本土的）
        const email_url_sms_verify_th = document.body.innerText.includes("กรุณาตรวจสอบข้อความในโทรศัพท์ขอ");    // SMS手机验证（泰国本土的）
        if (window.location.href.includes("/verify/") && (email_url_verify || email_url_verify_th)){
            return '邮箱链接验证';
        } else if (window.location.href.includes("/verify/") && email_url_sms_verify_th){
            return 'SMS验证';
        } else if (window.location.href.includes("/verify/")){
            return '未知的验证页面';
        } else if (login_error) {
            return '[其他错误信息]' + login_error.textContent;
        } else if (document.querySelector('aside')) {
            return '人机验证';
        } else if (email_error) {
            document.querySelectorAll('button').forEach(f=>{
                if (f.innerText === '发送'){
                    f.click();
                };
            });
            return '邮箱验证码';
        } else {
            return '未知错误';
        }
        """

        # 运行 JavaScript 并获取返回的结果
        result = driver.execute_script(js_code)
        # 输出结果
        print("JavaScript 执行结果:", result)
        if result == '邮箱验证码':
            print("❗ [邮箱验证码验证]")

            # 参数检测
            shopApi.TaskParamsException('非本土账号登录-邮箱验证码|email|auth_code', email, auth_code)
            verify_code = emailService.get_verify_code(type='shopee_verifycode', data={
                "auth_code": auth_code,
                "platform": "163",
                "email": email
            })
            print('shopee获取到邮箱验证码', verify_code)
            if not verify_code.get('data', ''):
                LoginException(f'登录失败-[邮箱验证码 获取失败] - {verify_code}')

            # 邮箱验证码输入框
            input_verify = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][placeholder="请输入"]')
            input_verify.send_keys(verify_code['data'])
            print("📩 邮箱验证码已填写")
            time.sleep(1)

            # 邮箱确认按钮
            button = driver.find_element(By.CSS_SELECTOR, ".pov-modal__footer button[class='eds-button eds-button--primary eds-button--normal']")
            button.click()
            print("✅ 点击了确定按钮")
            time.sleep(3)

            if login_num == 2:
                raise LoginException('登录失败-[验证失败]')
            return self.account_login(driver, shop_data, options, login_num + 1)
            # raise LoginException('登录失败-[邮箱验证码验证]')
        elif result == '邮箱链接验证':
            print("❗ [邮箱链接验证]")
            raise LoginException('登录失败-[邮箱链接验证]')
        elif result == 'SMS验证':
            print("❗ [SMS验证]")
            raise LoginException('登录失败-[SMS验证]')
        elif result == '未知的验证页面':
            print("❗ [未知的验证页面]")
            raise LoginException('登录失败-[未知的验证页面]')
        elif result == '人机验证':
            print("❗ [人机验证]")
            raise LoginException('登录失败-[人机验证]')
        elif result == '未知错误':
            print("❗ [未知错误]")
            raise LoginException('登录失败-[未知错误]')
        else:
            print(f"❗ {result}")
            raise LoginException(f'登录失败-[{result}]')

    def inject_storage(self, driver: unChrome, storage_data):
        '''
        @Desc    : 注入缓存（通用）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            cookies = storage_data.get("cookies")

            driver.execute_cdp_cmd("Network.enable", {})
            for cookie in cookies:
                try:
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                        "sameSite": cookie.get("sameSite", "None")
                    })
                except Exception as e:
                    print(f"⚠️ CDP 注入 cookie 失败：{cookie}, 错误：{e}")
        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")
        print("注入缓存成功")

    def save_storage(self, driver: unChrome, shop_global_id):
        '''
        @Desc    : 保存店铺缓存（通用）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取 cookies
        print("获取 cookies")
        cookies = driver.get_cookies()

        storage_data = {
            "shop_global_id": shop_global_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['code'] != 1:
            print("保存缓存成功")
            return common.back(0, res['msg'])

        print("保存缓存成功")

    def native_login(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 登录（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        print("——————————————【shopee登陆 本土】")
        print('shop_data', shop_data)
        print('options', options)

        site = options.get("site").upper()
        storage_data = shop_data.get("storage_data")

        if not site:
            raise TaskParamsException('site 请选择站点')

        map_url = shopApi.map_url['HOST'].get(site)
        if not map_url: raise TaskParamsException(f'site 该站点不存在 {site}')

        time.sleep(1)
        # 注入缓存，和语言
        storage_data['cookies'] += [{
                        "name": 'language',
                        "value": 'en',
                        "domain": f'.{map_url}',
                        "path": '/',
                        "secure": False,
                        "httpOnly": False,
                        "sameSite": ""
                    }]
        print("🌐 使用缓存尝试自动登录")
        self.inject_storage(driver, storage_data)

        # 访问登陆页面  https://shopee.co.th/verify/ivs
        driver.get(f'https://accounts.{map_url}/seller/login')
        time.sleep(4)

        wait = WebDriverWait(driver, 20)
        # 等待页面加载完成
        wait.until(EC.url_contains(map_url))

        # 获取登陆信息
        need_login = self.is_native_login(driver, shop_data, options)
        # 根据 need_login 决定是否执行登录逻辑
        if not need_login:
            # 执行登录流程
            login_res = self.native_account_login(driver, shop_data, options)
            # 登录失败
            if login_res['status'] == 0:
                return login_res
            # 获取登陆信息
            need_login = self.is_native_login(driver, shop_data, options)
            if not need_login: raise LoginException('本土登录失败')

        if 'existing-sellers-welcome' in driver.current_url:
            raise LoginException('登陆成功，但KYC未验证，无法进行执行')

        common.print_("✅ 本土登录成功")
        return common.back(1, '登录成功')

    def is_native_login(self, driver: unChrome, shop_data, options) ->bool:
        """
        @Desc     : 判断登陆情况并判断店铺id是否正确 （本土）
        @Author   : 祁国庆
        @Time     : 2025/08/09 10:30:57
        True 登陆成功  False 登陆失败
        """
        shop_id = options.get('shop_id')
        # 获取登录信息
        res = shopApi.getNativeInfoList(driver=driver, options=options)
        common.print_("获取登录信息", res)
        if res.get('errcode') == 0:
            common.print_("✅ 成功获取店铺信息，本土已登录")
            if str(shop_id) != str(res.get('shopid','')):
                raise TaskParamsException(f'{shop_id} 本土店铺ID与当前登陆店铺ID不一致')
            return True
        common.print_("🔒 shopee 本土未登录")
        return False

    def native_account_login(self, driver: unChrome, shop_data, options):
        '''
        @Desc    : 账号登录（本土）
        @Author  : 祁国庆
        @Time    : 2024/05/31 15:42:22
        '''
        shop_global_id = shop_data.get("shop_global_id")
        login_name = shop_data.get("login_name")
        password = shop_data.get("password")

        # 参数检测
        shopApi.TaskParamsException('本土账号登录', shop_global_id, login_name, password)

        wait = WebDriverWait(driver, 20)

        try:
            # 等待登陆页面加载完成
            wait.until(EC.url_contains('seller/login'))
        except:
            pass
        time.sleep(1)

        print("检查页面状态")
        if 'seller/login' not in driver.current_url and '/verify/' not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            time.sleep(5)
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        if '/verify/' in driver.current_url:
            raise LoginException('登陆失败 停留验证页面 /verify/')

        input_user = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')  # 账户输入框
        input_user.send_keys(login_name)
        print("✅ 账号已填写")
        time.sleep(1)

        input_password = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')  # 密码输入框
        input_password.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(1)

        # 找到页面中的所有按钮
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        # 遍历按钮，查找第一个非空文本按钮并点击
        for button in buttons:
            if button.text.strip() != '':
                button.click()
                print("✅ 点击了登录按钮")
                break
        time.sleep(1)

        # 获取当前URL
        current_url = driver.current_url
        print('[当前url] --> ', current_url)

        print("等待15秒")
        time.sleep(15)

        print("检查页面状态")
        if 'seller/login' not in driver.current_url and "/verify/" not in driver.current_url:
            print('✅ 已不在登陆页 登陆成功')
            time.sleep(5)
            # 保存店铺缓存
            self.save_storage(driver, shop_global_id)
            return common.back(1, '登录成功')

        # 执行 JavaScript
        js_code = """
        const text_innerText = document.body.innerText;   // web文本内容 公用
        console.log("[定时器检测中][捕获错误] -> ",window.data_info_0x294312)
        const login_error = document.querySelector('.login-error') || document.querySelector('div[role="alert"]');     // 登录错误的异常信息
        const email_error = document.querySelector('.pov-modal__title');  // 邮箱验证码验证
        const email_url_verify = document.querySelector('button[aria-label="Verify by Email Link"]');  // 邮箱链接验证
        const email_url_verify_th = document.querySelector('button[aria-label="ยืนยันตัวตนผ่านลิงก์"], button[aria-label="ยืนยันตัวตนด้วยลิงก์ในอีเมล"]');    // 邮箱链接验证（泰国本土的）
        const email_url_sms_verify_th = document.body.innerText.includes("กรุณาตรวจสอบข้อความในโทรศัพท์ขอ");    // SMS手机验证（泰国本土的）
        if (window.location.href.includes("/verify/") && (email_url_verify || email_url_verify_th)){
            return '邮箱链接验证';
        } else if (window.location.href.includes("/verify/") && email_url_sms_verify_th){
            return 'SMS验证';
        } else if (window.location.href.includes("/verify/")){
            return '未知的验证页面';
        } else if (login_error) {
            return '[其他错误信息]' + login_error.textContent;
        } else if (document.querySelector('aside')) {
            return '人机验证';
        } else if (email_error) {
            return '邮箱验证码';
        } else {
            return '未知错误';
        }
        """

        # 运行 JavaScript 并获取返回的结果
        result = driver.execute_script(js_code)
        # 输出结果
        print("JavaScript 执行结果:", result)
        if result == '邮箱验证码':
            print("❗ [邮箱验证码验证]")
            raise LoginException('登录失败-[邮箱验证码验证]')
        elif result == '邮箱链接验证':
            print("❗ [邮箱链接验证]")
            raise LoginException('登录失败-[邮箱链接验证]')
        elif result == 'SMS验证':
            print("❗ [SMS验证]")
            raise LoginException('登录失败-[SMS验证]')
        elif result == '未知的验证页面':
            print("❗ [未知的验证页面]")
            raise LoginException('登录失败-[未知的验证页面]')
        elif result == '人机验证':
            print("❗ [人机验证]")
            raise LoginException('登录失败-[人机验证]')
        elif result == '未知错误':
            print("❗ [未知错误]")
            raise LoginException('登录失败-[未知错误]')
        else:
            print(f"❗ {result}")
            raise LoginException(f'登录失败-[{result}]')


