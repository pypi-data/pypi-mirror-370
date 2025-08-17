import requests
from dataclasses import dataclass

@dataclass
class CF_TF_RESOURCE():
    name: str
    res_id: str
    zone_code: str
    dns_name: str
    content: str
    type_str: str
    ttl: str
    proxy: str
    comment: str
    priority: str | None

    def as_tf_resource(self) -> str:
        p_str = f'\n  priority = {self.priority}' if self.type_str == "MX" else ''
        return f"""
resource "cloudflare_record" "{self.name}" {{ #{self.zone_code}/{self.res_id}
  zone_id  = "{self.zone_code}"
  name     = "{self.dns_name}"
  content  = "{self.content.replace('"','\\"')}"
  comment  = "{self.comment.replace('"','\\"')}"
  type     = "{self.type_str}"
  ttl      = {self.ttl}
  proxied  = {self.proxy}{p_str}
}}
"""

@dataclass
class _Session():
    token: str

    def headers(self, existing: dict =None):
        headers = {}
        if existing:
            for k in existing:
                headers[k] = existing[k]
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

class Utils:
    def __init__(self, token: str, zone: str):
        self.session = _Session(token)
        self.zone = zone


    @staticmethod
    def url(zone: str, page: int = None, per_page: int = None):
        paging_str = "" if page is None and per_page is None else f"?page={page}&per_page={per_page}"
        return f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records{paging_str}"

    def load_page(self, page: int = None, per_page: int = None)->dict:
        res = requests.get(Utils.url(self.zone, page, per_page), headers=self.session.headers())
        if not res.status_code == requests.codes.ok:
            raise Exception(res.status_code, res.text)
        return res.json()

    def meta(self, res:dict=None)->dict:
        if res is None:
            res = self.load_page()
        result_info = res['result_info']
        return result_info

    def load_full_page(self)->[dict]:
        return Utils.load_dns(self.session.token, self.zone)

    @staticmethod
    def load_dns(token: str, zone: str)->[dict]:
        session = _Session(token)
        res = requests.get(Utils.url(zone), headers=session.headers())
        if not res.status_code == requests.codes.ok:
            raise Exception(res.status_code, res.text)

        records = []
        response = res.json()

        result_info = response['result_info']
        per_page = result_info['per_page']
        for page in range(1, result_info['total_pages'] + 1):
            # print(f"Load page {page}")
            res = requests.get(Utils.url(zone, page=page, per_page=per_page), headers=session.headers())
            for i in res.json()['result']:
                records.append(i)
        return records

    @staticmethod
    def load_from_cf(rec, zone_code, index) -> 'CF_TF_RESOURCE':
        import json
        # print(json.dumps(rec, indent=2))
        return CF_TF_RESOURCE(
            f"{rec['type'].lower()}_{rec['name'].replace('.', '_').replace('-', '_')}_{index}",
            rec['id'],
            zone_code,
            rec['name'],
            rec['content'],
            rec['type'],
            rec['ttl'],
            str(rec.get('proxied', False)).lower(),
            "" if rec['comment'] is None else rec['comment'],
            rec['priority'] if rec['type'] == 'MX' else None
        )

    @staticmethod
    def tf_file_to_import_script(file):
        import re
        pattern = r'^resource "cloudflare_record" "(?P<resource_name>[^"]+)" { #(?P<zone_id>[a-f0-9]+)/(?P<resource_id>[a-f0-9]+)$'
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read()

        for line in data.split("\n"):
            matching = re.match(pattern, line)
            if matching:
                yield f"tofu import cloudflare_record.{matching['resource_name']} {matching['zone_id']}/{matching['resource_id']}"