import requests
import json
from config_loader import Config
from ql_api import QL
from utils import *
from logger_init import logger_init
import random
import time
from datetime import datetime

logger = logger_init()


class ThreatbookAuto:
    def __init__(self):
        self.config = Config.from_json('config.json')
        self.COOKIE = self.get_threatbook_cookie()
        self.x_csrf_token = get_csrf_token(self.COOKIE)[0]
        self.xx_csrf = get_csrf_token(self.COOKIE)[1]
        self.session = requests.Session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Content-Type': 'application/json',
            'Cookie': self.COOKIE,
            'Origin': self.config.TASK.TARGET_BASE_URL,
            'Referer': self.config.TASK.TARGET_BASE_URL,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.87'
                          'Safari/537.36 SE 2.X MetaSr 1.0',
            'X-CSRF-Token': self.x_csrf_token,
            'Xx-Csrf': self.xx_csrf
        }

    def get_threatbook_cookie(self):
        address = f"{self.config.QL_SERVER_IP}:{self.config.QL_SERVER_PORT}"
        client_id = self.config.QL_APP_CLIENT_ID
        client_secret = self.config.QL_APP_CLIENT_SECRET
        ql = QL(address, client_id, client_secret)
        envs = ql.getEnvs()
        for env in envs:
            if env['name'] == 'threatbook_cookie' and env['status'] == 0:
                return env['value']
        return ""

    def get_article_data(self):
        article_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.ARTICLE.PATH
        page = 1
        last_threat_id = ''
        article_list = []
        like_list = []
        follow_list = []
        logger.info('开始获取主页数据...')
        # 获取主页数据
        while True:
            # 必选参数
            params = {
                'classify': 'all',
                'page': page,
                'pageSize': 10
            }
            if last_threat_id:
                params['lastThreatId'] = last_threat_id
            response = self.session.get(article_api, params=params)
            res_data = response.json()['data']

            if not res_data:
                break  # 如果没有返回数据，则退出循环

            # 检查每次获取的数据长度
            logger.info(f"正在浏览第 {page} 页, 获取了 {len(res_data)} 个数据")

            # 更新 last_threat_id 和 article_list
            last_threat_id = res_data[-1]['articleInfo']['bid']
            article_list.extend(res_data)  # 确保加入整个 res_data

            # 更新待点赞文章列表和待关注用户列表
            for article in res_data:
                if not article['articleInfo']['praised'] and len(like_list) < 15:
                    like_list.append(article['articleInfo']['threatId'])

                user_id = article['userInfo']['userId']
                user_data = self.get_user_data(user_id)
                if not user_data['data']['isFollowed'] and len(follow_list) < 5:
                    follow_list.append({
                        'user_id': user_id,
                        'user_name': user_data['data']['userName']
                    })

                # 如果两个列表都达到目标长度，退出循环
                if len(like_list) >= 15 and len(follow_list) >= 5:
                    break

            # 检查article_list中待点赞文章数和待关注用户数够不够
            if len(like_list) >= 15 and len(follow_list) >= 5:
                break

            page += 1

            sleep_time = random.uniform(0.1, 1)
            time.sleep(sleep_time)

        return article_list, like_list, follow_list

    def get_user_data(self, user_id: str):
        user_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.USER.PATH + user_id
        response = self.session.get(user_api)
        return response.json()

    def get_my_info(self):
        my_info_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.MY_INFO.PATH
        response = self.session.get(my_info_api)
        if response.json()['response_code'] == 0 and response.json()['verbose_msg'] == 'succeed':
            return response.json().get('data')
        else:
            return None

    def get_level_info(self):
        level_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.LEVEL.PATH
        my_info = self.get_my_info()
        response = self.session.get(level_api)
        if response.json()['response_code'] == 0 and response.json()['verbose_msg'] == 'succeed':
            logger.info(f"您的账号：{my_info.get('nickName')} | 当前等级：{response.json()['data']['level']} | 总成长值：{response.json()['data']['total']}")
        else:
            logger.error(f'等级信息获取失败：{response.json()}')

    def get_point_info(self):
        point_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.POINT.PATH
        page = 0
        today_point_list = []
        # 获取当前日期
        today_date = datetime.now().strftime("%Y-%m-%d")
        logger.info('正在获取今日成长值信息...')
        while True:
            params = {
                'page': page
            }
            response = self.session.get(point_api, params=params)
            data = response.json().get('point_list', [])
            if response.json().get('response_code') != 0 or not data:
                logger.info('没有更多数据或请求失败')
                break

            # 遍历当前页的数据
            for item in data:
                if item['ctime'].startswith(today_date):
                    today_point_list.append(item)
                else:
                    # 如果遇到不是当天的元素，结束循环
                    break

            # 如果当前页所有元素都是当天的，继续下一页
            page += 1

        today_point_list.reverse()
        today_total_point = 0
        # 创建一个字典来存储统计结果
        stats = {}
        logger.info("今日成长值信息获取成功！")
        for item in today_point_list:
            action = item["actionDesc"]
            point = item["point"]
            if action not in stats:
                stats[action] = {
                    "count": 0,
                    "total_points": 0
                }
            stats[action]["count"] += 1
            stats[action]["total_points"] += point

            logger.info(f"时间：{item['ctime']} | 成长值说明：{item['actionDesc']} | 成长值：{'+' if item['point'] > 0 else '' }{item['point']}")
            today_total_point += item['point']

        # 动态生成日志内容
        details = []
        for action, summary in stats.items():
            details.append(f"{action}×{summary['count']}：{'+' if summary['total_points'] > 0 else ''}{summary['total_points']}")

        # 将细节拼接成字符串
        details_str = " | ".join(details)

        # 打印格式化的日志信息
        logger.info(f"今日获取总成长值：{today_total_point} | {details_str}")

    def login(self):
        """
        每日登录 +10成长值
        """
        logger.info('开始登录...')
        article_data_list, like_list, follow_list = self.get_article_data()
        logger.info('登录成功！')
        return article_data_list, like_list, follow_list

    def like(self, like_list):
        """
        每日点赞文章 +5成长值/篇
        限制：每日最多加10篇点赞分
        """
        logger.info('开始点赞...')
        for index, article_id in enumerate(like_list):
            like_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.LIKE.PATH
            like_data = {
                'id': f'{article_id}',
                'option': self.config.TASK.API.LIKE.PARAMS.option.like
            }
            response = self.session.post(like_api, data=json.dumps(like_data))
            if response.json()['response_code'] == 0 and response.json()['verbose_msg'] == 'OK':
                if index < 10:
                    logger.info(f"点赞成功{index + 1}/{len(like_list)}：文章id {article_id} +5成长值")
                else:
                    logger.info(f"点赞成功{index + 1}/{len(like_list)}：文章id {article_id} 今日点赞成长值已达上限")
            else:
                logger.error(f"点赞失败{index + 1}/{len(like_list)}：文章id {article_id}, {response.json()}")
            sleep_time = random.uniform(0.5, 2)
            time.sleep(sleep_time)

    def follow(self, follow_list):
        """
        每日关注用户 +5成长值/人
        限制：每日最多加3人分
        """
        logger.info('开始关注...')
        for index, user in enumerate(follow_list):
            user_id = user['user_id']
            user_name = user['user_name']
            follow_api = self.config.TASK.TARGET_BASE_URL + self.config.TASK.API.FOLLOW.PATH + user_id
            params = {
                'operation': self.config.TASK.API.FOLLOW.PARAMS.operation.follow
            }
            response = self.session.get(follow_api, params=params)
            if response.json()['response_code'] == 0 and response.json()['verbose_msg'] == 'OK':
                if index < 3:
                    logger.info(f"关注成功{index + 1}/{len(follow_list)}：{user_name} +5成长值")
                else:
                    logger.info(f"关注成功{index + 1}/{len(follow_list)}：{user_name} 今日关注成长值已达上限")
            else:
                logger.error(f"关注失败{index + 1}/{len(follow_list)}：{user_name}, {response.json()}")
            sleep_time = random.uniform(0.5, 2)
            time.sleep(sleep_time)

    def run(self):
        article_data_list, like_list, follow_list = self.login()
        self.like(like_list)
        self.follow(follow_list)
        logger.info('任务完成！')
        logger.info('-----------------------------------------------------------------')
        self.get_point_info()
        self.get_level_info()

    def test(self):
        self.get_point_info()
        self.get_level_info()


if __name__ == "__main__":
    auto = ThreatbookAuto()
    auto.run()
