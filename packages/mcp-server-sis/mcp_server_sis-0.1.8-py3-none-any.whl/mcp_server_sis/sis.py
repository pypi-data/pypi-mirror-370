from typing import Any, Dict, Optional, Annotated
from pydantic import Field
import asyncio
import time
import logging
from fastmcp import FastMCP
import os
import dotenv
from .sis_system import SisSystem

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("CUHKSZ-SIS")

# 全局变量
_sis_instance: Optional[SisSystem] = None
_last_login_time: float = 0
_global_cache: Dict[str, Dict] = {}
LOGIN_TIMEOUT = 15 * 60  # 15分钟，单位秒

def _get_sis_instance() -> SisSystem:
    """获取SIS实例，如果需要则重新登录"""
    global _sis_instance, _last_login_time
    
    current_time = time.time()
    
    # 检查是否需要重新登录
    if (_sis_instance is None or 
        current_time - _last_login_time > LOGIN_TIMEOUT):
        
        if _sis_instance is None:
            logger.info("SIS instance not found, creating a new one.")
        else:
            logger.info(f"Login session timed out ({LOGIN_TIMEOUT}s). Performing relogin.")
        
        username = os.getenv("SIS_USERNAME")
        password = os.getenv("SIS_PASSWORD")
        
        if not username or not password:
            logger.error("SIS_USERNAME and SIS_PASSWORD must be set in environment variables.")
            raise ValueError("SIS_USERNAME and SIS_PASSWORD must be set in environment variables")
        
        _sis_instance = SisSystem(username, password)
        logger.info("Attempting to login to SIS...")
        success = _sis_instance.login()
        
        if success:
            _last_login_time = current_time
            logger.info(f"SIS login successful at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
        else:
            logger.error("Failed to login to SIS system")
            raise RuntimeError("Failed to login to SIS system")
    
    return _sis_instance

def _get_cached_or_fetch(cache_key: str, fetch_func, ttl: int = 300) -> str:
    """从缓存获取数据或重新获取"""
    global _global_cache
    
    current_time = time.time()
    
    # 检查缓存是否存在且未过期
    if (cache_key in _global_cache and 
        current_time - _global_cache[cache_key]['timestamp'] < ttl):
        logger.info(f"Cache HIT for key: '{cache_key}'")
        return _global_cache[cache_key]['data']
    
    logger.info(f"Cache MISS for key: '{cache_key}'. Fetching new data.")
    # 缓存不存在或已过期，重新获取数据
    try:
        data = fetch_func()
        _global_cache[cache_key] = {
            'data': data,
            'timestamp': current_time
        }
        logger.info(f"Successfully fetched and cached data for key: '{cache_key}'")
        return data
    except Exception as e:
        logger.error(f"Error fetching data for key '{cache_key}': {e}", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool(
    description="获取用户在CUHKSZ的课程表",
)
async def sis_get_schedule() -> str:
    """获取课程表
    
    Args:
        None
    Returns:
        str: 课程表
    """
    logger.info("Tool 'sis_get_schedule' called.")
    def fetch_schedule():
        sis = _get_sis_instance()
        return sis.get_schedule()
    
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _get_cached_or_fetch("schedule", fetch_schedule, ttl=3600)  # 1小时缓存
    )

@mcp.tool(
    description="获取CUHKSZ指定课程的在指定学期的开课信息",
)
async def sis_get_course(
    course_code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")],
    term: Annotated[str, Field(description="学期(注意学期格式要求, '24' 代表2024-25学年, '10' 代表秋季学期, '20' 代表春夏学期, '50' 代表暑期学期, 如: '2410' 代表 2024-25 Term1(即2024年秋季学期), '2420' 代表 2024-25 Term2(即2025年春夏学期), '2450' 代表 2024-25 Summer Session(即2025年暑期学期))")],
    open_only: Annotated[bool, Field(description="是否只查询开放课程(如 True, 则只查询开放课程)")] = False
) -> str:
    """查询课程信息
    
    Args:
        course_code (str): 课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)
        term (str): 学期(如 "2410" 代表 2024-25 Term1, "2420" 代表 2024-25 Term2, "2450" 代表 2024-25 Summer Session)
        open_only (bool): 是否只查询开放课程(如 True, 则只查询开放课程)
    Returns:
        str: 课程信息
    """
    logger.info(f"Tool 'sis_get_course' called with params: code={course_code}, term={term}, open_only={open_only}")
    cache_key = f"course_{course_code}_{term}_{open_only}"
    
    def fetch_course():
        sis = _get_sis_instance()
        return sis.get_course(course_code, term, open_only)
    
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _get_cached_or_fetch(cache_key, fetch_course, ttl=3600)  # 1小时缓存
    )

