# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
"""
pip install chromadb
pip3 install typing_extensions

eg:

import numpy as np
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
from chromadb.api.collection_configuration import (
            CreateCollectionConfiguration,
            CreateHNSWConfiguration
        )

class MyEmbeddingFunction(EmbeddingFunction):

    def __init__(self):
        pass

    def __call__(self, doc: Documents) -> Embeddings:
        embeddings = []
        demo = {
            "苹果": np.asarray([0.1, 0.2, 0.3]),
            "香蕉": np.asarray([0.2, 0.1, 0.4]),
            "橘子": np.asarray([0.15, 0.22, 0.35]),
            "橙子": np.asarray([0.15, 0.22, 0.5]),
        }
        for item in doc:
            embeddings.append(demo.get(item))
        return embeddings


master = ChromaDBMaster().create_collection(name="my_collection",
                                            configuration=CreateCollectionConfiguration(hnsw=CreateHNSWConfiguration(space="ip")),
                                            embedding_function=MyEmbeddingFunction())
master.add(
    ids=["id1", "id2", "id3"],
    documents=["苹果", "香蕉", "橘子"],
)
results = master.query(
    query_texts=["橙子"],
    n_results=3
)
print(results)
"""
from pathlib import Path
from typing import Union, Optional
from chromadb.api.models.Collection import Collection
import chromadb.utils.embedding_functions as ef
from chromadb.api.collection_configuration import (
    CreateCollectionConfiguration,
)

import chromadb
from chromadb.api.types import (
    Embeddable,
    EmbeddingFunction,
    DataLoader,
    Loadable,
    URI,
    CollectionMetadata,
    Embedding,
    PyEmbedding,
    Metadata,
    Document,
    Image,
    Where,
    IDs,
    GetResult,
    QueryResult,
    ID,
    OneOrMany,
    WhereDocument,
)


