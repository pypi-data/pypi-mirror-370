# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 不支持多进程
"""
pip install tinydb
"""
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.table import Document
from typing import (
    List,
    Mapping,
    TypeVar
)


class Entity:

    def __init__(self, document: Document = None):
        self.doc_id = None
        if document is not None:
            self.__dict__ = document

    def __call__(self, *args, **kwargs):
        pass

    def update(self, document: Document = None):
        if document is not None:
            self.__dict__.update(document)
            self.doc_id = document.doc_id
        return self

    def mapping(self):
        dic = self.__dict__
        if "doc_id" in dic:
            dic.pop("doc_id")
        return dic


T = TypeVar("T", bound=Entity)


class TINYDB:
    def __init__(self, db_dir: Path, db_name="db"):
        self.db = TinyDB(db_dir.joinpath("{0}.json".format(db_name)))

    def insert(self, document: Mapping) -> int:
        return self.db.insert(document)

    def insert_if_not_exist(self, document: Mapping, cond=None, doc_id=None) -> int:
        if self.db.contains(cond, doc_id):
            return -1
        return self.db.insert(document)

    def contains(self, cond=None, doc_id=None) -> bool:
        return self.db.contains(cond, doc_id)

    def search(self, cond=None) -> list:
        return self.db.search(cond)

    def query(self, obj: T, cond=None) -> List[T]:
        if cond:
            docs = self.db.search(cond)
        else:
            docs = self.db.all()
        return [obj.update(i) for i in docs]

    def query_all(self) -> List[Document]:
        return self.db.all()

    def update(self, fields, cond=None, doc_ids=None) -> List[int]:
        return self.db.update(fields, cond, doc_ids)

    def count(self, cond) -> int:
        return self.db.count(cond)

    def remove(self, cond, doc_ids) -> List[int]:
        return self.db.remove(cond, doc_ids)

    def remove_all(self):
        self.db.truncate()

    @staticmethod
    def query_ins():
        return Query()


if __name__ == "__main__":
    # from configure import DBDir
    # db = TINYDB(Path(__file__).parent, "test")

    # data = db.query_all()
    # print(data)

    # db.remove_all()
    # print(db.insert_if_not_exist({'task_id': 3, 'task_dir': '/root/image', 'task_status': 2}, db.query_ins().task_id == 3))

    # for item in db.query(obj=Entity()):
    #     print(item.__dict__)

    # result_ = db.query_all_return_class(obj=Note())
    # print(result_[0].task_id)

    # print(db.update(fields={"task_status": 0}, cond=None, doc_ids=[result.doc_id]))
    # print(db.update(fields={"task_status": 2}, cond=None, doc_ids=[result.doc_id]))
    pass

