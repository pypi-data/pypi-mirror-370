"""DocDB retriever class that communicates with MongoDB"""

import logging
from typing import Any, List

from aind_data_access_api.document_db import MetadataDbClient
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

# from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

dimensions = 1024
model_name = "mixedbread-ai/mxbai-embed-large-v1"
encode_kwargs = {"prompt_name": "query"}

# hf = HuggingFaceEmbeddings(
#     model_name=model_name,
#     encode_kwargs=encode_kwargs
# )

model = SentenceTransformer(model_name, truncate_dim=dimensions)


API_GATEWAY_HOST = "api.allenneuraldynamics-test.org"
DATABASE = "metadata_vector_index"
# COLLECTION = "data_schema_fields_index"
# COLLECTION = "data_schema_defs_index"
# COLLECTION = "data_schema_core_index"


class SchemaContextRetriever(BaseRetriever):
    """
    A retriever that contains the top k documents, retrieved
    from the DocDB index, aligned with the user's query.
    """

    k: int = Field(default=5, description="Number of documents to retrieve")
    collection: str = Field(description="MongoDB collection to retrieve from")

    def _get_relevant_documents(self, query: str, **kwargs: Any) -> List:
        """Synchronous retriever"""
        # For synchronous calls, we need to handle this differently
        # This method should not be used in async contexts
        raise NotImplementedError(
            "Use _aget_relevant_documents for async contexts"
        )

    async def _aget_relevant_documents(
        self,
        query: str,
    ) -> List:
        """Asynchronous retriever"""

        docdb_api_client = MetadataDbClient(
            host=API_GATEWAY_HOST,
            database=DATABASE,
            collection=self.collection,
        )

        embedded_query = model.encode(query, prompt_name="query").tolist()

        # embedded_query = await hf.aembed_query(query)

        # Construct aggregation pipeline
        vector_search = {
            "$search": {
                "vectorSearch": {
                    "vector": embedded_query,
                    "path": "vector_embeddings",
                    "similarity": "cosine",
                    "k": self.k,
                    "efSearch": 250,
                }
            }
        }

        projection_stage = {"$project": {"text": 1, "_id": 0}}

        pipeline = [vector_search, projection_stage]

        try:
            logging.info("Starting vector search")
            result = docdb_api_client.aggregate_docdb_records(
                pipeline=pipeline
            )

            return result

        except Exception as e:
            print(e)


# import asyncio
# query = "subject procedures"


# retriever = SchemaContextRetriever(k=4, collection="data_schema_core_index")
# documents = asyncio.run(retriever._aget_relevant_documents(query=query))
# for i in documents:
#     print(type(i))
