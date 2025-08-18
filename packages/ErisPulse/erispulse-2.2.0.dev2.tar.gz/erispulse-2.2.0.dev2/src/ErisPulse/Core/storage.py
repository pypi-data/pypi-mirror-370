"""
ErisPulse 存储管理模块

提供键值存储、事务支持、快照和恢复功能，用于管理框架运行时数据。
基于SQLite实现持久化存储，支持复杂数据类型和原子操作。

{!--< tips >!--}
1. 支持JSON序列化存储复杂数据类型
2. 提供事务支持确保数据一致性
3. 自动快照功能防止数据丢失
{!--< /tips >!--}
"""

import os
import json
import sqlite3
import shutil
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple, Type

class StorageManager:
    """
    存储管理器
    
    单例模式实现，提供键值存储的增删改查、事务和快照管理
    
    {!--< tips >!--}
    1. 使用get/set方法操作存储项
    2. 使用transaction上下文管理事务
    3. 使用snapshot/restore管理数据快照
    {!--< /tips >!--}
    """
    
    _instance = None
    db_path = os.path.join(os.path.dirname(__file__), "../data/config.db")
    SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "../data/snapshots")
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            # 确保关键属性在初始化时都有默认值
            self._last_snapshot_time = time.time()
            self._snapshot_interval = 3600
            self._init_db()
            self._initialized = True

    def _init_db(self) -> None:
        """
        {!--< internal-use >!--}
        初始化数据库
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.SNAPSHOT_DIR, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        
        # 启用WAL模式提高并发性能
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()
        
        # 初始化自动快照调度器
        self._last_snapshot_time = time.time()  # 初始化为当前时间
        self._snapshot_interval = 3600  # 默认每小时自动快照

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取存储项的值
        
        :param key: 存储项键名
        :param default: 默认值(当键不存在时返回)
        :return: 存储项的值
        
        :example:
        >>> timeout = storage.get("network.timeout", 30)
        >>> user_settings = storage.get("user.settings", {})
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
                result = cursor.fetchone()
            if result:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return result[0]
            return default
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                self._init_db()
                return self.get(key, default)
            else:
                from . import logger
                logger.error(f"数据库操作错误: {e}")
                
    def get_all_keys(self) -> List[str]:
        """
        获取所有存储项的键名
        
        :return: 键名列表
        
        :example:
        >>> all_keys = storage.get_all_keys()
        >>> print(f"共有 {len(all_keys)} 个存储项")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM config")
            return [row[0] for row in cursor.fetchall()]
            
    def set(self, key: str, value: Any) -> bool:
        """
        设置存储项的值
        
        :param key: 存储项键名
        :param value: 存储项的值
        :return: 操作是否成功
        
        :example:
        >>> storage.set("app.name", "MyApp")
        >>> storage.set("user.settings", {"theme": "dark"})
        """
        try:
            serialized_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            with self.transaction():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, serialized_value))
                conn.commit()
                conn.close()
            
            self._check_auto_snapshot()
            return True
        except Exception as e:
            return False

    def set_multi(self, items: Dict[str, Any]) -> bool:
        """
        批量设置多个存储项
        
        :param items: 键值对字典
        :return: 操作是否成功
        
        :example:
        >>> storage.set_multi({
        >>>     "app.name": "MyApp",
        >>>     "app.version": "1.0.0",
        >>>     "app.debug": True
        >>> })
        """
        try:
            with self.transaction():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                for key, value in items.items():
                    serialized_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                        (key, serialized_value))
                conn.commit()
                conn.close()
            
            self._check_auto_snapshot()
            return True
        except Exception as e:
            return False
            
    def getConfig(self, key: str, default: Any = None) -> Any:
        """
        获取模块/适配器配置项（委托给config模块）
        :param key: 配置项的键(支持点分隔符如"module.sub.key")
        :param default: 默认值
        :return: 配置项的值
        """
        try:
            from .config import config
            return config.getConfig(key, default)
        except Exception as e:
            return default
    
    def setConfig(self, key: str, value: Any) -> bool:
        """
        设置模块/适配器配置（委托给config模块）
        :param key: 配置项键名(支持点分隔符如"module.sub.key")
        :param value: 配置项值
        :return: 操作是否成功
        """
        try:
            from .config import config
            return config.setConfig(key, value)
        except Exception as e:
            return False

    def delete(self, key: str) -> bool:
        """
        删除存储项
        
        :param key: 存储项键名
        :return: 操作是否成功
        
        :example:
        >>> storage.delete("temp.session")
        """
        try:
            with self.transaction():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM config WHERE key = ?", (key,))
                conn.commit()
                conn.close()
            
            self._check_auto_snapshot()
            return True
        except Exception as e:
            return False
            
    def delete_multi(self, keys: List[str]) -> bool:
        """
        批量删除多个存储项
        
        :param keys: 键名列表
        :return: 操作是否成功
        
        :example:
        >>> storage.delete_multi(["temp.key1", "temp.key2"])
        """
        try:
            with self.transaction():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.executemany("DELETE FROM config WHERE key = ?", [(k,) for k in keys])
                conn.commit()
                conn.close()
            
            self._check_auto_snapshot()
            return True
        except Exception as e:
            return False
            
    def get_multi(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取多个存储项的值
        
        :param keys: 键名列表
        :return: 键值对字典
        
        :example:
        >>> settings = storage.get_multi(["app.name", "app.version"])
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(keys))
        cursor.execute(f"SELECT key, value FROM config WHERE key IN ({placeholders})", keys)
        results = {row[0]: json.loads(row[1]) if row[1].startswith(('{', '[')) else row[1] 
                    for row in cursor.fetchall()}
        conn.close()
        return results

    def transaction(self) -> 'StorageManager._Transaction':
        """
        创建事务上下文
        
        :return: 事务上下文管理器
        
        :example:
        >>> with storage.transaction():
        >>>     storage.set("key1", "value1")
        >>>     storage.set("key2", "value2")
        """
        return self._Transaction(self)

    class _Transaction:
        """
        事务上下文管理器
        
        {!--< internal-use >!--}
        确保多个操作的原子性
        """
        
        def __init__(self, storage_manager: 'StorageManager'):
            self.storage_manager = storage_manager
            self.conn = None
            self.cursor = None

        def __enter__(self) -> 'StorageManager._Transaction':
            """
            进入事务上下文
            """
            self.conn = sqlite3.connect(self.storage_manager.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("BEGIN TRANSACTION")
            return self

        def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Any) -> None:
            """
            退出事务上下文
            """
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                from .logger import logger
                logger.error(f"事务执行失败: {exc_val}")
            self.conn.close()

    def _check_auto_snapshot(self) -> None:
        """
        {!--< internal-use >!--}
        检查并执行自动快照
        """
        from .logger import logger
        
        if not hasattr(self, '_last_snapshot_time') or self._last_snapshot_time is None:
            self._last_snapshot_time = time.time()
            
        if not hasattr(self, '_snapshot_interval') or self._snapshot_interval is None:
            self._snapshot_interval = 3600
            
        current_time = time.time()
        
        try:
            time_diff = current_time - self._last_snapshot_time
            if not isinstance(time_diff, (int, float)):
                raise ValueError("时间差应为数值类型")

            if not isinstance(self._snapshot_interval, (int, float)):
                raise ValueError("快照间隔应为数值类型")
                
            if time_diff > self._snapshot_interval:
                self._last_snapshot_time = current_time
                self.snapshot(f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
        except Exception as e:
            logger.error(f"自动快照检查失败: {e}")
            self._last_snapshot_time = current_time
            self._snapshot_interval = 3600

    def set_snapshot_interval(self, seconds: int) -> None:
        """
        设置自动快照间隔
        
        :param seconds: 间隔秒数
        
        :example:
        >>> # 每30分钟自动快照
        >>> storage.set_snapshot_interval(1800)
        """
        self._snapshot_interval = seconds

    def clear(self) -> bool:
        """
        清空所有存储项
        
        :return: 操作是否成功
        
        :example:
        >>> storage.clear()  # 清空所有存储
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM config")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
        
    def __getattr__(self, key: str) -> Any:
        """
        通过属性访问存储项
        
        :param key: 存储项键名
        :return: 存储项的值
        
        :raises KeyError: 当存储项不存在时抛出
            
        :example:
        >>> app_name = storage.app_name
        """
        try:
            return self.get(key)
        except KeyError:
            from . import logger
            logger.error(f"存储项 {key} 不存在")

    def __setattr__(self, key: str, value: Any) -> None:
        """
        通过属性设置存储项
        
        :param key: 存储项键名
        :param value: 存储项的值
            
        :example:
        >>> storage.app_name = "MyApp"
        """
        try:
            self.set(key, value)
        except Exception as e:
            from . import logger
            logger.error(f"设置存储项 {key} 失败: {e}")

    def snapshot(self, name: Optional[str] = None) -> str:
        """
        创建数据库快照
        
        :param name: 快照名称(可选)
        :return: 快照文件路径
        
        :example:
        >>> # 创建命名快照
        >>> snapshot_path = storage.snapshot("before_update")
        >>> # 创建时间戳快照
        >>> snapshot_path = storage.snapshot()
        """
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = os.path.join(self.SNAPSHOT_DIR, f"{name}.db")
        
        try:
            # 快照目录
            os.makedirs(self.SNAPSHOT_DIR, exist_ok=True)
            
            # 安全关闭连接
            if hasattr(self, "_conn") and self._conn is not None:
                try:
                    self._conn.close()
                except Exception as e:
                    from . import logger
                    logger.warning(f"关闭数据库连接时出错: {e}")
            
            # 创建快照
            shutil.copy2(self.db_path, snapshot_path)
            from . import logger
            logger.info(f"数据库快照已创建: {snapshot_path}")
            return snapshot_path
        except Exception as e:
            from . import logger
            logger.error(f"创建快照失败: {e}")
            raise

    def restore(self, snapshot_name: str) -> bool:
        """
        从快照恢复数据库
        
        :param snapshot_name: 快照名称或路径
        :return: 恢复是否成功
        
        :example:
        >>> storage.restore("before_update")
        """
        snapshot_path = os.path.join(self.SNAPSHOT_DIR, f"{snapshot_name}.db") \
            if not snapshot_name.endswith('.db') else snapshot_name
            
        if not os.path.exists(snapshot_path):
            from . import logger
            logger.error(f"快照文件不存在: {snapshot_path}")
            return False
            
        try:
            # 安全关闭连接
            if hasattr(self, "_conn") and self._conn is not None:
                try:
                    self._conn.close()
                except Exception as e:
                    from . import logger
                    logger.warning(f"关闭数据库连接时出错: {e}")
            
            # 执行恢复操作
            shutil.copy2(snapshot_path, self.db_path)
            self._init_db()  # 恢复后重新初始化数据库连接
            from . import logger
            logger.info(f"数据库已从快照恢复: {snapshot_path}")
            return True
        except Exception as e:
            from . import logger
            logger.error(f"恢复快照失败: {e}")
            return False

    def list_snapshots(self) -> List[Tuple[str, datetime, int]]:
        """
        列出所有可用的快照
        
        :return: 快照信息列表(名称, 创建时间, 大小)
        
        :example:
        >>> for name, date, size in storage.list_snapshots():
        >>>     print(f"{name} - {date} ({size} bytes)")
        """
        snapshots = []
        for f in os.listdir(self.SNAPSHOT_DIR):
            if f.endswith('.db'):
                path = os.path.join(self.SNAPSHOT_DIR, f)
                stat = os.stat(path)
                snapshots.append((
                    f[:-3],  # 去掉.db后缀
                    datetime.fromtimestamp(stat.st_ctime),
                    stat.st_size
                ))
        return sorted(snapshots, key=lambda x: x[1], reverse=True)

    def delete_snapshot(self, snapshot_name: str) -> bool:
        """
        删除指定的快照
        
        :param snapshot_name: 快照名称
        :return: 删除是否成功
        
        :example:
        >>> storage.delete_snapshot("old_backup")
        """
        snapshot_path = os.path.join(self.SNAPSHOT_DIR, f"{snapshot_name}.db") \
            if not snapshot_name.endswith('.db') else snapshot_name
            
        if not os.path.exists(snapshot_path):
            from . import logger
            logger.error(f"快照文件不存在: {snapshot_path}")
            return False
            
        try:
            os.remove(snapshot_path)
            from . import logger
            logger.info(f"快照已删除: {snapshot_path}")
            return True
        except Exception as e:
            from . import logger
            logger.error(f"删除快照失败: {e}")
            return False

storage = StorageManager()

__all__ = [
    "storage"
]
