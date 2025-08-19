from typing import List

from appodus_utils import Object
from appodus_utils.integrations.document_sign.models import Signer


class GenerateAndSendSignDto(Object):
    template_id: str
    template_variables: dict[str, str]
    contract_id: str
    signers: List[Signer]
    signing_client_name: str
