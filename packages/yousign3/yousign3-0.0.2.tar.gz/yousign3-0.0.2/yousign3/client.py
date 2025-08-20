from typing import Optional, Tuple, Union, List

from yousign3.rest.endpoint import Endpoint
from yousign3.type.signature import Signature
from yousign3.type.signer import Signer
from yousign3.type.document import Document
from yousign3.type.field import Field
from yousign3.rest.request_handler import RequestHandler
from yousign3.datasets import SignatureData, SignerData, DocumentData, \
    Field as FieldData
from io import TextIOWrapper


class Client:
    req_handler: RequestHandler = None

    def __init__(self, token: str, debug: bool = False):
        self.req_handler = RequestHandler(token, debug)

    def create_signature(self, data: SignatureData) -> Signature:
        content = self.req_handler._req(
            "POST",
            Endpoint.get_signatures(),
            RequestHandler.ContentType.JSON,
            json={k: v for k, v in data.__dict__.items() if v is not None}
        )

        return Signature(self, **content)

    def save_signature(self, data: SignatureData) -> None:
        self.req_handler._req(
            "PATCH",
            Endpoint.get_signatures(self.data.id),
            RequestHandler.ContentType.JSON,
            json=data.model_dump_json()
        )

    def change_signature_status(self, signature_id: str, query: str) -> None:
        self.req_handler._req(
            "POST", Endpoint.get_signatures(signature_id, query=query)
        )

    def get_signatures(self, id: Optional[str] = None) -> Union[List[Signature] | Signature]:
        contents = self.req_handler._req(
            "GET", Endpoint.get_signatures(id))

        if id is not None:
            return Signature(self, **contents)

        signatures = []
        for content in contents['data']:
            signatures.append(Signature(self, **content))

        return signatures

    def delete_signature(self, id: Optional[str], permanent: bool = False):
        # Already deleted
        if not permanent and self.status == Signature.RequestStatus.DELETED:
            return

        self.req_handler._req("DELETE",  Endpoint.get_signatures(self.id))

    # Signers

    def create_signer(self, signature_id: str, data: SignerData) -> Signer:
        content = self.req_handler._req(
            "POST",
            Endpoint.get_signers(signature_id),
            RequestHandler.ContentType.JSON,
            json=data.model_dump(exclude_none=True)
        )
        return Signer(self, signature_id, **content)

    def delete_signer(self, signature_id: str, signer_id: str) -> None:
        self.req_handler._req(
            "DELETE",
            Endpoint.get_signers(signature_id, signer_id),
            RequestHandler.ContentType.JSON,
        )

    def get_signers(self, signature_id: str, signer_id: Optional[str] = None) -> Union[List[Signer] | Signer]:
        content = self.req_handler._req(
            "GET",
            Endpoint.get_signers(signature_id, signer_id),
            RequestHandler.ContentType.JSON,
        )

        if signer_id is not None:
            return Signer(self, signature_id, **content)

        signers = []
        for content in content['data']:
            signers.append(Signer(self, signature_id, **content))

        return signers

    def save_signer(self, signature_id: str, signer_id: str, data: SignerData) -> None:
        self.req_handler._req(
            "PATCH",
            Endpoint.get_signers(signature_id, signer_id),
            RequestHandler.ContentType.JSON,
            json=data.model_dump()
        )

    # Document

    def create_document(
            self,
            signature_id: str,
            document: DocumentData,
            file: Tuple[str, TextIOWrapper, str]
    ) -> Document:
        content = self.req_handler._req(
            "POST",
            Endpoint.get_documents(signature_id),
            RequestHandler.ContentType.NONE,
            files={"file": file},
            data=document.model_dump(exclude_none=True)
        )

        return Document(self, signature_id, **content)

    def delete_document(self, signature_id: str, document_id: str) -> None:
        self.req_handler._req(
            "DELETE",
            Endpoint.get_documents(signature_id, document_id),
            RequestHandler.ContentType.NONE,
        )

    def get_documents(self, signature_id: str, document_id: Optional[str] = None) -> Union[List[Document] | Document]:
        content = self.req_handler._req(
            "DELETE",
            Endpoint.get_documents(signature_id, document_id),
        )

        if document_id is not None:
            return Document(self, **content)

        documents = []
        for content in content['data']:
            documents.append(Document(self, **content))

        return documents

    def save_document(self, signature_id: str, document_id: str, data: DocumentData) -> None:
        self.req_handler._req(
            "PATCH",
            Endpoint.get_documents(signature_id, document_id),
            RequestHandler.ContentType.JSON,
            json=data.model_dump()
        )

    # Approvers
    def create_approvers(self):
        pass

    def get_approvers(self):
        pass

    def delete_approvers(self):
        pass

    # Fields

    def create_fields(self, signature_id: str, document_id: str, field: FieldData) -> Field:
        content = self.req_handler._req(
            "POST",
            Endpoint.get_fields(signature_id, document_id),
            RequestHandler.ContentType.JSON,
            json=field.model_json_dump(exclude_none=True),
        )

        return Field(self, **content)

    def delete_fields(self, signature_id: str, document_id: str, field_id: str) -> None:
        self.req_handler._req(
            "DELETE",
            Endpoint.get_fields(signature_id, document_id, field_id),
        )
