from tiled.client.array import ArrayClient
from ..xas import XAS


class XASClient(ArrayClient):
    def to_xas(self):
        data = self.read()
        header = self.metadata
        return XAS.from_data_header(data, header)
    
def xas_client(*args, **kwargs):
    ac = ArrayClient(*args, **kwargs)
    data = ac.read()
    header = ac.metadata
    return XAS.from_data_header(data, header)
