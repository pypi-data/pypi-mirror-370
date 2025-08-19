"""
报表模块数据采集
"""

import json
from random import uniform
from tempfile import gettempdir
from time import sleep, time

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from BrowserAutomationLauncher._utils.tools import (
    CommonTools,
    DateTimeTools,
    Downloader,
    OsTools,
)
from DrissionPage._pages.mix_tab import MixTab
from requests import post

from ._dict import RequestData


class Urls:
    goods_profit = 'https://ss.erp321.com/profit-report/goods-profit'
    """商品利润页面"""
    multi_dimension = 'https://ss.erp321.com/profit-report/multi-dimension'
    """多维度数据统计[店铺] 自定义查询"""


class DataPacketUrls:
    goods_profit = 'https://pf1.erp321.com/WebApi/PF/OrderSku/GetPFSkuList?uvalue=pfcweb_profit-report.goods-profit'
    """商品利润查询接口"""
    goods_set_list = 'https://pf.erp321.com/WebApi/PF/PfActivity/GetPfActivityAllList?uvalue=pfcweb_profit-report.goods-profit'
    """商品集合列表获取"""
    multi_dimension__export = 'https://pf.erp321.com/WebApi/PF/ProfitForDate/ExportDayGroupShop?uvalue=pfcweb_profit-report.multi-dimension'
    """多维度统计[店铺]导出"""
    goods_profit__export = 'https://pf.erp321.com/WebApi/PF/AdaptiveExport/ExprotPfSkuPfNew?uvalue=pfcweb_profit-report.goods-profit'
    """商品利润导出"""
    async_tasks = 'https://pf.erp321.com/WebApi/PF/NightPlan/GetNightList?uvalue=pfcweb_profit-report.goods-profit'
    """获取异步任务列表"""


