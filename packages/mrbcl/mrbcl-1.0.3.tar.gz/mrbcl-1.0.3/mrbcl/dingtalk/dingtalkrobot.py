import hmac
import hashlib
import base64
import urllib.parse
import requests
from typing import Dict, Optional, List

class DingTalkRobot:
    def __init__(self, webhook: str, secret: Optional[str] = None, keyword: Optional[str] = None):
        """
        初始化钉钉机器人

        :param webhook: 钉钉机器人的Webhook地址
        :param secret: 加签密钥，可选
        :param keyword: 消息关键字，可选
        """
        self.webhook = webhook
        self.secret = secret
        self.keyword = keyword
        # 钉钉默认打开链接方式
        self.default_open_url = "dingtalk://dingtalkclient/page/link?url="

    def _generate_sign(self) -> str:
        """
        生成加签签名

        :return: 签名后的URL参数
        """
        if not self.secret:
            return ""
        import time
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f'&timestamp={timestamp}&sign={sign}'

    def _send_request(self, data: Dict) -> Dict:
        """
        发送请求到钉钉机器人

        :param data: 请求数据
        :return: 响应结果
        """
        url = self.webhook + self._generate_sign()
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'errcode': -1, 'errmsg': str(e)}

    def send_text(self, content: str, at_mobiles: Optional[list] = None, at_user_ids: Optional[list] = None, is_at_all: bool = False) -> Dict:
        """
        发送文本消息

        :param content: 消息内容, 如需@人，需在内容中包含@mobild/@userid
        :param at_mobiles: 被@人的手机号列表，可选
        :param at_user_ids: 被@人的用户ID列表, 可选
        :param is_at_all: 是否@所有人，可选
        :return: 响应结果
        """
        if self.keyword and self.keyword not in content:
            content = f"{self.keyword} {content}"
        
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_user_ids or [],
                "isAtAll": is_at_all
            }
        }
        return self._send_request(data)

    def send_link(self, title: str, text: str, message_url: str, pic_url: str = "", pc_slide: bool = True) -> Dict:
        """
        发送链接消息

        :param title: 消息标题
        :param text: 消息内容
        :param message_url: 点击消息跳转的URL
        :param pic_url: 图片URL, 可选
        :param pc_slide: 链接打开方式, true为pc客户端侧边栏打开, false为外部浏览器打开, 默认为true
        :return: 响应结果
        """
        if self.keyword and self.keyword not in text:
            text = f"{self.keyword} {text}"
        
        # 对链接进行编码
        encoded_url = urllib.parse.quote_plus(message_url)
        # 拼接完整的URL
        encoded_url = f"{self.default_open_url}{encoded_url}&pc_slide={str(pc_slide).lower()}"
        
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": encoded_url
            }
        }
        return self._send_request(data)

    def send_markdown(self, title: str, text: str, at_mobiles: Optional[list] = None, at_user_ids: Optional[list] = None, is_at_all: bool = False) -> Dict:

        """
        发送Markdown消息

        :param title: 消息标题
        :param text: Markdown格式的消息内容, 如需@人，需在内容中包含@mobild/@userid
        :param at_mobiles: 被@人的手机号列表，可选
        :param at_user_ids: 被@人的用户ID列表, 可选
        :param is_at_all: 是否@所有人，可选
        :return: 响应结果
        """
        if self.keyword and self.keyword not in text:
            text = f"{self.keyword} {text}"
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_user_ids or [],
                "isAtAll": is_at_all
            }
        }
        return self._send_request(data)

    def send_action_card(self, title: str, text: str, single_title: str, single_url: str, pc_slide: bool = True, btn_orientation: str = "0") -> Dict:
        """
        发送整体跳转ActionCard消息

        :param title: 消息标题
        :param text: Markdown格式的消息内容, 如需@人，需在内容中包含@UserID
        :param single_title: 单个按钮的标题
        :param single_url: 单个按钮的跳转链接
        :param pc_slide: 链接打开方式, true为pc客户端侧边栏打开, false为外部浏览器打开, 默认为true
        :param btn_orientation: 按钮排列方式, 0: 垂直排列, 1: 水平排列, 默认为0
        :return: 响应结果
        """
        if self.keyword and self.keyword not in text:
            text = f"{self.keyword} {text}"
        
        # 对链接进行编码
        encoded_url = urllib.parse.quote_plus(single_url)
        # 拼接完整的URL
        encoded_url = f"{self.default_open_url}{encoded_url}&pc_slide={str(pc_slide).lower()}"

        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "singleTitle": single_title,
                "singleURL": encoded_url,
                "btnOrientation": btn_orientation
            }
        }
        return self._send_request(data)

    def send_action_card_btns(self, title: str, text: str, btns: List[Dict[str, str]], pc_slide: bool = True, btn_orientation: str = "0") -> Dict:
        """
        发送独立跳转ActionCard消息

        :param title: 消息标题
        :param text: Markdown格式的消息内容, 如需@人，需在内容中包含@UserID
        :param btns: 按钮列表，每个元素为字典，包含 "title" 和 "actionURL" 键
        :param pc_slide: 链接打开方式, true为pc客户端侧边栏打开, false为外部浏览器打开, 默认为true
        :param btn_orientation: 按钮排列方式, 0: 垂直排列, 1: 水平排列, 默认为0
        :return: 响应结果
        """
        if self.keyword and self.keyword not in text:
            text = f"{self.keyword} {text}"
        # 对按钮链接进行编码
        for btn in btns:
            url = urllib.parse.quote_plus(btn['actionURL'])
            # 拼接完整的URL
            btn['actionURL'] = f"{self.default_open_url}{url}&pc_slide={str(pc_slide).lower()}"

        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btns": btns,
                "btnOrientation": btn_orientation
            }
        }
        return self._send_request(data)

    def send_feed_card(self, links: List[Dict[str, str]], pc_slide: bool = True) -> Dict:
        """
        发送FeedCard消息

        :param links: 链接列表，每个元素为字典，包含 "title"、"messageURL" 和 "picURL" 键
        :param pc_slide: 链接打开方式, true为pc客户端侧边栏打开, false为外部浏览器打开, 默认为true
        :return: 响应结果
        """
        for link in links:
            if self.keyword and self.keyword not in link.get('title', ''):
                link['title'] = f"{self.keyword} {link.get('title', '')}"
            # 对链接进行编码
            encoded_url = urllib.parse.quote_plus(link['messageURL'])
            # 拼接完整的URL
            link['messageURL'] = f"{self.default_open_url}{encoded_url}&pc_slide={str(pc_slide).lower()}"
        
        data = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": links
            }
        }
        return self._send_request(data)
