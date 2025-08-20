from yousign3.type.field import Field
from yousign3.datasets import DocumentData
import yousign3.type.signature as sign
import yousign3.client as client
from typing import Optional, List, Union


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
