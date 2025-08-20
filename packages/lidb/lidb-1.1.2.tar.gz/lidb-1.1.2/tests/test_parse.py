# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/8/18 11:16
# Description:

import lidb
import logair

logger = logair.get_logger("lidb.test")

def test_parse_hive_partition_structure():
    root_path = lidb.tb_path("mc")
    file_pattern = "*.parquet"
    result = lidb.parse.parse_hive_partition_structure(root_path, file_pattern)
    logger.info(result["freq"].unique())

if __name__ == '__main__':
    test_parse_hive_partition_structure()