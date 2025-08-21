# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: lmdb (Lightning Memory-Mapped Database) 快如闪电的内存映射数据库
# 支持多进程
"""
pip install lmdb
pip install msgpack

[question]
MDB_MAP_FULL: Environment mapsize limit reached
[solution]
提升map_size或定时删除历史数据

[question]
lmdb.PanicError: mdb_txn_begin: MDB_PANIC: Update of meta page failed or environment had fatal error

"""
import logging
import threading
from pathlib import Path
from typing import Optional, Union, Any, Dict

import lmdb
import msgpack


class LMDB(object):

    def __init__(self, db_dir: Union[str, Path],
                 map_size: int = int(1e9),
                 max_readers: int = 126,
                 max_dbs: int = 0,
                 readonly: bool = False):
        """
        :param db_dir: 数据库文件路径
        :param map_size: 数据库最大大小（字节）
                         1e9 ≈ 1GB;
                         1e10 ≈ 10GB;
                         1e11 ≈ 100GB(最大值)
        :param max_readers: 最大读取器数量
        :param max_dbs: 最大数据库数量，0表示使用默认值
        :param readonly: 是否只读模式
        """
        self.db_dir = Path(db_dir) if isinstance(db_dir, str) else db_dir
        if not self.db_dir.exists():
            self.db_dir.mkdir(parents=True, exist_ok=True)
        self.map_size = map_size
        self.max_readers = max_readers
        self.max_dbs = max_dbs
        self.readonly = readonly
        self._lock = threading.RLock()
        self.env = self.initialize()

    def initialize(self):
        try:
            return lmdb.open(
                path=str(self.db_dir),
                map_size=self.map_size,
                max_readers=self.max_readers,
                max_dbs=self.max_dbs,
                readonly=self.readonly,
                lock=True
            )
        except Exception as e:
            logging.error(f"initialize lmdb failed: {e}")
            raise

    @staticmethod
    def _encode_key(key: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            return key.encode('utf-8')
        return key

    @staticmethod
    def _decode_key(key: bytes) -> str:
        return key.decode('utf-8')

    @staticmethod
    def _encode_value(value: Any) -> bytes:
        return msgpack.packb(value, use_bin_type=True)

    @staticmethod
    def _decode_value(value_bytes: bytes) -> Any:
        return msgpack.unpackb(value_bytes, raw=False)

    def count(self) -> int:
        with self._lock:
            try:
                with self.env.begin() as txn:
                    return txn.stat()['entries']
            except Exception as e:
                logging.error(f"items count failed from lmdb: {e}")
                return 0

    def insert(self, key: Union[str, bytes], value: Any, txn: Optional[lmdb.Transaction] = None) -> bool:
        try:
            encoded_key = self._encode_key(key)
            encoded_value = self._encode_value(value)
            if txn:
                txn.put(encoded_key, encoded_value)
            else:
                with self.env.begin(write=True) as txn:
                    txn.put(encoded_key, encoded_value)
            return True
        except Exception as e:
            logging.error(f"item insert failed from lmdb: key: {key}, error: {e}")
            return False

    def delete(self, key: Union[str, bytes], txn: Optional[lmdb.Transaction] = None) -> bool:
        with self._lock:
            try:
                encoded_key = self._encode_key(key)
                if txn:
                    txn.delete(encoded_key)
                else:
                    with self.env.begin(write=True) as txn:
                        txn.delete(encoded_key)
                return True
            except Exception as e:
                logging.error(f"clear_all failed from lmdb: {e}")
                return False

    def update(self,  key: Union[str, bytes], value: Any, txn: Optional[lmdb.Transaction] = None) -> bool:
        return self.insert(key, value, txn)

    def exists(self, key: Union[str, bytes]) -> bool:
        with self._lock:
            try:
                encoded_key = self._encode_key(key)
                with self.env.begin() as txn:
                    return txn.get(encoded_key) is not None
            except Exception as e:
                logging.error(f"query failed from lmdb: key: {key}, error: {e}")
                return False

    def query(self, key: Union[str, bytes], txn: Optional[lmdb.Transaction] = None, default: Any = None) -> Any:
        with self._lock:
            try:
                encoded_key = self._encode_key(key)
                if txn:
                    value_bytes = txn.get(encoded_key)
                    if value_bytes is None:
                        return default
                    return self._decode_value(value_bytes)
                else:
                    with self.env.begin() as txn:
                        value_bytes = txn.get(encoded_key)
                        if value_bytes is None:
                            return default
                        return self._decode_value(value_bytes)
            except Exception as e:
                logging.error(f"item query failed from lmdb: {e}")
                return default

    def query_all(self) -> Dict[str, Any]:
        with self._lock:
            result = {}
            try:
                with self.env.begin() as txn:
                    cursor = txn.cursor()
                    for encoded_key, value_bytes in cursor:
                        key = self._decode_key(encoded_key)
                        value = self._decode_value(value_bytes)
                        result[key] = value
                return result
            except Exception as e:
                logging.error(f"query_all failed from lmdb: {e}")
            return result

    def display(self):
        with self._lock:
            try:
                with self.env.begin() as txn:
                    cursor = txn.cursor()
                    for encoded_key, value_bytes in cursor:
                        key = self._decode_key(encoded_key)
                        value = self._decode_value(value_bytes)
                        print(key, value)
            except Exception as e:
                logging.error(f"display failed from lmdb: {e}")

    def clear_all(self) -> bool:
        with self._lock:
            try:
                with self.env.begin(write=True) as txn:
                    cursor = txn.cursor()
                    for key, _ in cursor:
                        txn.delete(key)
                return True
            except Exception as e:
                logging.error(f"clear_all failed from lmdb: {e}")
                return False

    def backup(self, backup_path: Union[str, Path]) -> bool:
        with self._lock:
            try:
                if isinstance(backup_path, str):
                    backup_path = Path(backup_path)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                with self.env.begin() as txn:
                    with lmdb.open(str(backup_path), map_size=self.map_size) as backup_env:
                        with backup_env.begin(write=True) as backup_txn:
                            cursor = txn.cursor()
                            for encoded_key, value_bytes in cursor:
                                backup_txn.put(encoded_key, value_bytes)

                logging.info(f"database backup from lmdb success: {backup_path}")
                return True
            except Exception as e:
                logging.error(f"database backup from lmdb failed: {e}")
                return False

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with self.env.begin() as txn:
                    stats = txn.stat()
                    info = self.env.info()
                return {
                    'entries': stats['entries'],
                    'depth': stats['depth'],
                    'branch_pages': stats['branch_pages'],
                    'leaf_pages': stats['leaf_pages'],
                    'overflow_pages': stats['overflow_pages'],
                    'map_size': info['map_size'],
                    'last_txnid': info['last_txnid'],
                    'max_readers': info['max_readers'],
                    'num_readers': info['num_readers']
                }
            except Exception as e:
                logging.error(f"fetch database stats failed: {e}")
                return {}

    def close(self):
        with self._lock:
            try:
                if hasattr(self, 'env'):
                    self.env.close()
                logging.info("close database connection successfully.")
            except Exception as e:
                logging.error(f"close database connection failed: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __del__(self):
        """析构函数"""
        self.close()


if __name__ == '__main__':
    db = LMDB(Path(__file__).parent)
    try:
        # 测试不同类型的数据
        test_cases = [
            ("int_value", 12345),
            ("float_value", 123.456),
            ("string_value", "Hello, World!"),
            ("dict_value", {"name": "张三", "age": 25}),
            ("list_value", [1, 2, 3, "a", "b", "c"]),
            ("bytes_value", b"binary_data_here")
        ]
        for k, v in test_cases:
            # 写入数据
            if db.insert(k, v):
                print(f"  ✅ 写入数据成功: {k}")
            else:
                print(f"  ❌ 写入数据失败: {k}")

        print("\n测试更新功能:")
        print(f"更新数据: {db.update(key='int_value', value=1000)}")

        print("\n测试查询功能:")
        print(f"查询数据: {db.query_all()}")

        print("\n测试删除功能:")
        print(f"删除数据: {db.delete(key='int_value')}")

        # 测试统计信息
        stats = db.get_stats()
        print(f"\n数据库统计: {db.count()} 条记录")
        print(f"数据库统计详细信息: {stats}")

        # 测试搜索功能
        print("\n测试搜索功能:")
        print(f"搜索结果: {db.query(key='dict_value')}")

        # 测试删除所有数据功能
        print("\n测试删除所有数据功能:")
        print(f"删除所有数据: {db.clear_all()}")
    finally:
        db.close()


