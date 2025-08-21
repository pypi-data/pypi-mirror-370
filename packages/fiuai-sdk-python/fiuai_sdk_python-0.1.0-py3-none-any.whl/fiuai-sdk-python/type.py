# -- coding: utf-8 --
# Project: fiuaiapp
# Created Date: 2025 05 Tu
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI


from pydantic import BaseModel, Field, create_model, validator
from typing import List, Any, Literal, Dict, Optional, Union, Type
from datetime import datetime
import json
import re

class UserProfile(BaseModel):
    name: str = Field(description="用户名称")
    full_name: str = Field(description="用户全名")
    email: str = Field(description="用户邮箱")
    roles: List[str] = Field(description="用户角色")
    auth_tenant_id: str = Field(description="用户租户")
    default_company_id: str = Field(description="用户默认公司", default="")
    phone: str = Field(description="用户电话", default="")


class ClientConfig(BaseModel):
    url: str
    max_api_retry: int
    verify: bool

class UOM(BaseModel):
    """
    frappe UOM文档数据
    """
    name: str = Field(description="UOM ID")
    uom_name: str = Field(description="uom描述")
    common_code: str = Field(description="uom通用代码")
    
    
    
class Currency(BaseModel):
    """
    frappe 货币文档数据
    """
    name: str = Field(description="货币ID,使用标准的ISO 4217货币代码, 比如CNY")
    currency_name: str = Field(description="货币描述，一般和name一致")
    fraction_units: int = Field(description="小数位数")
    smallest_currency_fraction_value: float = Field(description="最小货币面值,比如0.01代表最小的面值是1分")


class Country(BaseModel):
    """
    frappe 国家文档数据
    """
    name: str = Field(description="国家英文名称,比如China")
    code: str = Field(description="国家ID,使用标准的ISO 3166-1国家代码, 比如cn")

class Language(BaseModel):
    """
    frappe 语言文档数据
    """
    name: str = Field(description="语言ID,使用标准的ISO 639-1语言代码, 比如zh")
    language_name: str = Field(description="语言名称,比如简体中文, Melayu, 日本語")


class AiRecognitionValue(BaseModel):
    """
    frappe 文档字段的AI识别值格式, 用于AI识别后返回的值
    """
    value: Any = Field(description="字段值")
    confidence: float = Field(description="字段识别的置信度, 0-1", default=0)
    ai_comment: str = Field(description="ai识别的备注", default="")
    editable: bool = Field(description="用户是否可以更改", default=False)


class DocField(BaseModel):
    """
    frappe 文档字段文档数据
    """
    fieldname: str = Field(description="字段名称,比如Invoice,Purchase Order,etc.")
    hidden: bool = Field(description="字段是否隐藏")
    reqd: bool = Field(description="字段是否必填")
    read_only: bool = Field(description="字段是否只读")
    fieldtype: str = Field(description="字段类型,比如Data,Float,Link,etc.")
    options: List[str] = Field(description="字段选项,Select类型的字段的枚举值, Link类型字段的Link目标表名")
    field_prompt: str = Field(description="字段对应的prompt")
    # ai_recognition_value: AiRecognitionValue = Field(description="字段对应的AI识别结果", default=None)


##### company doc type #####

class BankAccount(BaseModel):
    name: str = Field(description="银行账号名称")
    bank: str = Field(description="银行名称", default="")
    bank_branch: str = Field(description="银行分支机构", default="")
    account_name: str = Field(description="银行账号", default="")
    bank_account_no: str = Field(description="银行账号")


class CompanyProfile(BaseModel):
    name: str = Field(description="公司名称")
    full_name: str = Field(description="公司全称")
    unqiue_no: str = Field(description="公司唯一编号")

    default_currency: str = Field(description="默认货币")
    country_region: str = Field(description="国家/地区")
    company_size: str = Field(description="公司规模")
    entity_type: str = Field(description="实体类型")
    
    abbr: str = Field(description="公司简称", default="")
    company_profile: str = Field(description="公司简介", default="")

    company_contact: str = Field(description="公司联系人", default="")
    email: str = Field(description="公司联系邮箱", default="")
    address: str = Field(description="公司联系地址", default="")

    default_bank_account: BankAccount|None = Field(description="公司银行名称", default=None)
    bank_accounts: List[BankAccount] = Field(description="公司银行账号", default=[])