class ChromaDBMaster:
    def __init__(self, path: Union[str, Path] = None):
        """

        :param path: 保存数据库的目录，非空时则为持久化数据库，eg: .chromadb
        """
        self.chroma_client = chromadb.PersistentClient(path=path) if path else chromadb.Client()
        self.collection = None

    def create_collection(self, name: str,
                          configuration: Optional[CreateCollectionConfiguration] = None,
                          metadata: Optional[CollectionMetadata] = None,
                          embedding_function: Optional[
                              EmbeddingFunction[Embeddable]
                          ] = ef.DefaultEmbeddingFunction(),
                          data_loader: Optional[DataLoader[Loadable]] = None,
                          get_or_create: bool = False)-> Collection:
        """Create a new collection with the given name and metadata.
               Args:
                   name: The name of the collection to create.
                   configuration:
                        {"hnsw": {"space": "ip"}}  内积
                        {"hnsw": {"space": "cosine"}} 余弦距离
                        {"hnsw": {"space": "l2"}} 欧式距离
                   metadata: Optional metadata to associate with the collection.
                   embedding_function: Optional function to use to embed documents.
                                       Uses the default embedding function if not provided.
                   get_or_create: If True, return the existing collection if it exists.
                   data_loader: Optional function to use to load records (documents, images, etc.)

               Returns:
                   Collection: The newly created collection.

               Raises:
                   ValueError: If the collection already exists and get_or_create is False.
                   ValueError: If the collection name is invalid.

               Examples:
                   ```python
                   client.create_collection("my_collection")
                   # collection(name="my_collection", metadata={})

                   client.create_collection("my_collection", metadata={"foo": "bar"})
                   # collection(name="my_collection", metadata={"foo": "bar"})
                   ```
               """
        params = locals().copy()
        params.pop("self")
        self.collection = self.chroma_client.create_collection(**params)
        return self.collection

    def count(self) -> int:
        """The total number of embeddings added to the database

        Returns:
            int: The total number of embeddings added to the database

        """
        return self.collection.count()

    def add(self,
            ids: OneOrMany[ID] = None,
            embeddings: Optional[Union[OneOrMany[Embedding], OneOrMany[PyEmbedding]]] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
            images: Optional[OneOrMany[Image]] = None,
            uris: Optional[OneOrMany[URI]] = None) -> None:
        """Add embeddings to the data store.
        Args:
            ids: The ids of the embeddings you wish to add
            embeddings: The embeddings to add. If None, embeddings will be computed based on the documents or images using the embedding_function set for the Collection. Optional.
            metadatas: The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.
            images: The images to associate with the embeddings. Optional.
            uris: The uris of the images to associate with the embeddings. Optional.

        Returns:
            None

        Raises:
            ValueError: If you don't provide either embeddings or documents
            ValueError: If the length of ids, embeddings, metadatas, or documents don't match
            ValueError: If you don't provide an embedding function and don't provide embeddings
            ValueError: If you provide both embeddings and documents
            ValueError: If you provide an id that already exists

        """
        if ids is None:
            index = self.count()
            if documents:
                ids = [str(index + i) for i in range(1, len(documents) + 1)]
            if embeddings:
                ids = [str(index + i) for i in range(1, len(embeddings) + 1)]
        params = locals().copy()
        params.pop("self")
        if "index" in params:
            params.pop("index")
        self.collection.add(**params)

    def query(
            self,
            query_embeddings: Optional[
                Union[
                    OneOrMany[Embedding],
                    OneOrMany[PyEmbedding],
                ]
            ] = None,
            query_texts: Optional[OneOrMany[Document]] = None,
            query_images: Optional[OneOrMany[Image]] = None,
            query_uris: Optional[OneOrMany[URI]] = None,
            ids: Optional[OneOrMany[ID]] = None,
            n_results: int = 10,
            where: Optional[Where] = None,
            where_document: Optional[WhereDocument] = None,
            include=None,
    ) -> QueryResult:
        """Get the n_results nearest neighbor embeddings for provided query_embeddings or query_texts.

        Args:
            query_embeddings: The embeddings to get the closes neighbors of. Optional.
            query_texts: The document texts to get the closes neighbors of. Optional.
            query_images: The images to get the closes neighbors of. Optional.
            query_uris: The URIs to be used with data loader. Optional.
            ids: A subset of ids to search within. Optional.
            n_results: The number of neighbors to return for each query_embedding or query_texts. Optional.
            where: A Where type dict used to filter results by. E.g. `{"$and": [{"color" : "red"}, {"price": {"$gte": 4.20}}]}`. Optional.
            where_document: A WhereDocument type dict used to filter by the documents. E.g. `{"$contains": "hello"}`. Optional.
            include: A list of what to include in the results. Can contain `"embeddings"`, `"metadatas"`, `"documents"`, `"distances"`. Ids are always included. Defaults to `["metadatas", "documents", "distances"]`. Optional.

        Returns:
            QueryResult: A QueryResult object containing the results.

        Raises:
            ValueError: If you don't provide either query_embeddings, query_texts, or query_images
            ValueError: If you provide both query_embeddings and query_texts
            ValueError: If you provide both query_embeddings and query_images
            ValueError: If you provide both query_texts and query_images

        """
        if include is None:
            include = ["metadatas", "documents", "distances"]
        params = locals().copy()
        params.pop("self")
        return self.collection.query(**params)

    def get(
            self,
            ids: Optional[OneOrMany[ID]] = None,
            where: Optional[Where] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            where_document: Optional[WhereDocument] = None,
            include=None,
    ) -> GetResult:
        """Get embeddings and their associate data from the data store. If no ids or where filter is provided returns
        all embeddings up to limit starting at offset.

        Args:
            ids: The ids of the embeddings to get. Optional.
            where: A Where type dict used to filter results by. E.g. `{"$and": [{"color" : "red"}, {"price": {"$gte": 4.20}}]}`. Optional.
            limit: The number of documents to return. Optional.
            offset: The offset to start returning results from. Useful for paging results with limit. Optional.
            where_document: A WhereDocument type dict used to filter by the documents. E.g. `{"$contains": "hello"}`. Optional.
            include: A list of what to include in the results. Can contain `"embeddings"`, `"metadatas"`, `"documents"`. Ids are always included. Defaults to `["metadatas", "documents"]`. Optional.

        Returns:
            GetResult: A GetResult object containing the results.

        """
        if include is None:
            include = ["metadatas", "documents"]
        params = locals().copy()
        params.pop("self")
        return self.collection.get(**params)

    def update(
            self,
            ids: OneOrMany[ID],
            embeddings: Optional[
                Union[
                    OneOrMany[Embedding],
                    OneOrMany[PyEmbedding],
                ]
            ] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
            images: Optional[OneOrMany[Image]] = None,
            uris: Optional[OneOrMany[URI]] = None,
    ) -> None:
        """Update the embeddings, metadatas or documents for provided ids.

        Args:
            ids: The ids of the embeddings to update
            embeddings: The embeddings to update. If None, embeddings will be computed based on the documents or images using the embedding_function set for the Collection. Optional.
            metadatas:  The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.
            images: The images to associate with the embeddings. Optional.
            uris: The uris of the images to associate with the embeddings. Optional.
        Returns:
            None
        """
        params = locals().copy()
        params.pop("self")
        self.collection.update(**params)

    def upsert(
            self,
            ids: OneOrMany[ID],
            embeddings: Optional[
                Union[
                    OneOrMany[Embedding],
                    OneOrMany[PyEmbedding],
                ]
            ] = None,
            metadatas: Optional[OneOrMany[Metadata]] = None,
            documents: Optional[OneOrMany[Document]] = None,
            images: Optional[OneOrMany[Image]] = None,
            uris: Optional[OneOrMany[URI]] = None,
    ) -> None:
        """Update the embeddings, metadatas or documents for provided ids, or create them if they don't exist.

        Args:
            ids: The ids of the embeddings to update
            embeddings: The embeddings to add. If None, embeddings will be computed based on the documents using the embedding_function set for the Collection. Optional.
            metadatas:  The metadata to associate with the embeddings. When querying, you can filter on this metadata. Optional.
            documents: The documents to associate with the embeddings. Optional.
            images: The images to associate with the embeddings. Optional.
            uris: The uris of the images to associate with the embeddings. Optional.
        Returns:
            None
        """
        params = locals().copy()
        params.pop("self")
        self.collection.upsert(**params)

    def delete(
            self,
            ids: Optional[IDs] = None,
            where: Optional[Where] = None,
            where_document: Optional[WhereDocument] = None,
    ) -> None:
        """Delete the embeddings based on ids and/or a where filter

        Args:
            ids: The ids of the embeddings to delete
            where: A Where type dict used to filter the delection by. E.g. `{"$and": [{"color" : "red"}, {"price": {"$gte": 4.20}]}}`. Optional.
            where_document: A WhereDocument type dict used to filter the deletion by the document content. E.g. `{"$contains": "hello"}`. Optional.

        Returns:
            None

        Raises:
            ValueError: If you don't provide either ids, where, or where_document
        """
        params = locals().copy()
        params.pop("self")
        self.collection.delete(**params)


