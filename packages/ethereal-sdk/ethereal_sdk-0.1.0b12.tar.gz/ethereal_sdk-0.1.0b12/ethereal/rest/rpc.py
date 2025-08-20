from ethereal.constants import API_PREFIX
from ethereal.models.rest import RpcConfigDto, SignatureTypesDto, DomainTypeDto


def get_rpc_config(self, **kwargs) -> RpcConfigDto:
    """Gets RPC configuration.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        RpcConfigDto: EIP-712 Domain Data necessary for message signing.
    """
    endpoint = f"{API_PREFIX}/rpc/config"

    res = self.get(endpoint, **kwargs)
    domain = DomainTypeDto(**res["domain"])
    signature_types = SignatureTypesDto(**res["signatureTypes"])
    return RpcConfigDto(domain=domain, signatureTypes=signature_types)