@mcp.tool(
    description="获取用户在CUHKSZ指定学期的成绩",
)
async def sis_get_grades(
    term: Annotated[str, Field(description="学期(注意学期格式要求, '24' 代表2024-25学年, 'Term1' 代表秋季学期, 'Term2' 代表春夏学期, 'Summer Session' 代表暑期学期, 如: '24t1' 代表 2024-25 Term1(即2024年秋季学期), '24t2' 代表 2024-25 Term2(即2025年春夏学期), '24s' 代表 2024-25 Summer Session(即2025年暑期学期))")]
) -> str:
    """查询成绩
    
    Args:
        term (str): 学期(如 2024-25 Term 1, 2024-25 Term 2, 2024-25 Summer Session)
    Returns:
        str: 成绩
    """
    logger.info(f"Tool 'sis_get_grades' called with params: term={term}")
    cache_key = f"grades_{term}"
    
    def fetch_grades():
        sis = _get_sis_instance()
        return sis.get_grades(term)
    
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _get_cached_or_fetch(cache_key, fetch_grades, ttl=3600)  # 1小时缓存
    )

@mcp.tool(
    description="获取CUHKSZ指定课程的课程大纲",
)
async def sis_get_course_outline(
    course_code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")]
) -> str:
    """查询课程大纲
    
    Args:
        course_code (str): 课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)
    Returns:
        str: 课程大纲
    """
    logger.info(f"Tool 'sis_get_course_outline' called with params: code={course_code}")
    cache_key = f"outline_{course_code}"
    
    def fetch_outline():
        sis = _get_sis_instance()
        return sis.get_course_outline(course_code)
    
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _get_cached_or_fetch(cache_key, fetch_outline, ttl=3600)  # 1小时缓存
    )

@mcp.tool(
    description="获取用户在CUHKSZ的学术记录",
)
async def sis_get_academic_record() -> str:
    """查询学术记录
    
    Args:
        None
    Returns:
        str: 学术记录
    """
    logger.info("Tool 'sis_get_academic_record' called.")
    def fetch_record():
        sis = _get_sis_instance()
        return sis.get_academic_record()
    
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _get_cached_or_fetch("academic_record", fetch_record, ttl=3600)  # 1小时缓存
    )

# @mcp.tool()
# async def sis_clear_cache() -> str:
#     """清除缓存"""
#     logger.info("Tool 'sis_clear_cache' called.")
#     global _global_cache
#     _global_cache.clear()
#     logger.info("Global cache has been cleared.")
#     return "Cache cleared successfully"

# @mcp.tool()
# async def sis_force_relogin() -> str:
#     """强制重新登录"""
#     logger.info("Tool 'sis_force_relogin' called.")
#     global _sis_instance, _last_login_time
#     _sis_instance = None
#     _last_login_time = 0
    
#     try:
#         _get_sis_instance()
#         return "Force relogin successful"
#     except Exception as e:
#         logger.error("Force relogin failed.", exc_info=True)
#         return f"Force relogin failed: {str(e)}"

# 交互式测试函数
def test():
    async def _test():
        print("请先设置环境变量 SIS_USERNAME 和 SIS_PASSWORD")
        # print("1. 查询课表\n2. 查询课程\n3. 查询成绩\n4. 查询课程大纲\n5. 查询学术记录\n6. 清除缓存\n7. 强制重新登录")
        print("1. 查询课表\n2. 查询课程\n3. 查询成绩\n4. 查询课程大纲\n5. 查询学术记录")
        choice = input("请选择功能编号: ")
        
        if choice == "1":
            result = await sis_get_schedule()
            print("\n课表结果:\n", result)
        elif choice == "2":
            course_code = input("请输入课程代码（如 CSC3002）: ")
            term = input("请输入学期代码（如 2510）: ")
            open_only = input("只看开放课程？(y/n): ").lower() == 'y'
            result = await sis_get_course(course_code, term, open_only)
            print("\n课程查询结果:\n", result)
        elif choice == "3":
            term = input("请输入学期名称（如 2024-25 Term 1）: ")
            result = await sis_get_grades(term)
            print("\n成绩查询结果:\n", result)
        elif choice == "4":
            course_code = input("请输入课程代码（如 CSC3002）: ")
            result = await sis_get_course_outline(course_code)
            print("\n课程大纲查询结果:\n", result)
        elif choice == "5":
            print("查询学术记录，请稍等...")
            result = await sis_get_academic_record()
            print("\n学术记录查询结果:\n", result)
        # elif choice == "6":
        #     result = await sis_clear_cache()
        #     print(result)
        # elif choice == "7":
        #     result = await sis_force_relogin()
        #     print(result)
        else:
            print("无效选择")
    
    asyncio.run(_test())

if __name__ == "__main__":
    test()
