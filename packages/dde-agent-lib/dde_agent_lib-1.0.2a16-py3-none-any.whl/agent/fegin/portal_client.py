import requests


class PortalClient:

    def __init__(self, logger, portal_address, system_config):
        self.logger = logger
        self.portal_address = portal_address
        self.chatdetail_url = system_config['feign']['portal']['chatdetail_url']

    def get_chat_detail(self, sessionId: str):
        """
        获取历史聊天信息
        """
        url = f"{self.portal_address}{self.chatdetail_url}"
        with requests.Session() as session:
            response = session.get(url, params={"sessionId": sessionId}, timeout=5)
            chat_detail = response.json()
            return chat_detail
