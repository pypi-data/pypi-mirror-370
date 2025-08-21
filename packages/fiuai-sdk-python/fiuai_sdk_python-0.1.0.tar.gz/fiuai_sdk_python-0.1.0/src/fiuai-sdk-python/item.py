# -- coding: utf-8 --
# Project: fiuaiclient
# Created Date: 2025 05 Sa
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .setup import get_client


class Item(BaseModel):
    """
    商品信息
    """
    name: str = Field(description="商品id")
    item_code: str = Field(description="商品编码")
    item_name: str = Field(description="商品名称")
    stock_uom: str = Field(description="计量单位")
    description: str = Field(description="商品描述", default="")


def load_item_data(auth_tenant_id: str, auth_company_id: str)-> List[Item]:
    """
    从frappe获取item数据
    """
    with get_client() as client:
        client.swith_company(auth_tenant_id, auth_company_id)
        item_list = client.get_list(
            doctype="Item", 
            filters=[
                ["disabled", "=", 0],
                ["auth_tenant_id", "=", auth_tenant_id],
                ["auth_company_id", "=", auth_company_id]
            ],
            fields=["name", "item_code", "item_name", "stock_uom", "description"]
            )
        return [Item(name=item["name"], item_code=item["item_code"], item_name=item["item_name"], stock_uom=item["stock_uom"], description=item["description"] if item["description"] else "") for item in item_list]