##### other type #####

class DocTypeMeta(BaseModel):
    """
    frappe 文档类型文档数据
    """
    name: str = Field(description="文档类型名称,比如Invoice,Purchase Order,etc.")
    doctype_prompts: str = Field(description="文档类型对应的prompt")
    fields: List[DocField] = Field(description="文档类型所有的字段配置", default_factory=list)
    link_docs: List[str] = Field(description="文档类型包含的所有Link文档类型", default_factory=list)
    child_docs: List[str] = Field(description="文档类型包含的所有Child文档类型", default_factory=list)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def get_all_fields(self)-> List[DocField]:
        """返回所有字段"""
        return self.fields
    
    def get_normal_fields(self)-> List[DocField]:
        """返回第一层field"""
        r = []
        for field in self.fields:
            if field.fieldtype not in ["Link", "Table", "Dynamic Link"] and field.field_prompt != "":
                r.append(field)
        return r
    
    def get_link_fields(self)-> List[DocField]:
        """返回link类型的field"""
        r = []
        for field in self.fields:
            if field.fieldtype == "Link" and field.field_prompt != "":
                r.append(field)
        return r
    
    def get_all_fields_prompt(self, simple: bool=False) -> List[str]:
        r = []
        for i in self.fields:
            if simple:
                r.append(f"Field: {i.fieldname}, Type: {i.fieldtype}, option: {i.options}, Prompt: {i.field_prompt}")
            else:
                r.append(i.model_dump_json())
        return r
    
    def create_empty_data_json(self, mock_type: Literal["full", "json"]="json", with_child_tables: bool = False) -> str:
        return json.dumps(self.create_empty_data(mock_type, with_child_tables), indent=4)

    def create_empty_data(self, mock_type: Literal["full", "json"]="json", with_child_tables: bool = False, is_child_table: bool = False) -> Dict[str, Any]:
        """
        创建一个空的文档数据，根据字段类型返回对应的空值
        Args:
            mock_type: 返回数据的格式类型，"json"或"full"
            with_child_tables: 是否自动加载子表元数据并创建子表数据
        Returns:
            dict: 包含所有字段的空值
        """
        default_full_value = {
            "ai_comment": "",
            "confidence": 0.01,
            "editable": False
        }
        r = {}

        for field in self.fields:
            v = default_full_value.copy()

            if field.field_prompt == "":
                continue
                
            if field.fieldtype == "Link":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Table":
                # 处理子表类型，递归创建子表数据并附上1条示例数据
                child_table_data = []
                
                if field.options and len(field.options) > 0:
                    child_doctype = field.options[0]
                    if with_child_tables:
                        try:
                            # 动态导入避免循环依赖
                            from pkg.fiuaiclient .setup import load_doctype_meta
                            # 自动加载子表元数据
                            child_meta = load_doctype_meta(child_doctype)
                            if child_meta:
                                # 递归创建子表的空数据
                                child_data = child_meta.create_empty_data(mock_type, with_child_tables)
                                # 为子表添加基础字段
                                child_data["idx"] = 1 if mock_type == "json" else {
                                    "value": 1, 
                                    "ai_comment": "子表行索引", 
                                    "confidence": 1.0, 
                                    "editable": False
                                }
                                child_data["name"] = f"row_1_{child_doctype.lower()}" if mock_type == "json" else {
                                    "value": f"row_1_{child_doctype.lower()}", 
                                    "ai_comment": "子表行名称", 
                                    "confidence": 1.0, 
                                    "editable": False
                                }
                                child_table_data = [child_data]
                            else:
                                # 如果加载失败，创建基础的子表行
                                child_table_data = self._create_basic_child_data(child_doctype, mock_type)
                        except Exception as e:
                            # 如果加载元数据失败，创建基础的子表行
                            child_table_data = self._create_basic_child_data(child_doctype, mock_type)
                    else:
                        # 如果不需要加载子表元数据，创建基础的子表行
                        child_table_data = self._create_basic_child_data(child_doctype, mock_type)
                
                v.update({"value": child_table_data})
                r[field.fieldname] = child_table_data if mock_type == "json" else v
            elif field.fieldtype == "Dynamic Link":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Float":
                v.update({"value": 0.0})
                r[field.fieldname] = 0.0 if mock_type == "json" else v
            elif field.fieldtype == "Int":
                v.update({"value": 0})
                r[field.fieldname] = 0 if mock_type == "json" else v
            elif field.fieldtype == "Check":
                v.update({"value": 0})
                r[field.fieldname] = 0 if mock_type == "json" else v
            elif field.fieldtype == "Select":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Date":
                v.update({"value": datetime.now().strftime("%Y-%m-%d")})
                r[field.fieldname] = datetime.now().strftime("%Y-%m-%d") if mock_type == "json" else v
            elif field.fieldtype == "Datetime":
                v.update({"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                r[field.fieldname] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if mock_type == "json" else v
            elif field.fieldtype == "Time":
                v.update({"value": datetime.now().strftime("%H:%M:%S")})
                r[field.fieldname] = datetime.now().strftime("%H:%M:%S") if mock_type == "json" else v
            elif field.fieldtype == "Text":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Long Text":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Attach":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Attach Image":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Color":
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v
            elif field.fieldtype == "Currency":
                v.update({"value": 0.0})
                r[field.fieldname] = 0.0 if mock_type == "json" else v
            elif field.fieldtype == "Percent":
                v.update({"value": 0.0})
                r[field.fieldname] = 0.0 if mock_type == "json" else v
            else:
                v.update({"value": ""})
                r[field.fieldname] = "" if mock_type == "json" else v

        if not is_child_table:
            r["doctype"] = self.name if mock_type == "json" else {
                "value": self.name,
                "ai_comment": "",
                "confidence": 0.01,
                "editable": False
            }
        
        return r
    
    def _create_basic_child_data(self, child_doctype: str, mock_type: Literal["full", "json"] = "json") -> List[Dict[str, Any]]:
        """
        创建基础的子表行数据
        Args:
            child_doctype: 子表文档类型
            mock_type: 返回数据的格式类型，"json"或"full"
        Returns:
            List[Dict[str, Any]]: 包含1条基础子表行数据的列表
        """
        basic_child_data = {
            "name": f"row_1_{child_doctype.lower()}" if mock_type == "json" else {
                "value": f"row_1_{child_doctype.lower()}", 
                "ai_comment": "子表行名称", 
                "confidence": 1.0, 
                "editable": False
            },
            "idx": 1 if mock_type == "json" else {
                "value": 1, 
                "ai_comment": "子表行索引", 
                "confidence": 1.0, 
                "editable": False
            },
            "doctype": child_doctype if mock_type == "json" else {
                "value": child_doctype, 
                "ai_comment": "子表文档类型", 
                "confidence": 1.0, 
                "editable": False
            }
        }
        return [basic_child_data]
    
    def _get_type_string(self, field_type: Type) -> str:
        """
        获取类型的字符串表示，正确处理Optional类型
        """
        # 检查是否是Optional类型 (Union[T, None])
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            # 获取Union的所有参数
            args = field_type.__args__
            # 如果是Optional[T]，即Union[T, None]
            if len(args) == 2 and type(None) in args:
                # 找到非None的类型
                inner_type = next(arg for arg in args if arg is not type(None))
                return f"Optional[{self._get_type_string(inner_type)}]"
            else:
                # 普通的Union类型
                type_names = [self._get_type_string(arg) for arg in args]
                return f"Union[{', '.join(type_names)}]"
        
        # 检查是否是List类型
        elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            if hasattr(field_type, '__args__') and field_type.__args__:
                inner_type = field_type.__args__[0]
                return f"List[{self._get_type_string(inner_type)}]"
            else:
                return "List"
        
        # 检查是否是Dict类型
        elif hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
            if hasattr(field_type, '__args__') and len(field_type.__args__) >= 2:
                key_type, value_type = field_type.__args__[0], field_type.__args__[1]
                return f"Dict[{self._get_type_string(key_type)}, {self._get_type_string(value_type)}]"
            else:
                return "Dict"
        
        # 普通类型
        else:
            if hasattr(field_type, '__name__'):
                return field_type.__name__
            else:
                return str(field_type)

    def get_pydantic_model(self) -> Type[BaseModel]:
        """
        根据字段类型返回对应的Pydantic模型，支持动态生成包括子表的复杂模型
        """
        field_definitions = {}
        
        # 字段类型映射
        type_mapping = {
            'Data': str,
            'Float': float,
            'Int': int,
            'Check': int,
            'Select': str,
            'Date': str,  # 使用字符串格式存储日期
            'Datetime': str,  # 使用字符串格式存储时间
            'Time': str,
            'Text': str,
            'Long Text': str,
            'Small Text': str,
            'Attach': str,
            'Attach Image': str,
            'Color': str,
            'Currency': float,
            'Percent': float,
            'Link': str,
            'Dynamic Link': str,
            'Password': str,
            'Code': str,
            'HTML': str,
            'JSON': Dict[str, Any],
        }
        
        for field in self.fields:
            if field.field_prompt == "":
                continue
                
            field_name = field.fieldname
            field_type = field.fieldtype
            
            # 获取基础类型
            python_type = type_mapping.get(field_type, str)
            
            # 处理特殊字段类型
            if field_type == "Table":
                # 子表类型，使用List[Dict[str, Any]]
                python_type = List[Dict[str, Any]]
            elif field_type == "Select" and field.options:
                # Select类型保持为str
                python_type = str
            elif field_type == "Check":
                # Check字段可能是0/1或bool
                python_type = int
            elif field_type == "Date":
                # 日期字段
                python_type = str
            elif field_type == "Email":
                # 邮箱字段
                python_type = str
            elif field_type == "Phone":
                # 电话字段  
                python_type = str
            elif field_type == "URL":
                # URL字段
                python_type = str
            
            # 创建字段定义
            field_args = [Field(description=field.field_prompt)]
            
            # 添加字段约束
            if field.reqd:
                # 必填字段
                if field_type in ["Float", "Currency", "Percent"]:
                    field_args[0] = Field(description=field.field_prompt, ge=0)
                elif field_type == "Int":
                    field_args[0] = Field(description=field.field_prompt, ge=0)
                
                field_definitions[field_name] = (python_type, field_args[0])
            else:
                # 可选字段
                if field_type in ["Float", "Currency", "Percent"]:
                    field_args[0] = Field(default=None, description=field.field_prompt, ge=0)
                elif field_type == "Int":
                    field_args[0] = Field(default=None, description=field.field_prompt, ge=0)
                else:
                    field_args[0] = Field(default=None, description=field.field_prompt)
                
                field_definitions[field_name] = (Optional[python_type], field_args[0])
        
        # 添加doctype字段
        field_definitions['doctype'] = (str, Field(default=self.name, description="文档类型"))
        
        # 动态创建模型
        model_name = f"{re.sub(r'[^a-zA-Z0-9]', '', self.name)}Model"
        
        # 创建基础模型
        dynamic_model = create_model(
            model_name,
            __base__=BaseModel,
            **field_definitions
        )
        
        return dynamic_model
    
    def create_instance_from_model(self, data: Dict[str, Any] = None, with_child_tables: bool = False) -> BaseModel:
        """
        使用动态生成的模型创建实例
        
        Args:
            data: 用于初始化模型的数据，如果为None则使用空数据
            with_child_tables: 是否自动加载子表元数据并创建子表数据
            
        Returns:
            BaseModel: 动态生成的模型实例
        """
        if data is None:
            data = self.create_empty_data(mock_type="json", with_child_tables=with_child_tables)
        
        DynamicModel = self.get_pydantic_model()
        return DynamicModel(**data)

    def create_json_schema(self, with_child_tables: bool = True) -> Dict[str, Any]:
        """
        创建JSON Schema，基于字段类型和结构
        Args:
            with_child_tables: 是否包含子表结构
        Returns:
            Dict[str, Any]: 标准的JSON Schema
        """
        # 字段类型到JSON Schema类型的映射
        type_mapping = {
            'Data': 'string',
            'Float': 'number', 
            'Int': 'integer',
            'Check': 'integer',  # 0 或 1
            'Select': 'string',
            'Date': 'string',
            'Datetime': 'string', 
            'Time': 'string',
            'Text': 'string',
            'Long Text': 'string',
            'Small Text': 'string',
            'Attach': 'string',
            'Attach Image': 'string',
            'Color': 'string',
            'Currency': 'number',
            'Percent': 'number',
            'Link': 'string',
            'Dynamic Link': 'string',
            'Password': 'string',
            'Code': 'string',
            'HTML': 'string',
            'JSON': 'object',
            'Table': 'array'  # 子表类型
        }
        
        properties = {}
        required_fields = []
        
        # 处理所有字段
        for field in self.fields:
            if field.field_prompt == "":
                continue
                
            field_name = field.fieldname
            field_type = field.fieldtype
            
            # 获取JSON Schema类型
            json_type = type_mapping.get(field_type, 'string')
            
            # 创建字段的schema定义
            field_schema = {
                "type": json_type,
                "description": field.field_prompt
            }
            
            # 处理特殊字段类型
            if field_type == "Select" and field.options:
                # Select类型添加枚举选项
                field_schema["enum"] = [opt for opt in field.options if opt.strip() != ""]
                if len(field_schema["enum"]) == 0:
                    del field_schema["enum"]
            
            elif field_type == "Check":
                # Check字段限制为0或1
                field_schema["minimum"] = 0
                field_schema["maximum"] = 1
            
            elif field_type in ["Float", "Currency", "Percent"]:
                # 数值类型添加最小值限制
                field_schema["minimum"] = 0
            
            elif field_type == "Int":
                # 整数类型添加最小值限制  
                field_schema["minimum"] = 0
            
            elif field_type == "Date":
                # 日期字段添加格式
                field_schema["format"] = "date"
            
            elif field_type == "Datetime":
                # 日期时间字段添加格式
                field_schema["format"] = "date-time"
            
            elif field_type == "Time":
                # 时间字段添加格式
                field_schema["format"] = "time"
            
            elif field_type == "Email":
                # 邮箱字段添加格式
                field_schema["format"] = "email"
            
            elif field_type == "URL":
                # URL字段添加格式
                field_schema["format"] = "uri"
            
            elif field_type == "Table":
                # 子表类型处理
                if with_child_tables and field.options and len(field.options) > 0:
                    child_doctype = field.options[0]
                    try:
                        # 动态导入避免循环依赖
                        from pkg.fiuaiclient .setup import load_doctype_meta
                        child_meta = load_doctype_meta(child_doctype)
                        if child_meta:
                            # 递归创建子表的JSON Schema
                            child_schema = child_meta.create_json_schema(with_child_tables=with_child_tables)
                            field_schema["items"] = child_schema
                        else:
                            # 如果加载失败，使用基础的对象结构
                            field_schema["items"] = {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "子表行名称"},
                                    "idx": {"type": "integer", "description": "子表行索引", "minimum": 1},
                                    "doctype": {"type": "string", "description": "子表文档类型"}
                                },
                                "required": ["idx", "doctype"]
                            }
                    except Exception:
                        # 异常情况下使用基础结构
                        field_schema["items"] = {
                            "type": "object", 
                            "properties": {
                                "name": {"type": "string", "description": "子表行名称"},
                                "idx": {"type": "integer", "description": "子表行索引", "minimum": 1},
                                "doctype": {"type": "string", "description": "子表文档类型"}
                            },
                            "required": ["idx", "doctype"]
                        }
                else:
                    # 不包含子表详情时，使用简单的数组结构
                    field_schema["items"] = {"type": "object"}
            
            # 添加字段到properties
            properties[field_name] = field_schema
            
            # 检查是否为必填字段
            if field.reqd:
                required_fields.append(field_name)
        
        # 添加doctype字段
        properties["doctype"] = {
            "type": "string",
            "description": "文档类型",
            "const": self.name  # 固定值
        }
        required_fields.append("doctype")
        
        # 构建最终的JSON Schema
        json_schema = {
            "type": "object",
            "title": f"{self.name} Schema",
            "description": self.doctype_prompts if self.doctype_prompts else f"{self.name}文档类型的数据结构",
            "properties": properties,
            "required": required_fields,
            "additionalProperties": False  # 不允许额外属性
        }
        
        return json_schema