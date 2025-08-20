from typing import List, Tuple
from yousign3.datasets import SignatureData, SignerData, DocumentData
import yousign3.client as ys_client
import yousign3.type.document as doc
import yousign3.type.signer as signer
from io import TextIOWrapper


class Signature:
    client: 'ys_client.Client'
    data: SignatureData
    signers: List['signer.Signer'] = []
    documents: List['doc.Document'] = []

    def __init__(self, client: 'ys_client.Client', **kwargs):
        self.client = client
        signers = kwargs.pop('signers', [])
        documents = kwargs.pop('documents', [])
        labels = kwargs.pop('labels', [])
        approvers = kwargs.pop('approvers', [])
        fields = kwargs.pop('fields', [])
        sender = kwargs.pop('sender', [])
        decline_information = kwargs.pop('decline_information', None)

        self.data = SignatureData(**kwargs)

    def delete(self):
        self.client.delete_signature(self.data.id)

    def activate(self):
        self.client.change_signature_status(self.data.id, 'activate')

    def reactivate(self):
        self.client.change_signature_status(self.data.id, 'reactivate')

    def cancel(self):
        self.client.change_signature_status(self.data.id, 'cancel')

    # Signer

    def add_signer(self, signer: SignerData):
        self.client.create_signer(self.data.id, signer)

    def rem_signer(self, signer_id: str):
        self.client.delete_signer(self.data.id, signer_id)

    def get_signers(self):
        return self.client.get_signers(self.data.id)

    # Document

    def add_doc(self, document: DocumentData, file: Tuple[str, TextIOWrapper, str]):
        doc = self.client.create_document(self.data.id, document, file)
        self.documents.append(doc)
        return doc

    def rem_document(self, document_id: str):
        self.client.rem(self.data.id, document_id)

    def get_documents(self):
        return self.client.get_documents(self.data.id)
