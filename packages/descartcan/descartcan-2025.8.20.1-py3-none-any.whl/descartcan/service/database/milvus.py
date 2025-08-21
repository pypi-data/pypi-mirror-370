import asyncio
import time
import traceback
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from pymilvus import MilvusClient, DataType, CollectionSchema
from pymilvus.milvus_client.index import IndexParams
from descartcan.config import config
from descartcan.utils.log import logger


class MilvusConnection:

    def __init__(self):
        self.uri = f"{config.MILVUS_PREFIX}://{config.MILVUS_HOST}:{config.MILVUS_PORT}"
        self.token = config.MILVUS_TOKEN
        self.db_name = config.MILVUS_DB_NAME
        self.client = None
        self.in_use = False
        self.last_used = time.time()
        self.created_at = time.time()

    def connect(self):
        if self.client is None:
            self.client = MilvusClient(
                uri=self.uri,
                token=self.token,
                db_name=self.db_name
            )
        return self.client

    def disconnect(self):
        self.client = None

    def is_connected(self):
        if self.client is None:
            return False

        try:
            self.client.list_collections()
            return True
        except Exception as e:
            logger.warning(f"连接检查失败: {e}")
            return False


class MilvusConnectionPool:
    """Milvus 连接池实现"""

    def __init__(
            self,
            max_connections: int = 10,
            min_connections: int = 2,
            max_idle_time: int = 300,  # 空闲连接的最大生存时间（秒）
            connection_timeout: int = 30,  # 获取连接的超时时间（秒）
            connection_ttl: int = 3600,  # 连接的最大生存时间（秒）
            health_check_interval: int = 60  # 健康检查间隔（秒）
    ):
        """
        初始化连接池

        Args:
            max_connections: 连接池中最大连接数
            min_connections: 连接池中最小连接数（预创建）
            max_idle_time: 空闲连接的最大生存时间（秒）
            connection_timeout: 获取连接的超时时间（秒）
            connection_ttl: 连接的最大生存时间（秒）
            health_check_interval: 健康检查间隔（秒）
        """
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_idle_time = max_idle_time
        self.connection_timeout = connection_timeout
        self.connection_ttl = connection_ttl
        self.health_check_interval = health_check_interval

        # 连接池
        self.pool: List[MilvusConnection] = []
        # 连接可用性信号量
        self.semaphore = asyncio.Semaphore(max_connections)
        # 连接池锁
        self.lock = asyncio.Lock()
        # 健康检查任务
        self.health_check_task = None
        # 连接池状态
        self.running = False

    async def start(self):
        """启动连接池"""
        if self.running:
            return

        self.running = True

        # 预创建连接
        async with self.lock:
            for _ in range(self.min_connections):
                conn = MilvusConnection()
                conn.connect()
                self.pool.append(conn)

        # 启动健康检查任务
        self.health_check_task = asyncio.create_task(self._health_check())

        logger.info(f"Milvus 连接池已启动，初始连接数: {self.min_connections}")

    async def stop(self):
        """停止连接池"""
        if not self.running:
            return

        self.running = False

        # 取消健康检查任务
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        # 关闭所有连接
        async with self.lock:
            for conn in self.pool:
                conn.disconnect()
            self.pool.clear()

        logger.info("Milvus 连接池已停止")

    async def _health_check(self):
        """定期健康检查，清理过期连接，确保最小连接数"""
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)

                if not self.running:
                    break

                current_time = time.time()
                to_remove = []

                async with self.lock:
                    # 检查并移除过期连接
                    for conn in self.pool:
                        # 跳过正在使用的连接
                        if conn.in_use:
                            continue

                        # 检查空闲超时
                        if current_time - conn.last_used > self.max_idle_time:
                            to_remove.append(conn)
                            continue

                        # 检查连接总生存时间
                        if current_time - conn.created_at > self.connection_ttl:
                            to_remove.append(conn)
                            continue

                        # 检查连接是否有效
                        if not conn.is_connected():
                            to_remove.append(conn)

                    # 移除过期或无效连接
                    for conn in to_remove:
                        if conn in self.pool:
                            conn.disconnect()
                            self.pool.remove(conn)

                    # 确保最小连接数
                    idle_count = sum(1 for conn in self.pool if not conn.in_use)
                    for _ in range(max(0, self.min_connections - idle_count)):
                        if len(self.pool) < self.max_connections:
                            conn = MilvusConnection()
                            conn.connect()
                            self.pool.append(conn)

                logger.debug(f"健康检查完成，当前连接池大小: {len(self.pool)}, 移除: {len(to_remove)}")

            except Exception as e:
                logger.error(f"健康检查出错: {e}")

    async def get_connection(self) -> MilvusConnection:
        """获取一个可用连接"""
        if not self.running:
            await self.start()

        # 使用超时机制获取信号量
        try:
            # 创建一个任务来获取信号量，并设置超时
            acquire_task = asyncio.create_task(self.semaphore.acquire())
            done, pending = await asyncio.wait(
                [acquire_task],
                timeout=self.connection_timeout
            )

            if acquire_task not in done:
                # 取消任务
                acquire_task.cancel()
                raise TimeoutError(f"获取 Milvus 连接超时，当前连接池大小: {len(self.pool)}")
        except Exception as e:
            if not isinstance(e, TimeoutError):
                logger.error(f"获取连接信号量时出错: {e}")
            raise

        # 尝试获取空闲连接
        async with self.lock:
            # 查找空闲连接
            for conn in self.pool:
                if not conn.in_use:
                    conn.in_use = True
                    conn.last_used = time.time()
                    return conn

            # 如果没有空闲连接但未达到最大连接数，创建新连接
            if len(self.pool) < self.max_connections:
                conn = MilvusConnection()
                conn.connect()
                conn.in_use = True
                conn.last_used = time.time()
                self.pool.append(conn)
                return conn

        # 这种情况理论上不会发生，因为我们有信号量控制
        self.semaphore.release()
        raise RuntimeError("无法获取 Milvus 连接")

    def release_connection(self, conn: MilvusConnection):
        conn.in_use = False
        conn.last_used = time.time()
        self.semaphore.release()

    @asynccontextmanager
    async def connection(self):
        conn = await self.get_connection()
        try:
            yield conn.client
        finally:
            self.release_connection(conn)


