"""
公共配置文件, 项目直接访问
"""
import yaml


PGSQL_URL:str

SCHEMA='public'


globals().update(yaml.safe_load(open('config_private.yaml', encoding='utf-8')))
