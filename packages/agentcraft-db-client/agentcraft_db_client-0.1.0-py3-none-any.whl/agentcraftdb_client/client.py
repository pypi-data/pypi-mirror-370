import requests
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional

class CreateIndexRequest(BaseModel):
    index_name: str
    dimension: int
    metric: Optional[str] = "cosine"
    hostname: Optional[str] = None
    cloud: Optional[str] = None
    region: Optional[str] = None
    type_: Optional[str] = None
    capacity: Optional[str] = None
    model: Optional[str] = None

class UpsertRequest(BaseModel):
    index_name: str
    namespace: str
    vectors: List[List[float]]
    ids: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None

    @model_validator(mode="after")
    def check_vectors_and_ids_length(self):
        if len(self.vectors) != len(self.ids):
            raise ValueError("The number of vectors must match the number of ids.")
        return self

class QueryRequest(BaseModel):
    index_name: str
    namespace: str
    vector: List[float]
    filter: Optional[Dict[str, Any]] = None
    top_k: int = 3

class AgentCraftDBClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self):
        return {"X-API-Key": self.api_key}

    def _check_response(self, resp):
        if resp.status_code != 200:
            raise Exception(f"Error: {resp.status_code} - {resp.text}")
        return resp.json()

    def create_index(self, **kwargs):
        req = CreateIndexRequest(**kwargs)
        payload = req.dict()
        resp = requests.post(
            f"{self.base_url}/create_index",
            headers=self._headers(),
            json=payload,
        )
        return self._check_response(resp)

    def upsert(self, **kwargs):
        req = UpsertRequest(**kwargs)
        payload = req.dict()
        resp = requests.post(
            f"{self.base_url}/upsert",
            headers=self._headers(),
            json=payload,
        )
        return self._check_response(resp)

    def query(self, req: QueryRequest):
        resp = requests.post(
            f"{self.base_url}/query",
            headers=self._headers(),
            json={
                "index_name": req.index_name,
                "namespace": req.namespace,
                "vector": req.vector,
                "top_k": req.top_k,
                "filter": req.filter or {},
            },
        )
        return self._check_response(resp)
