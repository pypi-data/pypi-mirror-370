"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

import logging
from mcp.server.fastmcp import FastMCP
from datasource import MySQLConnectionUtil, load_mysql_config_from_file
from pydantic import BaseModel
from .date_utils import convert_date_format_if_needed

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("projectWorkSummaryMcp")


# 获取发版内容的类
class GetReleaseContentDto(BaseModel):
    requirement_code: str
    requirement_name: str
    
    class Config:
        arbitrary_types_allowed = True

# 获取发版内容（按项目）
@mcp.tool()
def get_release_content_project(
    start_time: str, 
    end_time: str,
    project_name: str
    ) -> list[GetReleaseContentDto]:
    """
    :description 获取发版内容
    根据时间范围，查询当前项目指定时间内的发版内容
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param project_name: 项目名称
    """
    
    # 自动处理日期格式转换
    converted_start, converted_end = convert_date_format_if_needed(start_time)
    if converted_start and converted_end:
        start_time = converted_start
        end_time = converted_end
        logger.info(f"日期格式已转换: {start_time} 到 {end_time}")
    
    logger.info(f"开始执行 get_release_content_project 方法")
    logger.info(f"参数: start_time={start_time}, end_time={end_time}, project_name={project_name}")
    
    # 加载数据库配置
    logger.info("正在加载数据库配置...")
    config = load_mysql_config_from_file()
    logger.info(f"数据库配置加载完成，配置详情: host={config['host']}, port={config['port']}, database={config['database']}")
    
    # 创建数据库连接
    logger.info("正在创建数据库连接...")
    db_util = MySQLConnectionUtil(config, max_retries=3, retry_delay=2.0)
    
    try:
        if not db_util.connect():
            error_msg = "数据库连接失败"
            logger.error(error_msg)
            raise Exception(error_msg)
        logger.info("数据库连接成功")
        
        # 优化：使用JOIN查询一次性获取所需数据，提高性能
        # 通过项目名称获取项目ID，再通过项目ID获取迭代ID，再通过迭代ID获取任务
        # 这样可以避免多次查询和中间变量存储
        task_query = """
        SELECT DISTINCT 
            t.gt_id, 
            t.gt_task_no, 
            t.gt_title 
        FROM gdp_task t
        INNER JOIN gdp_sprint s ON t.gt_sprint_id = s.gs_id
        INNER JOIN gdp_release_window rw ON s.gs_release_win_id = rw.grw_id
        INNER JOIN gdp_sprint_relation sr ON s.gs_id = sr.gsr_sprint_id
        INNER JOIN gdp_project p ON sr.gsr_target_id = p.gp_id
        WHERE 
            rw.grw_release_time >= %s 
            AND rw.grw_release_time <= %s
            AND p.gp_name LIKE %s
            AND t.gt_task_type_id IN (1, 3, 4, 5, 6, 12)
        """
        
        logger.debug(f"执行SQL: {task_query}")
        # 参数构建
        params = (start_time, end_time, f'%{project_name}%')
        logger.debug(f"参数数量: {len(params)}, 参数值: {params}")
        
        tasks = db_util.execute_query(task_query, params)
        logger.info(f"查询到 {len(tasks)} 个任务")
        
        # 构建返回结果
        result = []
        for task in tasks:
            dto = GetReleaseContentDto(
                requirement_code=task['gt_task_no'],
                requirement_name=task['gt_title']
            )
            result.append(dto)
        
        logger.info(f"成功执行 get_release_content_project，返回 {len(result)} 个结果")
        return result
        
    except Exception as e:
        error_msg = f"执行 get_release_content_project 时发生错误: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    finally:
        # 确保关闭数据库连接
        logger.info("正在关闭数据库连接...")
        try:
            db_util.disconnect()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭数据库连接时发生错误: {str(e)}")
    
    


# Add an addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b


# Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"


# Add a prompt
# @mcp.prompt()
# def greet_user(name: str, style: str = "friendly") -> str:
#     """Generate a greeting prompt"""
#     styles = {
#         "friendly": "Please write a warm, friendly greeting",
#         "formal": "Please write a formal, professional greeting",
#         "casual": "Please write a casual, relaxed greeting",
#     }

#     return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# 获取发版内容（按窗口）
@mcp.tool()
def get_release_content_by_window(
    start_time: str, 
    end_time: str,
    window_name: str = None
    ) -> list[GetReleaseContentDto]:
    """
    :description 获取发版内容
    根据时间范围，查询指定时间窗口内的所有发版内容
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param window_name: 发布窗口名称（可选）
    """
    
    # 自动处理日期格式转换
    converted_start, converted_end = convert_date_format_if_needed(start_time)
    if converted_start and converted_end:
        start_time = converted_start
        end_time = converted_end
        logger.info(f"日期格式已转换: {start_time} 到 {end_time}")
    
    logger.info(f"开始执行 get_release_content_by_window 方法")
    logger.info(f"参数: start_time={start_time}, end_time={end_time}, window_name={window_name}")
    
    # 加载数据库配置
    logger.info("正在加载数据库配置...")
    config = load_mysql_config_from_file()
    logger.info(f"数据库配置加载完成，配置详情: host={config['host']}, port={config['port']}, database={config['database']}")
    
    # 创建数据库连接
    logger.info("正在创建数据库连接...")
    db_util = MySQLConnectionUtil(config, max_retries=3, retry_delay=2.0)
    
    try:
        if not db_util.connect():
            error_msg = "数据库连接失败"
            logger.error(error_msg)
            raise Exception(error_msg)
        logger.info("数据库连接成功")
        
        # 如果window_name为空，直接返回空列表
        if not window_name:
            logger.info("window_name为空，直接返回空列表")
            return []
        
        # 优化：使用JOIN查询一次性获取所需数据，提高性能
        # 参考get_release_content_project方法的优化思路
        # 根据窗口名称查询窗口ID，然后获取任务
        task_query = """
        SELECT DISTINCT 
            t.gt_id, 
            t.gt_task_no, 
            t.gt_title 
        FROM gdp_task t
        INNER JOIN gdp_sprint s ON t.gt_sprint_id = s.gs_id
        INNER JOIN gdp_release_window rw ON s.gs_release_win_id = rw.grw_id
        INNER JOIN gdp_sprint_relation sr ON s.gs_id = sr.gsr_sprint_id
        WHERE 
            rw.grw_name LIKE %s
            AND rw.grw_release_time >= %s 
            AND rw.grw_release_time <= %s
            AND t.gt_task_type_id IN (1, 3, 4, 5, 6, 12)
        """
        
        logger.debug(f"执行SQL: {task_query}")
        params = (f'%{window_name}%', start_time, end_time)
        logger.debug(f"参数数量: {len(params)}, 参数值: {params}")
        
        tasks = db_util.execute_query(task_query, params)
        logger.info(f"查询到 {len(tasks)} 个任务")
        
        # 构建返回结果
        result = []
        for task in tasks:
            dto = GetReleaseContentDto(
                requirement_code=task['gt_task_no'],
                requirement_name=task['gt_title']
            )
            result.append(dto)
        
        logger.info(f"成功执行 get_release_content_by_window，返回 {len(result)} 个结果")
        return result
        
    except Exception as e:
        error_msg = f"执行 get_release_content_by_window 时发生错误: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    finally:
        # 确保关闭数据库连接
        logger.info("正在关闭数据库连接...")
        try:
            db_util.disconnect()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭数据库连接时发生错误: {str(e)}")

def main() -> None:
    mcp.run(transport="stdio")
