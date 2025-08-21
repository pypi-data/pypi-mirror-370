# -- coding: utf-8 --
# Project: fiuaiapp
# Created Date: 2025 05 Tu
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI


import psycopg2
import os
from pydantic import BaseModel
from typing import Dict

from config.config import get_settings
settings = get_settings()


class TokenConfig(BaseModel):
    user: str
    key: str
    secret: str

class Tokens(BaseModel):
    configs: Dict[str, TokenConfig] = {}

    def __init__(self):
        super().__init__()
        self.load_tokens()
        self.validate_tokens()
        
        
    def validate_tokens(self):
        for u, t in self.configs.items():
            if t.key == "":
                raise ValueError(f"Token key is not set for user {u}")
            if t.secret == "":
                raise ValueError(f"Token secret is not set for user {u}")

    def load_tokens(self):
        self.configs = {
            settings.FIUAI_USER: TokenConfig(
                user=settings.FIUAI_USER,
                key=settings.FIUAI_KEY,
                secret=settings.FIUAI_SECRET,
            )
        }
        
        # try:
        #     c = _connect_db()
        #     cursor = c.cursor()
        #     try:
        #         cursor.execute("""SELECT name, fieldname, password FROM "__Auth" 
        #                        WHERE doctype = 'fiuai_internal' 
        #                        """)
                
        #         for row in cursor:
        #             user = row[0]
        #             if user not in self.configs:
        #                 self.configs[user] = TokenConfig(user=user, key="", secret="")

        #             if row[1] == 'key':
        #                 self.configs[user].key = row[2]
        #             elif row[1] == 'secret':
        #                 self.configs[user].secret = row[2]
        #     finally:
        #         cursor.close()
        #         c.close()
        # except Exception as e:
        #     raise e
        
    def validate_token(self, user: str, key: str, secret: str) -> bool:
        if user not in self.configs:
            return False
        token = self.configs[user]
        return token.key == key and token.secret == secret
            
    def get(self, user: str) -> TokenConfig:
        if user not in self.configs:
            raise KeyError(f"User {user} not found in tokens")
        return self.configs[user]

# def _connect_db():
#     # 连接到数据库, 不能使用配置对象Config
#     connection = psycopg2.connect(
#         user=os.getenv("DB_USER", "dev"),
#         password=os.getenv("DB_PASS", "dev"),
#         host=os.getenv("DB_HOST", "localhost"),
#         port=int(os.getenv("DB_PORT", "5432")),
#         database=os.getenv("DB_NAME", "dev")
#     )

#     return connection