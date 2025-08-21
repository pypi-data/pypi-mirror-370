from microsoft import MSGraphAPI

from sepp.settings import (
    MS_CLIENT_ID,
    MS_CLIENT_SECRET,
    MS_REDIRECT_URI,
    MS_REFRESH_TOKEN_URL,
    MS_SCOPE,
    MS_TENANT_ID,
)

# generate new ms refresh token
ms_api = MSGraphAPI(
    tenant_id=MS_TENANT_ID,
    client_id=MS_CLIENT_ID,
    client_secret=MS_CLIENT_SECRET,
    scope=MS_SCOPE,
    redirect_uri=MS_REDIRECT_URI,
    refresh_token_url=MS_REFRESH_TOKEN_URL,
)

ms_api.create_access_token()
