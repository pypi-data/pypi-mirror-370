from yousign.type.field import Field
from yousign.datasets import DocumentData
from typing import Optional, List, Union


import yousign.type.signature as sign
import yousign.client as client


class Document:
    _client: 'client.Client'
    _signature: 'sign.Signature'
    data: DocumentData
    field: List[Field]

    def __init__(self, client: 'client.Client', signature_id: str, **kwargs):
        self._client = client
        self._signature_id = client.get_signatures(signature_id)
        self.data = DocumentData(**kwargs)

    def update(self) -> None:
        self.data = Document.Data(**self._client.save_document())

    def get_fields(self, id: Optional[str]) -> Union[List[Field] | Field]:
        pass

    def add_field(self, field: Field):
        pass

    def remove_field(self, field: Field) -> None:
        self._client.remove_field(self._signature.data.id, self.id, field.id)
