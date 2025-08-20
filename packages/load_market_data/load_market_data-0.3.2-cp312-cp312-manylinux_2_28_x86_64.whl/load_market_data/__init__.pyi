# load_market_data.pyi
def parse_market_data(db_path: str, output_path: str, force_parse: bool = False) -> None:
    """
    解析市场数据, 输出parquet结果到指定路径
    
    :param db_path: 数据库路径
    :param output_path: 输出路径
    :param force_parse: 是否强制解析, 如果目标文件已生成是否重新解析, 默认为False
    :return: None
    """
    ...


def save_mem_signal_snapshot(db_path: str, output_path: str) -> None:
    """
    解析signal_snapshot数据, 输出内存映射文件结果到指定路径
    
    :param db_path: 数据库路径
    :param output_path: 输出路径
    :return: None
    """
    ...