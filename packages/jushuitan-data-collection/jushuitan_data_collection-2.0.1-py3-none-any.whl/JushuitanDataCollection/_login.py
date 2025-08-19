"""
处理聚水潭登录逻辑
"""

from typing import Callable

from BrowserAutomationLauncher import Browser
from BrowserAutomationLauncher._utils.tools import WebTools
from DrissionPage._pages.mix_tab import MixTab


class Urls:
    login = 'https://erp321.com/login.aspx'
    home = 'https://www.erp321.com/epaas'


class DataPacketUrls:
    login = 'https://api.erp321.com/erp/webapi/UserApi/WebLogin/Passport'
    get_user_info = 'https://api.erp321.com/erp/webapi/UserApi/Passport/GetUserInfo'


class Login:
    def __init__(self, browser: Browser):
        self._browser = browser

    def __wait__login_packet(self, callback: Callable, page: MixTab):
        """等待登录数据包返回"""

        page.listen.start(targets=DataPacketUrls.login, method='POST', res_type='XHR')
        callback()
        packet = page.listen.wait(timeout=15)
        if not packet:
            raise RuntimeError('登录超时')

        resp = packet.response.body
        if not isinstance(resp, dict):
            raise ValueError('登录返回的数据包格式非预期的 dict 类型')

        if 'data' not in resp:
            raise ValueError('登录返回的数据包中未找到 data 字段')
        data = resp['data']
        if not isinstance(data, dict):
            raise ValueError('登录返回的数据包中 data 字段格式非预期的 dict 类型')

        msg = data.get('msg')
        has_msg = msg and isinstance(msg, str)

        return has_msg

    def __alert__handler1(self, page: MixTab):
        """提示框处理模式1"""

        alert = page.ele('c:div.ant-modal-content', timeout=3)
        if not alert:
            return

        alert_footer = alert.ele('c:div.ant-modal-footer', timeout=3)
        confirm_btn = alert_footer.ele('t:button@@text()=确 定', timeout=1)
        if not confirm_btn:
            raise RuntimeError('未找到提示框中的确认按钮元素')

        confirm_btn.click(by_js=True)

    def __get__current_account(self, page: MixTab):
        """获取当前登录账号"""

        u_lid = page.cookies().as_dict().get('u_lid')
        return WebTools.url_decode(u_lid)

    def __login_mode1(self, account: str, password: str, page: MixTab):
        """登录模式1"""

        login_type_switcher = page.ele('t:a@@text()=账号密码登录', timeout=3)
        if login_type_switcher:
            login_type_switcher.click(by_js=True)

        account_input = page.ele('#login_id', timeout=3)
        if not account_input:
            raise RuntimeError('未找到登录账号输入框元素')

        password_input = page.ele('#password', timeout=1)
        if not password_input:
            raise RuntimeError('未找到登录密码输入框元素')

        account_input.input(account, clear=True)
        password_input.input(password, clear=True)

        agreement_checkbox_text = page.ele('t:span@@text()^我已阅读并同意', timeout=1)
        if not agreement_checkbox_text:
            raise RuntimeError('未找到协议勾选框标签元素')
        agreement_checkbox = agreement_checkbox_text.prev(
            'c:span.ant-checkbox', timeout=1
        )
        if not agreement_checkbox:
            raise RuntimeError('未找到协议勾选框元素')
        if 'ant-checkbox-checked' not in agreement_checkbox.attr('class'):
            agreement_checkbox.click(by_js=True)

        login_btn = page.ele('t:button@@text()=立即登录', timeout=1)
        if not login_btn:
            raise RuntimeError('未找到登录按钮元素')

        if self.__wait__login_packet(lambda: login_btn.click(by_js=True), page):
            self.__alert__handler1(page)

        if page.wait.title_change('聚水潭 ERP', timeout=8):
            return

        if self.__get__current_account() != account:
            raise RuntimeError('登录失败，请检查账号密码是否正确')

    def login(self, account: str, password: str):
        """
        登录系统

        Args:
            account: 登录账号
            password: 登录密码
        """

        page = self._browser.chromium.latest_tab
        page.listen.start(
            targets=DataPacketUrls.get_user_info, method='POST', res_type='Fetch'
        )
        page.get(Urls.home)
        user_info__packet = page.listen.wait(timeout=6)
        if not user_info__packet or user_info__packet.response.status != 200:
            return self.__login_mode1(account, password, page)

        user_info__resp: dict = user_info__packet.response.body
        if not isinstance(user_info__resp, dict):
            raise ValueError('用户信息数据包非预期的 dict 类型')

        if 'data' not in user_info__resp:
            raise ValueError('用户信息数据包中未找到 data 字段')

        user_info__data = user_info__resp['data']
        if not isinstance(user_info__data, dict):
            raise ValueError('用户信息数据包中 data 字段格式非预期的 dict 类型')

        if user_info__data.get('loginId') != account:
            raise RuntimeError('当前已登录账号与预期账号不符')

        return
