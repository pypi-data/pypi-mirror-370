import dataclasses
import datetime
from typing import List
from typing import Optional

from eval_studio_client import api
from eval_studio_client.api import models


@dataclasses.dataclass
class Document:
    """Represents a document in Eval Studio, that can be uploaded to RAG system.

    Attributes:
        key (str): Generated ID of the document.
        name (str): Display name of the document.
        description (str): Description of the document.
        url (str): URL of the document.
        create_time (datetime): Timestamp of the document creation.
        update_time (datetime): Timestamp of the last document update.
    """

    key: str
    name: str
    description: str
    url: str
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None
    _client: Optional[api.ApiClient] = None

    def __post_init__(self):
        if self._client:
            self._document_api = api.DocumentServiceApi(self._client)

    def delete(self):
        """Deletes the document."""
        self._document_api.document_service_delete_document(self.key)

    def to_api_proto(self) -> models.V1Document:
        """Converts the client Document to an API Document."""
        return models.V1Document(
            display_name=self.name, description=self.description, url=self.url
        )

    @staticmethod
    def _from_api_document(
        api_document: models.V1Document, client: Optional[api.ApiClient]
    ) -> "Document":
        """Converts an API Document to a client Document."""
        return Document(
            key=api_document.name or "",
            name=api_document.display_name or "",
            description=api_document.description or "",
            url=api_document.url or "",
            create_time=api_document.create_time or None,
            update_time=api_document.update_time or None,
            _client=client,
        )


class _Documents:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.DocumentServiceApi(client)

    def get(self, key: str) -> Document:
        """Retrieves a document by its resource name.

        Args:
            key: The document resource name to retrieve.

        Returns:
            The document with the given resource name.
        """
        res = self._api.document_service_get_document(key)
        if res and res.document:
            return Document._from_api_document(res.document, self._client)

        raise KeyError("Document not found.")

    def list(self) -> List[Document]:
        """List all user documents in Eval Studio."""
        res = self._api.document_service_list_documents()
        if res and res.documents:
            return [Document._from_api_document(d, self._client) for d in res.documents]

        return []

    def delete(self, key: str):
        """Deletes the document with the given resource name from the Eval Studio.

        Args:
            key: The document resource name to delete.
        """
        self._api.document_service_delete_document(key)