class AsyncMilvusClient:

    _instance = None
    _pool = None

    @classmethod
    def get_milvus_client(cls):
        if config.MILVUS_HOST and config.MILVUS_PORT and config.MILVUS_PREFIX:
            return AsyncMilvusClient()
        return None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncMilvusClient, cls).__new__(cls)
            cls._pool = MilvusConnectionPool(
                max_connections=config.MILVUS_MAX_CONNECTIONS,
                min_connections=config.MILVUS_MIN_CONNECTIONS,
                max_idle_time=config.MILVUS_MAX_IDLE_TIME,
                connection_timeout=config.MILVUS_CONNECTION_TIMEOUT,
                connection_ttl=config.MILVUS_CONNECTION_TTL,
                health_check_interval=config.MILVUS_HEALTH_CHECK_INTERVAL
            )
        return cls._instance

    async def start(self):
        await self._pool.start()

    async def stop(self):
        await self._pool.stop()

    @asynccontextmanager
    async def connection(self):
        async with self._pool.connection() as client:
            yield client

    async def create(self, name: str, schema: CollectionSchema, index_params: IndexParams):
        try:
            async with self._pool.connection() as client:
                if not client.has_collection(name):
                    client.create_collection(
                        name, auto_id=True, schema=schema, index_params=index_params
                    )
                    logger.info(f"milvus create collection:{name}")
        except Exception as e:
            logger.error(f"milvus create error: {traceback.format_exc()}")

    async def load(self, collection_names: [str] = None):
        try:
            async with self._pool.connection() as client:
                for name in collection_names:
                    if client.has_collection(name):
                        client.load_collection(name)
                        logger.info(f"milvus load collection:{name}")
                    else:
                        logger.error(f"milvus load collection:{name} error")
        except Exception as e:
            logger.error(f"milvus load error: {traceback.format_exc()}")

    async def insert(self, name: str, data: List[Dict[str, Any]] = None):
        try:
            async with self._pool.connection() as client:
                client.insert(name, data=data)
        except Exception as e:
            logger.error(f"milvus insert error: {traceback.format_exc()}")

    async def search(self, name, data, anns_field, param, limit=10, expr=None, output_fields=None):
        try:
            async with self._pool.connection() as client:
                return client.search(
                    name, data, anns_field, param, limit,
                    expression=expr, output_fields=output_fields
                )
        except Exception as e:
            logger.error(f"milvus search error: {traceback.format_exc()}")

    async def delete(self, name: str, ids: List[int]):
        try:
            expr = f"id in {ids}"
            async with self._pool.connection() as client:
                return client.delete(name, expr=expr)
        except Exception as e:
            logger.error(f"milvus delete {ids} error: {traceback.format_exc()}")

    async def drop_collection(self, name: str):
        try:
            async with self._pool.connection() as client:
                return client.drop_collection(name)
        except Exception as e:
            logger.error(f"milvus drop {name} error: {traceback.format_exc()}")

    async def get_collection_stats(self, name: str):
        try:
            async with self._pool.connection() as client:
                return client.get_collection_stats(name)
        except Exception as e:
            logger.error(f"milvus get collection {name} stats error: {traceback.format_exc()}")

    async def list_collections(self):
        try:
            async with self._pool.connection() as client:
                return client.list_collections()
        except Exception as e:
            logger.error(f"milvus list collections error: {traceback.format_exc()}")
