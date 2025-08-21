import datetime
def generate_date_ranges(start_date_str, end_date_str, date_format, period_type='day', interval_days=None):
    """
    生成指定粒度的日期范围
    
    Args:
        start_date_str: 开始日期字符串（需与date_format匹配）
        end_date_str: 结束日期字符串（需与date_format匹配）
        date_format: 日期格式字符串（如'%Y-%m-%d'）,若含时间部分，则默认为'%Y-%m-%d %H:%M:%S',则开始时间为00:00:00，结束时间为23:59:59
        period_type: 分组类型，可选值：
            'year' - 按整年分组
            'month' - 按整月分组
            'week' - 按自然周分组（周一至周日）
            'day' - 按单日分组
            'custom' - 自定义间隔天数
        interval_days: 自定义间隔天数（仅当period_type='custom'时有效）
    
    Returns:
        List[Tuple[str, str]]: 日期范围列表，每个元素包含(开始日期, 结束日期)
    
    示例:
         generate_date_ranges('2023-01-01', '2023-01-15', '%Y-%m-%d', 'week')
        [('2023-01-01', '2023-01-01'), ('2023-01-02', '2023-01-08'), 
         ('2023-01-09', '2023-01-15')]
    """
    ranges = []  # 初始化日期范围列表
    
    # 判断传入的日期字符串是否包含时间部分
    input_has_time = any(token in start_date_str for token in ['T', ' ', ':'])
    
    # 如果传入的日期字符串不包含时间部分，但在date_format中包含时间部分，则添加默认时间
    if not input_has_time and any(token in date_format for token in ['%H', '%I', '%p', '%M', '%S', '%f', '%z', '%Z']):
        start_date_str += ' 00:00:00'
        end_date_str += ' 00:00:00'
        input_has_time = True  # 更新input_has_time为True，因为已经添加了时间部分
    
    # 解析日期并调整时间
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S' if input_has_time else '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S' if input_has_time else '%Y-%m-%d')
    
    # 检查日期格式是否包含时间部分
    has_time = any(token in date_format for token in ['%H', '%I', '%p', '%M', '%S', '%f', '%z', '%Z'])
    
    # 调整开始和结束时间
    if has_time:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    current_start = start_date
    
    while current_start <= end_date:
        if period_type == 'year':
            year_start = datetime.datetime(current_start.year, 1, 1)
            next_year_start = datetime.datetime(current_start.year + 1, 1, 1)
            year_end = next_year_start - datetime.timedelta(days=1)
            if has_time:
                year_end = year_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            ranges.append((year_start.strftime(date_format), year_end.strftime(date_format)))
            current_start = next_year_start
        
        elif period_type == 'month':
            # 计算当月最后一天
            if current_start.month == 12:
                next_month = datetime.datetime(current_start.year + 1, 1, 1)
            else:
                next_month = datetime.datetime(current_start.year, current_start.month + 1, 1)
            month_end = next_month - datetime.timedelta(days=1)
            month_start = datetime.datetime(current_start.year, current_start.month, 1)
            if has_time:
                month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            ranges.append((month_start.strftime(date_format), month_end.strftime(date_format)))
            current_start = next_month
        
        elif period_type == 'week':
            # 处理周分组逻辑：
            # 1. 如果current_start是周日，直接作为单日周
            # 2. 否则计算到当周周日的间隔天数
            weekday = current_start.weekday()
            if weekday == 6:  # 周日直接结束
                week_end = current_start
            else:
                days_to_sunday = 6 - weekday  # 计算到周日的天数差
                week_end = current_start + datetime.timedelta(days=days_to_sunday)
            if week_end > end_date:
                week_end = end_date
            if has_time:
                week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            ranges.append((current_start.strftime(date_format), week_end.strftime(date_format)))
            current_start = week_end + datetime.timedelta(days=1)
        
        elif period_type == 'day':
            end_day = current_start
            if has_time:
                end_day = end_day.replace(hour=23, minute=59, second=59, microsecond=999999)
            ranges.append((current_start.strftime(date_format), end_day.strftime(date_format)))
            current_start += datetime.timedelta(days=1)
        
        elif period_type == 'custom' and interval_days is not None:
            end_interval = current_start + datetime.timedelta(days=interval_days - 1)
            if end_interval > end_date:
                end_interval = end_date
            if has_time:
                end_interval = end_interval.replace(hour=23, minute=59, second=59, microsecond=999999)
            ranges.append((current_start.strftime(date_format), end_interval.strftime(date_format)))
            current_start = end_interval + datetime.timedelta(days=1)
        
        else:
            raise ValueError("Invalid period_type. Expected 'year','month','week','day', or 'custom'")
    
    return ranges