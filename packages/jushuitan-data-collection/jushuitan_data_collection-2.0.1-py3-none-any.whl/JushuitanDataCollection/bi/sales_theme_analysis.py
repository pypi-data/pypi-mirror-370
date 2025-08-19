"""
报表-销售主题分析
"""

import json
import re
from contextlib import suppress
from time import sleep, time
from urllib.parse import urlencode

from BrowserAutomationLauncher import Browser
from BrowserAutomationLauncher._utils.tools import DateTimeTools
from DrissionPage.errors import ContextLostError
from requests import post


class Urls:
    main_page = 'https://bi.erp321.com/app/daas/report/subject/adsorder/default.aspx'


class SalesThemeAnalysis:
    PAGE_TITLE = '销售主题分析'

    def __init__(self, browser: Browser):
        self._browser = browser
        self._timeout = 15

    def _get__main_page(self):
        """
        获取标题为 [销售主体分析报表] 的页面
        """

        with suppress(Exception):
            page = self._browser.chromium.get_tab(title=self.PAGE_TITLE)
            return page

        page = self._browser.chromium.new_tab(url=Urls.main_page)
        return page

    def get__multidimension(
        self,
        include_tag: str,
        begin_date: str,
        end_date: str,
        timeout: int | float = None,
    ):
        """
        获取多维分析数据

        Args:
            include_tag: 包含的标签
            begin_date: 起始日期
            end_date: 结束日期
        """

        page = self._get__main_page()

        iframe = page.get_frame('#tab0', timeout=8)

        for _ in range(3):
            with suppress(ContextLostError):
                form_ele = iframe.ele('#form1', timeout=5)
                break
            sleep(3)

        if not form_ele:
            raise RuntimeError('未找到查询表单元素')

        viewstate_ele = form_ele.ele('#__VIEWSTATE', timeout=1)
        viewstategenerator_ele = form_ele.ele('#__VIEWSTATEGENERATOR', timeout=1)

        search = '[{"k":"B.skulabels","v":"$include_tag","c":"@like","t":""},{"k":"cost_type","v":"1","c":"@=","t":""},{"k":"A.status","v":"SENT","c":"@=","t":""},{"k":"C.afterstatus","v":"CONFIRMED","c":"@=","t":""},{"k":"combinesku_type","v":2,"c":"@=","t":""},{"k":"combinesku","v":1,"c":"@=","t":""},{"k":"is_currency","v":0,"c":"@=","t":""},{"k":"A.send_date","v":"$begin_date","c":">=","t":"date"},{"k":"export_date_begin","v":"$end_date","c":">="},{"k":"A.send_date","v":"$reserve_date","c":"<","t":"date"},{"k":"export_date_end","v":"$reserve_date","c":"<"}]'

        reserve_date = DateTimeTools.date_calculate(days=-1, date=end_date)
        variable_table = {
            'include_tag': include_tag,
            'begin_date': begin_date,
            'end_date': end_date,
            'reserve_date': reserve_date,
        }
        for key, value in variable_table.items():
            search = search.replace(f'${key}', value)

        request_data = {
            '__VIEWSTATE': viewstate_ele.value,
            '__VIEWSTATEGENERATOR': viewstategenerator_ele.value,
            'search': search,
            'dataPageCount': None,
            'column_name': ['渠道', '日期'],
            '__CALLBACKID': 'ACall1',
            '__CALLBACKPARAM': r'{"Method":"LoadDataToJSON","Args":["1","","{\"fld\":\"销售数量\",\"type\":\"desc\"}"],"CallControl":"{page}"}',
        }

        api_uri = iframe.attr('src')
        _timeout = timeout if isinstance(timeout, (int, float)) else 120
        resp = post(
            api_uri,
            params={'ts__': int(time() * 1000), 'am__': 'LoadDataToJSON'},
            headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'referer': api_uri,
                'cookie': page.cookies().as_str(),
            },
            data=urlencode(request_data, doseq=True),
            timeout=_timeout,
        )

        if resp.status_code != 200:
            raise RuntimeError(f'请求失败，状态码：{resp.status_code}')

        if not isinstance(resp.text, str):
            raise ValueError('响应数据非预期的 str 类型')

        resp_data = re.sub(r'^0\|', '', resp.text)
        try:
            resp_data = json.loads(resp_data)
        except Exception as err:
            raise ValueError(f'响应数据 JSON 化出错: {err}') from err

        if 'ReturnValue' not in resp_data:
            raise KeyError('响应数据中未找到 ReturnValue 字段')

        return_value = resp_data['ReturnValue']
        if not isinstance(return_value, str):
            raise TypeError('响应数据中的 ReturnValue 字段非预期的 str 类型')

        try:
            return_value = json.loads(return_value)
        except Exception as err:
            raise ValueError(
                f'响应数据中的 ReturnValue 字段数据 JSON 化出错: {err}'
            ) from err

        if 'datas' not in return_value or not (datas := return_value['datas']):
            return

        data_list: list[dict] = []
        for item in datas:
            if '实发数量' not in item:
                item['实发数量'] = item.get('sent_qty')

            data_list.append(item)

        return data_list
