# -- coding: utf-8 --
# Project: fiuaiapp
# Created Date: 2025 05 Tu
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

# const
AI_ALLOWED_DOCTYPE_META = [
    "Contract", 
    "Contract Item", 
    "Bank Transaction",
    "Bank Statement",
    # "invoice"
    ]
USED_COUNTRY_LIST =  ["China", "United States", "Japan", "Thailand", "India", "Indonesia", "Malaysia", "Philippines", "Singapore", "South Korea", "United Kingdom", "Vietnam"]
USED_LANGUAGE_LIST = ["zh", "en", "ja", "th", "id", "ms", "ph", "sg", "kr", "uk", "vn"]
from .type import (
    UOM, 
    Currency, 
    Country,
    Language,
    DocTypeMeta,
    DocField,
    AiRecognitionValue
)
from typing import List
from logging import getLogger

from .client import FrappeClient
from .util import get_token

logger = getLogger(__name__)


def get_client(username: str="assistant@fiuai.com")-> FrappeClient:
    """
    获取frappe client
    """
    return FrappeClient(username)

async def aget_client(username: str="assistant@fiuai.com")-> FrappeClient:
    """
    获取frappe client
    """
    return FrappeClient(username)

def load_uom_data()-> List[UOM]:
    """
    从frappe获取uom数据
    """
    with get_client() as client:
        uom_list = client.get_list(doctype="UOM", fields=["name", "uom_name", "common_code"])
        return [UOM(name=uom["name"], uom_name=uom["uom_name"], common_code=uom["common_code"]) for uom in uom_list]

def load_currency_data()-> List[Currency]:
    """
    从frappe获取currency数据
    """
    with get_client() as client:
        currency_list = client.get_list(
            doctype="Currency", 
            filters={"enabled": 1},
            fields=["name", "currency_name", "fraction_units", "smallest_currency_fraction_value"]
            )
        return [Currency(name=currency["name"], currency_name=currency["currency_name"], fraction_units=currency["fraction_units"], smallest_currency_fraction_value=currency["smallest_currency_fraction_value"]) for currency in currency_list]

def load_country_data()-> List[Country]:
    """
    从frappe获取country数据
    """
    with get_client() as client:
        country_list = client.get_list(
            doctype="Country", 
            filters={"name": ["in", USED_COUNTRY_LIST]},
            fields=["name", "code"]
        )
        return [Country(name=country["name"], code=country["code"]) for country in country_list]

def load_language_data()-> List[Language]:
    """
    从frappe获取language数据
    """
    with get_client() as client:
        language_list = client.get_list(
            doctype="Language", 
            filters={"name": ["in", USED_LANGUAGE_LIST]},
            fields=["name", "language_name"]
        )
        return [Language(name=language["name"], language_name=language["language_name"]) for language in language_list]

def load_doctype_meta(doctype: str, max_api_retry: int = 3)-> DocTypeMeta:
    """
    从frappe获取doctype数据
    """

    retry_count = 0
    doc_meta = None
    while retry_count < max_api_retry:
            
        doc_meta = _get_meta(doctype=doctype)
        
        if doc_meta:
            break
        else:
            retry_count += 1
           
    return doc_meta        

def _get_meta(doctype: str) -> DocTypeMeta:
    try:
        with get_client() as client:
            m = client.get_meta(doctype)
            
            if m is None:
                return None

            _fields = []
            links = []
            child_docs = []
            for _f in m["fields"]:
                field_name = _f["fieldname"]
                field_type = _f["fieldtype"]
                field_prompt = _f.get("field_prompt", "")
                options_str = _f.get("options", "")
                hidden = _f.get("hidden", 0)
                reqd = _f.get("reqd", 0)
                read_only = _f.get("read_only", 0)

                options = []
                match field_type:
                    case "Select":
                        options = options_str.split("\n")
                    case "Link":
                        links.append(options_str)
                        options.append(options_str)
                    case "Table":
                        child_docs.append(options_str)
                        options.append(options_str) 
                    case _:
                        pass


                if field_prompt == "":
                    # 仅有prompt的field才是应该关心的字段，降低复杂度
                    continue
                if hidden == 1:
                    continue
                
                
                _fields.append(DocField(
                    fieldname=field_name, 
                    fieldtype=field_type, 
                    hidden=True if _f.get("hidden", 0) == 1 else False,
                    read_only=True if _f.get("read_only", 0) == 1 else False,
                    reqd=True if _f.get("reqd", 0) == 1 else False,
                    options=options,
                    field_prompt=field_prompt,
                    ai_recognition_value=AiRecognitionValue(value=None, confidence=0, ai_comment="")
                ))
            
            # links, child 去重
            links = list(set(links))
            child_docs = list(set(child_docs))

            doc_meta = DocTypeMeta(
                    name=doctype, 
                    doctype_prompts=m["doctype_prompts"], 
                    fields=_fields,
                    link_docs=links,
                    child_docs=child_docs
                )
            return doc_meta
    except Exception as e:
        logger.error(f"load doctype meta failed: {e.args}")
        return None
        
        
def load_all_allowed_doctype_meta()-> List[DocTypeMeta]:
    """
    从frappe获取doctype数据
    """
    r = []
    for _d in AI_ALLOWED_DOCTYPE_META:
        m = load_doctype_meta(_d)
        r.append(m)
    return r
