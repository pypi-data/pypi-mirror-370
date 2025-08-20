
import os

os.makedirs("logs", exist_ok=True)

from .orm.jxUtils import set_host_id, logger as jxORMLogger
from .orm.orm import ORM, get_by_type_id, get_by_type_name, select
from .orm.common import DBDataType, ColType, jxDB, DBType, set_default_db, get_default_db, get_db, register_create_db, dual_with_db

__all__ = ['set_host_id', 'jxORMLogger', 'ORM', 'select', 'dual_with_db', 'DBDataType', 'ColType', 'jxDB', 'DBType', 'set_default_db', 'get_default_db', 'get_db', 'register_create_db', ]
