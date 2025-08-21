from dataclasses import asdict

from microsoft import MSGraphAPI

from sepp.settings import ms_graph_config

# generate new ms refresh token
ms_api = MSGraphAPI(**asdict(ms_graph_config))

ms_api.create_access_token()