class Report:
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
    }

    def __init__(self, browser: Browser):
        self._browser = browser
        self._timeout = 15

    def __generate__combine_date(self, begin_date: str, end_date: str):
        """生成数据包查询所需要的 combine_date 值"""

        date_maps = [f'{begin_date} 00:00:00.000', f'{end_date} 23:59:59.999']
        combine_begin_date, combine_end_date = [
            DateTimeTools.date_to_utc(
                date_map, pattern='%Y-%m-%d %H:%M:%S.%f', replace_with_nowtime=False
            )
            for date_map in date_maps
        ]

        return combine_begin_date, combine_end_date

    def _get_target_page__byurl(self, url: str):
        """根据 URL 获取目标页面标签"""

        page = None
        for tab in self._browser.chromium.get_tabs():
            if url in tab.url:
                page = tab
                self._browser.chromium.activate_tab(page)
                break

        if page is None:
            page = self._browser.chromium.new_tab()
            page.get(url)
            page.wait.eles_loaded('t:button@@text()=查 询', timeout=30)

        return page

    def get__async_task(self, task_id: int, page: MixTab, timeout: float | int = None):
        """
        获取异步任务结果

        Args:
            task_id: 任务ID
            page: 页面对象
        Returns:
            任务结果 (任务状态, 任务结果文件URL)
        """

        payload = {
            'ip': '',
            'page': {'currentPage': 1, 'pageSize': 25},
            'uid': '',
            'coid': '',
            'data': {'versionModel': 10, 'cbShopSite': '', 'useOldTaskTable': False},
            'ssProjectType': 'SS',
            'ssClientType': 'Web',
        }
        headers = {
            **self._headers,
            'Cookie': page.cookies().as_str(),
            'Referer': Urls.goods_profit,
        }
        real_timeout = timeout if isinstance(timeout, (int, float)) else self._timeout
        resp = post(
            url=DataPacketUrls.async_tasks,
            headers=headers,
            json=payload,
            timeout=real_timeout,
        )
        if resp.status_code != 200:
            raise ValueError(f'异步任务列表请求出错: 状态码 {resp.status_code}')

        try:
            resp_jsonify = resp.json()
        except Exception as e:
            raise ValueError(f'异步任务列表数据格式化 JSON 出错: {e}') from e

        data = DataPacketProcessor(resp_jsonify).filter('data')
        task_list: list[dict] = data['data']

        task = next((task for task in task_list if task['tId'] == task_id), None)
        if not task:
            raise ValueError(f'未找到ID为 {task_id} 的异步任务')

        return (task['status'], task['fileUrl'])

    def get__goods_set_list(self, timeout: float | int = None):
        """获取当前登录账号的商品集合列表"""

        page = self._get_target_page__byurl(Urls.goods_profit)

        payload = {
            'ip': '',
            'page': {'currentPage': 1, 'pageSize': 25},
            'uid': '',
            'coid': '',
            'data': {},
            'ssProjectType': 'SS',
            'ssClientType': 'Web',
        }
        real_timeout = timeout if isinstance(timeout, (int, float)) else self._timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': page.cookies().as_str(),
            'Referer': Urls.goods_profit,
        }
        response = post(
            url=DataPacketUrls.goods_set_list,
            headers=headers,
            json=payload,
            timeout=real_timeout,
        )
        if response.status_code != 200:
            raise ValueError(f'请求出错: 状态码 {response.status_code}')

        try:
            resp_jsonify = response.json()
        except Exception as e:
            raise ValueError(f'数据格式化 JSON 出错: {e}') from e

        data = DataPacketProcessor(resp_jsonify).filter('data')
        goods_set: list[dict] = data['data']
        return goods_set

    def get__goods_profit__detail(
        self,
        shop_id: str,
        goods_ids: list[str],
        begin_date: str,
        end_date: str,
        raw=False,
        timeout: float = None,
    ):
        """
        获取商品利润数据

        Args:
            shop_id: 店铺ID
            goods_ids: 商品ID列表
            begin_date: 开始日期
            end_date: 结束日期
        Returns:
            数据对象: {商品id: {字段: 值, ...}, ...}
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        # 检查当前打开的页面中是否有胜算商品利润页面
        page = None
        for tab in self._browser.chromium.get_tabs():
            if Urls.goods_profit in tab.url:
                page = tab
                self._browser.chromium.activate_tab(page)
                break

        if page is None:
            page = self._browser.chromium.new_tab()
            page.change_mode('d', go=False)
            page.get(Urls.goods_profit)
            page.wait.eles_loaded('t:button@@text()=查 询', timeout=30)

        combine_begin_date, combine_end_date = self.__generate__combine_date(
            begin_date, end_date
        )

        reqdata = (
            RequestData.goods_profit.replace('$combine_begin_date', combine_begin_date)
            .replace('$combine_end_date', combine_end_date)
            .replace('$shop_id', str(shop_id))
            .replace('$goods_ids', json.dumps(goods_ids))
            .replace('$begin_date', begin_date)
            .replace('$end_date', end_date)
        )
        reqdata_json = json.loads(reqdata)
        resp = post(
            DataPacketUrls.goods_profit,
            json=reqdata_json,
            timeout=_timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'Content-Type': 'application/json;charset=UTF-8',
                'Cookie': page.cookies().as_str(),
                'Referer': Urls.goods_profit,
            },
        )
        try:
            resp_json: dict = resp.json()
        except Exception as e:
            raise ValueError(f'商品利润数据包格式化出错: {e}') from e

        if 'data' not in resp_json:
            raise ValueError('商品利润数据包中未找到 data 字段')
        data = resp_json['data']

        if raw is True:
            return data

        if not isinstance(data, dict):
            raise ValueError('商品利润数据包中 data 字段非预期 dict 类型')

        if 'fldHeads' not in data:
            raise ValueError('商品利润数据包中未找到 data.fldHeads 字段')
        heads: list[dict] = data['fldHeads']
        if not isinstance(heads, list):
            raise ValueError('商品利润数据包中 data.fldHeads 字段非预期 list 类型')

        if 'dataList' not in data:
            raise ValueError('商品利润数据包中未找到 data.dataList 字段')
        data_list: list[dict] = data['dataList']
        if not isinstance(data_list, list):
            raise ValueError('商品利润数据包中 data.dataList 字段非预期 list 类型')

        titles = {head.get('fld'): head.get('title') for head in heads}
        records = {}
        for item in data_list:
            goods_id = item.get('primaryKey')
            record = {}
            for key, title in titles.items():
                value = item.get(key)
                record[title] = value
            records[goods_id] = record

        return records

    def download__multi_dimension(
        self,
        begin_date: str,
        end_date: str,
        raw=False,
        save_path: str = None,
        save_name: str = None,
        timeout: float = None,
    ):
        """
        下载多维度统计报表

        Args:
            begin_date: 开始日期
            end_date: 结束日期
            raw: 如果为 True 则返回文件路径, 否则返回解析后的数据
            save_path: 文件保存的路径
            save_name: 文件保存的名称
            timeout: 超时时间
        Returns:
            数据列表
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        # 检查当前打开的页面中是否有多维度数据统计页面
        page = None
        for tab in self._browser.chromium.get_tabs():
            if Urls.multi_dimension in tab.url:
                page = tab
                self._browser.chromium.activate_tab(page)
                break

        if page is None:
            page = self._browser.chromium.new_tab()
            page.get(Urls.multi_dimension)
            page.wait.eles_loaded('t:button@@text()=查 询', timeout=30)

        payload = {
            'ip': '',
            'page': {'currentPage': 1, 'pageSize': 25},
            'uid': '',
            'coid': '',
            'data': {
                'conDitionJson': '{"shop":[],"gzMustSql":false,"date":["${begin_date_utc}","${end_date_utc}"],"olderDate":["${begin_date_utc}","${end_date_utc}"],"tabKey":0,"tabItem":{"name":"自定义查询","alias":"自定义查询操作","ruleName":null,"id":0,"remark":null,"type":0,"fromType":null,"isHidden":false,"dateType":null,"returnType":null,"ruleId":0,"useRealityReturnRate":null},"timeType":"day","planId":6,"isSplitCombine":true,"dateType":"senddate","returnType":"comfirmdate","ruleId":13912,"isCrossBorder":false,"beginDate":"${begin_date}","endDate":"${end_date}"}',
                'showCsgTypes': ['last', 'second', 'first'],
                'isExportCond': False,
            },
            'ssProjectType': 'SS',
            'ssClientType': 'Web',
        }

        begin_date_utc, end_date_utc = self.__generate__combine_date(
            begin_date, end_date
        )
        variable_table = {
            'begin_date': begin_date,
            'end_date': end_date,
            'begin_date_utc': begin_date_utc,
            'end_date_utc': end_date_utc,
        }
        payload['data']['conDitionJson'] = CommonTools.str_replace_by_variables(
            variable_table, payload['data']['conDitionJson']
        )

        resp = post(
            DataPacketUrls.multi_dimension__export,
            json=payload,
            timeout=_timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'Content-Type': 'application/json;charset=UTF-8',
                'Cookie': page.cookies().as_str(),
                'Referer': Urls.multi_dimension,
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(f'请求出错了: 响应状态码 {resp.status_code}')

        try:
            resp_jsonify = resp.json()
        except Exception as err:
            raise ValueError(f'响应体解析为 JSON 出错: {err}') from err

        data = DataPacketProcessor(resp_jsonify).filter('data.url')
        try:
            file_path = Downloader().download(
                url=data['url'],
                file_exists='overwrite',
                save_path=save_path or gettempdir(),
                rename=save_name,
                show_progress=True,
                timeout=_timeout,
                cookies=page.cookies().as_str(),
            )
        except Exception as err:
            raise RuntimeError(f'报表下载出错: {err}') from err

        if raw is True:
            return file_path

        try:
            data_list = OsTools.xlsx_read(file_path=file_path)
            OsTools.file_remove(file_path)
        except Exception as err:
            raise RuntimeError(f'报表文件解析出错: {err}') from err

        return data_list

    def download__goods_profit__bygoodsset(
        self,
        begin_date: str,
        end_date: str,
        goods_set_ids: list[int],
        is_accrued=False,
        raw=False,
        save_path: str = None,
        save_name: str = None,
        timeout: float = None,
    ):
        """
        根据商品集合下载商品利润报表

        Args:
            begin_date: 开始日期
            end_date: 结束日期
            goods_set_ids: 商品集合 ID 列表
            is_accrued: 是否使用预提方案. 一般跨境店使用
            raw: 如果为 True 则返回文件路径, 否则返回解析后的数据
            save_path: 文件保存的路径
            save_name: 文件保存的名称
            timeout: 超时时间
        Returns:
            数据列表
        """

        page = self._get_target_page__byurl(url=Urls.goods_profit)

        payload = {
            'ip': '',
            'page': {'currentPage': 1, 'pageSize': 25},
            'uid': '',
            'coid': '',
            'data': {
                'exportCondition': '{"isAds":false,"condition":{"act":${goods_set_ids},"dateFld":"send_date","combineDate":["${begin_date_utc}","${end_date_utc}"],"groupList":["shop_i_id"],"shop":[],"effective":"nosplit","planSel":3,"planShowAmountType":"Amount","groupByType":"shop_i_id","isShowOnlineSkuName":true,"ruleId":${rule_id},"splitCombine":true,"isShowOtherPromotion":true,"isRefundEstimate":false,"wmsCoidList":[],"buIdList":[],"skuIn":{"type":"anyonesku","values":[],"select":"in"},"skuOut":{"type":"anyonesku","values":[],"select":"out"},"labelIn":{"type":"anyonelabel","values":[],"select":"in"},"labelout":{"type":"anyonelabel","values":[],"select":"out"},"creatorList":[],"skuLabelIn":{"type":"anyoneskulabel","values":[],"select":"in"},"skuLabelOut":{"type":"anyoneskulabel","values":[],"select":"out"},"brands":[],"categorys":[],"vcNames":[],"goodsCostGroup":{"skuCostAmountSearchType":{"value":2,"label":"按固定值搜索商品成本"},"value":"","values":["",""]},"onlineSkuName":"","beginDate":"${begin_date}","endDate":"${end_date}","seachType":1,"skuGroup":"shop_i_id","orderType":[],"drpCoidtos":[],"skuCostAmountSearchType":2,"skuCostAmountList":[],"expSkuFee":false,"isOL":false,"isExport":true,"showCsgTypes":["last","second","first"],"isExportCond":false,"exportType":"pfskuactgroup","dateOrderType":null,"isCrossBorder":false}}'
            },
            'ssProjectType': 'SS',
            'ssClientType': 'Web',
        }

        begin_date_utc, end_date_utc = self.__generate__combine_date(
            begin_date, end_date
        )
        variable_table = {
            'rule_id': 22017 if is_accrued is True else 19694,
            'goods_set_ids': json.dumps(goods_set_ids, separators=(',', ':')),
            'begin_date_utc': begin_date_utc,
            'end_date_utc': end_date_utc,
            'begin_date': begin_date,
            'end_date': end_date,
        }
        payload['data']['exportCondition'] = CommonTools.str_replace_by_variables(
            variable_table, payload['data']['exportCondition']
        )

        return self.download__goods_profit_report(
            payload=payload,
            raw=raw,
            save_path=save_path,
            save_name=save_name,
            timeout=timeout,
            page=page,
        )

    def download__goods_profit_report(
        self,
        payload: dict,
        raw=False,
        save_path: str = None,
        save_name: str = None,
        timeout: float = None,
        page: MixTab = None,
    ):
        """
        下载自定义筛选条件商品利润数据报表

        Args:
            payload: 请求参数
            raw: 如果为 True 则返回文件路径, 否则返回解析后的数据
            save_path: 文件保存的路径
            save_name: 文件保存的名称
            timeout: 请求超时时间, 默认 15 秒
            page: 页面对象, 如果不传则自动创建
        Returns:
            数据列表或者文件路径
        """

        page = (
            page
            if isinstance(page, MixTab)
            else self._get_target_page__byurl(url=self.url)
        )

        real_timeout = timeout if isinstance(timeout, float) else timeout
        resp = post(
            DataPacketUrls.goods_profit__export,
            json=payload,
            timeout=real_timeout,
            headers={
                **self._headers,
                'Cookie': page.cookies().as_str(),
                'Referer': Urls.goods_profit,
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(f'请求出错: 状态码 {resp.status_code}')

        try:
            resp_jsonify = resp.json()
        except Exception as err:
            raise ValueError(f'响应体格式化 JSON 出错: {err}') from err

        data = DataPacketProcessor(resp_jsonify).filter(['?data.url', '?data.taskId'])

        file_url = data.get('url')
        if task_id := data.get('taskId'):
            # 系统检测到数据量过大，改为了异步导出
            start_time = time()
            while real_timeout > time() - start_time:
                sleep(uniform(5, 10))

                task_status, file_url = self.get__async_task(
                    task_id, page, timeout=real_timeout
                )
                if task_status == 'Success':
                    break
            else:
                raise TimeoutError('异步任务等待超时')

        if not file_url:
            raise RuntimeError('获取报表下载链接出错')

        try:
            file_path = Downloader().download(
                url=file_url,
                file_exists='overwrite',
                save_path=save_path or gettempdir(),
                rename=save_name,
                show_progress=True,
                timeout=real_timeout,
                cookies=page.cookies().as_str(),
            )
        except Exception as err:
            raise RuntimeError(f'报表下载出错: {err}') from err

        if raw is True:
            return file_path

        try:
            data_list = OsTools.csv_read(file_path=file_path)
            OsTools.file_remove(file_path)
        except Exception as err:
            raise RuntimeError(f'报表文件解析出错: {err}') from err

        return data_list

    def download__goods_profit__to_finance(
        self,
        begin_date: str,
        end_date: str,
        is_accrued=False,
        raw=False,
        save_path: str = None,
        save_name: str = None,
        timeout: float = None,
    ):
        """
        下载商品利润数据 (用于财务对商品利润的监控)
        - 筛选条件为按店铺/日期/SKU/预提方案查询数据

        Args:
            begin_date: 开始日期
            end_date: 结束日期
            is_accrued: 是否使用预提方案
            custom_payload: 自定义请求参数
            raw: 如果为 True 则返回文件路径, 否则返回解析后的数据
            save_path: 文件保存的路径
            save_name: 文件保存的名称
            timeout: 请求超时时间
        Returns:
            数据列表或者文件路径
        """

        page = self._get_target_page__byurl(url=Urls.goods_profit)

        payload = {
            'ip': '',
            'page': {'currentPage': 1, 'pageSize': 25},
            'uid': '',
            'coid': '',
            'data': {
                'exportCondition': '{"isAds":false,"condition":{"seachType":0,"shop":[],"act":[],"groupByType":"shop_i_id","groupList":["shop_id","datevalue","sku"],"effective":"nosplit","isShowOnlineSkuName":false,"splitCombine":true,"isShowOtherPromotion":true,"isRefundEstimate":false,"wmsCoidList":[],"buIdList":[],"drpCoidtos":[],"skuIn":{"type":"anyonesku","values":[],"select":"in"},"skuOut":{"type":"anyonesku","values":[],"select":"out"},"labelIn":{"type":"anyonelabel","values":[],"select":"in"},"labelout":{"type":"anyonelabel","values":[],"select":"out"},"creatorList":[],"skuLabelIn":{"type":"anyoneskulabel","values":[],"select":"in"},"skuLabelOut":{"type":"anyoneskulabel","values":[],"select":"out"},"brands":[],"categorys":[],"vcNames":[],"goodsCostGroup":{"skuCostAmountSearchType":{"value":2,"label":"按固定值搜索商品成本"},"value":"","values":["",""]},"dateFld":"send_date","combineDate":["${begin_date_utc}","${end_date_utc}"],"ruleId":${rule_id},"beginDate":"${begin_date}","endDate":"${end_date}","skuGroup":"shop_i_id","orderType":[],"skuCostAmountSearchType":2,"skuCostAmountList":[],"expSkuFee":false,"isOL":true,"isExport":true,"showCsgTypes":["last"],"isExportCond":false,"exportType":"pfsku","dateOrderType":null,"indexPerferUnType":"pfskuprofit_normal_report","isShowProption":true,"isCrossBorder":false}}'
            },
            'ssProjectType': 'SS',
            'ssClientType': 'Web',
        }

        begin_date_utc, end_date_utc = self.__generate__combine_date(
            begin_date, end_date
        )
        variable_table = {
            'rule_id': 22017 if is_accrued is True else 19694,
            'begin_date': begin_date,
            'end_date': end_date,
            'begin_date_utc': begin_date_utc,
            'end_date_utc': end_date_utc,
        }
        payload['data']['exportCondition'] = CommonTools.str_replace_by_variables(
            variable_table, payload['data']['exportCondition']
        )

        return self.download__goods_profit_report(
            payload=payload,
            raw=raw,
            save_path=save_path,
            save_name=save_name,
            timeout=timeout,
            page=page,
        )
