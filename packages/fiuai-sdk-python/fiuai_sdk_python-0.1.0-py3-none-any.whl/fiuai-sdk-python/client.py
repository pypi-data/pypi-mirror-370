import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from urllib.parse import quote
from io import StringIO
from typing import Any, Literal

from .util import create_headers
from .error import FiuaiGeneralError, FiuaiAuthError
from logging import getLogger
from .type import UserProfile

logger = getLogger(__name__)

class NotUploadableException(FiuaiGeneralError):
	def __init__(self, doctype):
		self.message = "The doctype `{1}` is not uploadable, so you can't download the template".format(doctype)


class FiuaiSDK(object):
    def __init__(self, 
        username: str, 
        url: str,
        password: str=None, 
        token_key: str=None, 
        token_secret: str=None,
        auth_type: Literal["internal", "password"]="password",
        max_api_retry: int=3,
        timeout: int=5,
        verify: bool=False
    ):
        self.username = username
    
        self.auth_type = auth_type
        self.headers = None
        self.verify = verify
        self.url = url
        self.max_api_retry = max_api_retry

        self.client = httpx.Client(
            verify=self.verify,
            timeout=timeout,
            follow_redirects=True,
            proxy=None
        )

        match self.auth_type:
            case "internal":
                if token_key == "" or token_secret == "":
                    raise FiuaiGeneralError("Token key and secret are required")
                self.headers = create_headers(token_key, token_secret, username)
            case "password":
                if username == "" or password == "":
                    raise FiuaiGeneralError("Username and password are required")
                
                self.headers = {"Accept": "application/json"}
                self._login(username, password)
            case _:
                raise FiuaiGeneralError(f"Invalid auth type: {self.auth_type}")

        
    def _login(self, username: str, password: str):
        r = self.client.post(self.url, data={
			'cmd': 'login',
			'usr': username,
			'pwd': password
		}, headers=self.headers)

        if r.json().get('message') == "Logged In":
            self.can_download = []
            logger.info(f"Login to {self.url} success")
            return r.json()
        else:
            raise FiuaiAuthError(f"Login failed: {r.json().get('message')}")
    
    def _logout(self):
        logger.info(f"Logout from {self.url}")
        self.client.get(self.url, params={"cmd": "logout"}, headers=self.headers)


    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._logout()
        self.client.close()
        # self.logout()

   
    def get_avaliable_company(self, page: int=1, page_size: int=20) -> str:
        r = self.client.get(self.url + "/api/method/fiuai.network.doctype.company.company.get_available_companies", params={"page": page, "page_size": page_size})
        return self.post_process(r)
    
    def swith_company(self, tenant: str, company: str) -> bool:
        if self.auth_type == "internal":
            self.headers["Fiuai-Internal-Tenant"] = tenant
            self.headers["Fiuai-Internal-Company"] = company
        else:
            r = self.client.post(self.url + "/api/method/frappe.sessions.change_current_company",
			data={"auth_company_id": company})
            if r.status_code != 200:
                logger.error(f"Switch company failed: {r.json().get('message')}")
                # raise FiuaiAuthError(f"Switch company failed: {r.json().get('message')}")
                return False
            else:
                return True

    def get_user_profile(self) -> UserProfile:
        d = self.get_doc("User", self.username, fields=["name", "full_name", "email", "phone", "roles", "auth_tenant_id", "default_company_id"])
        return UserProfile(
            name=self.username,
            full_name=d.get("full_name"),
            email=d.get("email"),
            roles=[x.get("role") for x in d.get("roles")],
            auth_tenant_id=d.get("auth_tenant_id"),
            phone=d.get("phone") or "",
            default_company_id=d.get("default_company_id") or "",
        )
            
    def get_list(self, doctype, fields='"*"', filters=None, limit_start=0, limit_page_length=0, order_by=None):
        '''Returns list of records of a particular type'''
        if not isinstance(fields, str):
            fields = json.dumps(fields)
        params = {
            "fields": fields,
        }
        if filters:
            params["filters"] = json.dumps(filters)
        if limit_page_length:
            params["limit_start"] = str(limit_start)
            params["limit_page_length"] = str(limit_page_length)
        if order_by:
            params['order_by'] = order_by

        res = self.client.get(self.url + "/api/resource/" + doctype, params=params, headers=self.headers)
        return self.post_process(res)        

    def insert(self, doc):
        '''Insert a document to the remote server

        :param doc: A dict or Document object to be inserted remotely'''
        res = self.client.post(self.url + "/api/resource/" + quote(doc.get("doctype")),
            data={"data":json.dumps(doc)}, headers=self.headers)
        
        return self.post_process(res)


    def update(self, doc):
        '''Update a remote document

        :param doc: dict or Document object to be updated remotely. `name` is mandatory for this'''
        url = self.url + "/api/resource/" + quote(doc.get("doctype")) + "/" + quote(doc.get("name"))
        res = self.client.put(url, data={"data":json.dumps(doc)}, headers=self.headers)
        return self.post_process(res)


    def delete(self, doctype, name):
        '''Delete remote document by name

        :param doctype: `doctype` to be deleted
        :param name: `name` of document to be deleted'''
        return self.post_request({
            'cmd': 'frappe.client.delete',
            'doctype': doctype,
            'name': name
        })

    def submit(self, doclist):
        '''Submit remote document

        :param doc: dict or Document object to be submitted remotely'''
        return self.post_request({
            'cmd': 'frappe.client.submit',
            'doclist': json.dumps(doclist)
        })


    def cancel(self, doctype, name):
        return self.post_request({
            'cmd': 'frappe.client.cancel',
            'doctype': doctype,
            'name': name
        })

    def get_doc(self, doctype, name="", filters=None, fields=None):
        '''Returns a single remote document

        :param doctype: DocType of the document to be returned
        :param name: (optional) `name` of the document to be returned
        :param filters: (optional) Filter by this dict if name is not set
        :param fields: (optional) Fields to be returned, will return everythign if not set'''
        params = {}
        if filters:
            params["filters"] = json.dumps(filters)
        if fields:
            params["fields"] = json.dumps(fields)

        res = self.client.get(self.url + '/api/resource/' + doctype + '/' + name,
                                params=params, headers=self.headers)

        return self.post_process(res)


    def get_api(self, method, params={}):
        res = self.client.get(self.url + '/api/method/' + method.lstrip('/') , params=params, headers=self.headers)
        return self.post_process(res)

    def post_api(self, method, postdata={}):
        res = self.client.post(self.url + '/api/method/' + method.lstrip('/'), data=postdata, headers=self.headers)
        return self.post_process(res)
    
    def get_v2_api(self, uri, params={}):
        res = self.client.get(self.url + '/api/v2/' + uri.lstrip('/'), params=params, headers=self.headers)
        return self.post_process(res)

    def post_v2_api(self, uri, postdata={}):
        res = self.client.post(self.url + '/api/v2/' + uri.lstrip('/'), data=postdata, headers=self.headers)
        return self.post_process(res)
    
    def internal_create(self, data={}):
        res = self.client.post(self.url + '/api/v2/internal/doctype/create', data={"data":json.dumps(data, ensure_ascii=False)}, headers=self.headers)
        return self.post_process(res)
    
    def get_meta(self, doctype: str):
        res = self.client.get(self.url + '/api/v2/internal/doctype/meta/' + doctype, headers=self.headers)
      
        return self.post_process(res)
    
    def get_request(self, params):
        res = self.client.get(self.url, params=self.preprocess(params), headers=self.headers)
        res = self.post_process(res)
        return res

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
    def post_request(self, data):
        res = self.client.post(self.url, headers=self.headers, data=self.preprocess(data))
        res = self.post_process(res)
        return res

    def preprocess(self, params):
        '''convert dicts, lists to json'''
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                params[key] = json.dumps(value)

        return params

    def post_process(self, response):
        try:
            rjson = response.json()
        except ValueError:
            raise

        if rjson and ('exc' in rjson) and rjson['exc']:
            raise FiuaiGeneralError(rjson['exc'])
        if 'message' in rjson:
            return rjson['message']
        elif 'data' in rjson:
            return rjson['data']
        else:
            return None
