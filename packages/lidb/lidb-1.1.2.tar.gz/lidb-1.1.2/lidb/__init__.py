# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 

from .init import (
    NAME,
    DB_PATH,
    CONFIG_PATH,
    get_settings,
)

from .database import (
    sql,
    put,
    has,
    tb_path,
    read_mysql,
    read_ck,
    scan,
)

from .parse import parse_hive_partition_structure

__version__ = "1.1.2"