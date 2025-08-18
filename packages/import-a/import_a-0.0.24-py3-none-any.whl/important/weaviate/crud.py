from typing import Callable, List, Optional
from uuid import uuid4

import numpy as np
from weaviate.client import Client
from weaviate.util import get_valid_uuid
import yaml

from important.weaviate.utils import _capitalize_first_letter, _json_serializable, cosine_similarity


class WeaviateCRUD:
    """
    Weaviate CRUD operations.

    A wrapper around the weaviate client.
    As an alternative to the langchain weaviate client.
    """

    def __init__(
        self,
        client: Client,
        class_name: str,
        embedder,
        embedder_name: Optional[str] = None,
    ):
        self.client = client
        self.class_name: str = class_name
        self.embedder = embedder

        if embedder_name is None:
            self.embedder_name = embedder.model
        else:
            self.embedder_name = embedder_name

    def __repr__(self) -> str:
        return f"WeaviateCRUD(class_name={self.class_name}, model={self.embedder_name})"

    @property
    def property_names(self) -> List[str]:
        """
        Get the properties of a class.
        """
        classes = self.client.schema.get()["classes"]

        # find_class_data
        class_data = None
        for class_data_ in classes:
            if class_data_["class"] == self.class_name:
                class_data = class_data_
                break
        if class_data is None:
            raise ValueError(f"Class {self.class_name} not found")

        name_list = [prop["name"] for prop in class_data["properties"]]
        return name_list

    def create(
        self,
        text: str,
        **metadata,
    ) -> str:
        """
        Create a vector in the vector database.
        The text will be vectorized and
        """
        vector = self.embedder.embed_query(text)

        if len(metadata) > 0:
            metadata = {key: _json_serializable(value) for key, value in metadata.items()}

        metadata["page_content"] = text
        metadata["model"] = self.embedder_name

        _id = get_valid_uuid(uuid4())

        return self.client.data_object.create(
            data_object=metadata,
            class_name=_capitalize_first_letter(self.class_name),
            uuid=_id,
            vector=vector,
        )

    def update_by_id(
        self,
        uuid: str,
        text: str,
        **metadata,
    ) -> None:
        """
        Upload text, metadata and vector to the vector database.
        """
        metadata["page_content"] = text
        self.client.data_object.update(
            data_object=metadata,
            class_name=_capitalize_first_letter(self.class_name),
            vector=self.embedder.embed_query(text),
            uuid=uuid,
        )

    def delete_by_id(
        self,
        uuid: str,
    ) -> None:
        """
        Delete an entry by id.
        """
        self.client.data_object.delete(
            class_name=_capitalize_first_letter(self.class_name),
            uuid=uuid,
        )

    def search(
        self,
        query: str,
        limit: int = 10,
        return_score: bool = True,
        min_threshould: Optional[float] = None,
        **metadata,
    ):
        """
        Search with a query
        qeury: str, search query text
        limit: int, limit of results
        return_score: bool, return score or not
        min_threshould: float, minimum score threshold, if set,
            only results with score >= min_threshould will be returned,
            it might be less than limit.
        metadata are the key and value pairs of the properties.
        """
        vector = self.embedder.embed_query(query)

        query_obj = self.client.query.get(
            class_name=self.class_name,
            properties=list(self.property_names),
        )

        # equal filters
        for key, value in metadata.items():
            query_obj = query_obj.with_where(
                {
                    "operator": "Equal",
                    "path": key,
                    "valueString": value,
                }
            )

        # rank with vector
        query_obj = query_obj.with_near_vector(
            {"vector": vector},
        )

        if return_score or (min_threshould is not None):
            query_obj = query_obj.with_additional("vector")

        res = query_obj.with_limit(limit=limit).do()

        if "error" in res:
            raise ValueError(res)

        results = res["data"]["Get"][self.class_name]

        if return_score or (min_threshould is not None):
            for result in results:
                res_vec = result["_additional"]["vector"]
                result["score"] = cosine_similarity(np.array(vector), res_vec)
                del result["_additional"]

        if min_threshould is not None:
            results = [result for result in results if result["score"] >= min_threshould]
        return results

    def filter_read(self, limit: Optional[int] = None, **metadata):
        """
        Filter by metadata matching.
        Return all entries that match all the key value pairs in metadata.
        """
        query_obj = self.client.query.get(
            class_name=self.class_name,
            properties=list(self.property_names),
        )
        for key, value in metadata.items():
            query_obj = query_obj.with_where(
                {
                    "operator": "Equal",
                    "path": key,
                    "valueString": value,
                }
            )
        query_obj = query_obj.with_additional("id")
        if limit is not None:
            query_obj = query_obj.with_limit(limit=limit)
        res = query_obj.do()
        if ("error" in res) or ("errors" in res):
            raise ValueError(res)
        results = res["data"]["Get"][self.class_name]
        for res in results:
            res["id"] = res["_additional"]["id"]
            del res["_additional"]
        return results

    def filter_delete(self, **metadata):
        """
        Delete all entries that match all the key value pairs in metadata.
        """
        results = self.filter_read(**metadata)
        for result in results:
            self.delete_by_id(result["id"])

    def info_data(
        self,
    ):
        classes_return = dict()
        for class_data in self.client.schema.get()["classes"]:
            classes = dict()
            classes["name"] = class_data["class"]
            properties = dict()
            for property_data in class_data["properties"]:
                properties[property_data["name"]] = dict(
                    data_type=property_data["dataType"],
                    name=property_data["name"],
                    index_filterable=property_data["indexFilterable"],
                    index_searchable=property_data["indexSearchable"],
                )
            classes["properties"] = properties
            retrieved_objects = self.client.data_object.get(
                class_name=class_data["class"],
            )
            if retrieved_objects is None:
                classes["total_count"] = 0
            elif "totalResults" not in retrieved_objects:
                classes["total_count"] = 0
            else:
                classes["total_count"] = retrieved_objects["totalResults"]

            classes_return[class_data["class"]] = classes
        return dict(
            classes=classes_return,
        )

    def info(
        self,
    ):
        """
        Print the info of the weaviate data schema
        In yaml format.
        """
        print(yaml.dump(self.info_data()))
