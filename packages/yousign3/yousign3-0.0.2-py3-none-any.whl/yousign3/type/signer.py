from typing import Self
from yousign3.datasets import SignerData
"avoid circular import"
import yousign3.client as client
import yousign3.type.signature as sign


class Signer:
    _client: 'client.Client'
    _signature: 'sign.Signature'
    data: SignerData

    def __init__(self, client: 'client.Client', signature_id: str, **kwargs) -> Self:
        self._client = client
        self._signature = client.get_signatures(signature_id)
        self.data = SignerData(**kwargs)

    def update(self):
        content = self._client.get_signers(self.id)
        self.data = SignerData(**content)

    def delete(self):
        self._client.delete_signer(self._signature.id, self.id)

    def save(self):
        pass
