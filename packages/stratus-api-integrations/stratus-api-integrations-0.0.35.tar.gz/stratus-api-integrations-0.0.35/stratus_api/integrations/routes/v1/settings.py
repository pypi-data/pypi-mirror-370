def get_settings_request(user, token_info):
    from stratus_api.integrations.base import get_integration_settings
    return dict(active=True, response=get_integration_settings())
