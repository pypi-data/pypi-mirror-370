# -- coding: utf-8 --
# Project: fiuaiclient
# Created Date: 2025 06 Tu
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

from pydantic import BaseModel, Field
from .client import FrappeClient
from logging import getLogger
from typing import Literal
from .type import CompanyProfile
from .bank import get_bank_account_by_bank_id

logger = getLogger(__name__)

class TargetCompanySearchResult(BaseModel):
    name: str = Field(description="公司id")
    full_name: str = Field(description="公司全称")
    unique_no: str = Field(description="公司唯一编号")

    exists: bool = Field(description="是否存在", default=False)
    in_network: bool = Field(description="是否在本方网络中", default=False)

    comment: str = Field(description="备注", default="")

def get_target_company_by_name(client: FrappeClient, full_name: str, target_side: Literal["buyer", "seller"]) -> TargetCompanySearchResult:
    """
    根据公司名称获取公司信息
    
    Args:
        full_name: 公司名称
        
    Returns:
        TargetCompanySearchResult: 目标公司信息
    """
    connection_type = "Customer" if target_side == "buyer" else "Supplier"
    
    _lookup = client.get_doc(
        doctype="Company Lookup", 
        fields=["target_company_id", "unique_no"], 
        filters=[["company_name", "=", full_name]])
    if not _lookup:
        logger.debug(f"get_target_company_by_name: {full_name} not found")
        return TargetCompanySearchResult(name="", full_name="", unique_no="", exists=False, in_network=False, comment="该公司不存在")
    
    _lookup = _lookup[0]

    _network = client.get_doc(
        doctype="Company Network", 
        fields=["name", "target_company_id", "target_company"], 
        filters=[["target_company_id", "=", _lookup["target_company_id"]], ["connection_type", "=", connection_type]])
    if not _network:
        logger.debug(f"get_target_company_by_name: {full_name} is not in network")
        return TargetCompanySearchResult(name="", full_name="", unique_no="", exists=True, in_network=False, comment="该公司不在本方网络中")
    
    _network = _network[0]


    n = TargetCompanySearchResult(
            name=_network["target_company_id"], 
            full_name=_network["target_company"], 
            unique_no=_lookup["unique_no"], 
            exists=True, 
            in_network=True, 
            comment="",
        )
    
    return n


def get_company_profile(client: FrappeClient, auth_company_id: str)-> CompanyProfile | None:
    """
    获取公司信息
    """
    resp = client.get_doc(
        doctype="Company",
        filters=[["name", "=", auth_company_id]],
        fields=[
            "name",
            "full_name",
            "abbr",
            "unique_no",
            "company_profile",
            "default_currency",
            "country_region",
            "company_size",
            "entity_type",
            "email",
            "address",
            "default_bank_account",
            "company_contact",
            "email",
            "address",
        ],
    )
    
    if not resp:
        return None

    r = resp[0]
   
    if r["default_bank_account"]:
        rr = get_bank_account_by_bank_id(client, r["default_bank_account"])
        if not rr:
            logger.error(f"get_company_profile: default_bank_account {r['default_bank_account']} not found")
            return None
    else:
        rr = None

    return CompanyProfile(
        name=r["name"],
        full_name=r["full_name"],
        unqiue_no=r["unique_no"],
        default_currency=r["default_currency"],
        country_region=r["country_region"],
        company_size=r["company_size"],
        entity_type=r["entity_type"],
        abbr=r.get("abbr", "") if r.get("abbr", "") else "",
        company_profile=r.get("company_profile", "") if r.get("company_profile", "") else "",
        company_contact=r.get("company_contact", "") if r.get("company_contact", "") else "",
        email=r.get("email", "") if r.get("email", "") else "",
        address=r.get("address", "") if r.get("address", "") else "",
        default_bank_account=rr,
    )