from typing import Optional


class Endpoint:
    BASE = 'https://api-sandbox.yousign.app/v3/signature_requests'

    def get_signatures(
            signature_id: Optional[str] = None,
            **kwargs
    ) -> str:
        url = Endpoint.BASE

        if signature_id is None:
            return url

        url += f"/{signature_id}"

        query = kwargs.get('query', None)
        if query is not None and query in ['activate', 'cancel', 'reactivate']:
            return f"{url}/{query}"

        permanent_delete = kwargs.get('permanent_delete', False)
        if permanent_delete:
            return f"{url}/?permanent_delete={permanent_delete}"

        return url

    def get_documents(
            signature_id: str,
            document_id: Optional[str] = None,
            **kwargs
    ) -> str:
        url = Endpoint.get_signatures(signature_id) + "/documents"

        if document_id is None:
            return url

        url += f"/{document_id}"

        query = kwargs.get('query', None)
        if query is not None and query in ['replace', 'download']:
            url += f"/{query}"

            # Some params
            if query == Endpoint.DocumentQuery.DOWNLOAD:
                # To do
                _ = kwargs.get('version', None)
                _ = kwargs.get('archive', None)

        return url

    def get_signers(
            signature_id: str,
            signer_id: Optional[str] = None,
            **kwargs
    ) -> str:
        url = Endpoint.get_signatures(signature_id) + "/signers"

        if signer_id is None:
            return url

        url += f"{url}/{signer_id}"

        query = kwargs.get('query', None)

        allowed_queries = ['send_reminder', 'send_otp', 'identity_verification',
                           'sign', 'unblock_identification']

        if query is not None and query in allowed_queries:
            return f"{url}/{query}"

        return url

    def get_approvers(
            signature_id: str,
            approver_id: Optional[str] = None,
            send_reminder: bool = False
    ) -> str:
        url = Endpoint.get_signatures(signature_id) + "/approvers"

        if approver_id is None:
            return url

        url += f"{approver_id}"

        if send_reminder:
            return f"{url}/send_reminder"

        return url

    def get_fields(
            signature_id: str,
            document_id: str,
            field_id: Optional[str] = None,
            answer: bool = False
    ) -> str:
        url = Endpoint.get_documents(signature_id, document_id) + "/fields"

        if field_id is None:
            return url

        url += f"/{field_id}"

        if answer:
            url += "/answer"

        return url

    def get_followers(signature_id: str) -> str:
        return f"{Endpoint.get_signatures(signature_id)}/followe"
