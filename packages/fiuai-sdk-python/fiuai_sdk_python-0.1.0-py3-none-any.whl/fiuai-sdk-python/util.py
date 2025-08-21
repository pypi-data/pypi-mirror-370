# -- coding: utf-8 --
# Project: frappeclient
# Created Date: 2025 05 Sa
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI



import logging

logger = logging.getLogger(__name__)

TOKENS = None 
CLIENTCONFIG = None

def create_headers(key, secret, user, tenant="", company=""):

    headers = {
        "Fiuai-Internal-Auth": "true",
        "Fiuai-Internal-Key": key,
        "Fiuai-Internal-Secret": secret,
        "Fiuai-Internal-User": user,
        "Fiuai-Internal-Tenant": tenant,
        "Fiuai-Internal-Company": company,
        "Accept": "application/json",
    }

    return headers

