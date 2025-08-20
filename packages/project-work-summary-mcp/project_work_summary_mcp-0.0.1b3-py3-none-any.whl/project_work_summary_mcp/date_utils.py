"""
日期格式处理工具模块
提供日期格式转换等功能
"""

import re
from calendar import monthrange
from datetime import datetime


def convert_date_format_if_needed(date_str):
    """
    仅在输入为特殊格式时进行转换，否则返回None表示不转换
    特殊格式：25年5月 -> 2025-05-01, 2025-05-31
    
    Args:
        date_str (str): 输入的日期字符串
        
    Returns:
        tuple: (start_date, end_date) 或 (None, None) 如果不需要转换
    """
    if not date_str:
        return None, None
        
    # 只有当输入符合特殊格式时才进行转换
    year_month_match = re.match(r'^(\d{2})年(\d{1,2})月$', date_str)
    if year_month_match:
        year = int(year_month_match.group(1))
        month = int(year_month_match.group(2))
        
        # 自动补全年份（假设为20xx年）
        if year >= 0 and year <= 99:
            year += 2000
            
        # 计算该月的第一天和最后一天
        _, last_day = monthrange(year, month)
        
        start_date = f"{year:04d}-{month:02d}-01"
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
        
        return start_date, end_date
    
    # 如果不是特殊格式（包括标准格式），不进行转换
    return None, None
