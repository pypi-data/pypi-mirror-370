def create_destination_request(user, token_info, body):
    from stratus_api.integrations import create_entity
    from stratus_api.core.exceptions import ApiError
    try:
        external_id, external_attributes = create_entity(
            entity_type='destination', name=body['name'],
            platform_name=body['platform_name'],
            destination_uuid=body['destination_uuid'], settings=body['settings'],
            token_info=token_info, account_uuid=body.get('account_uuid'), product_uuid=body.get('product_uuid'),
        )
    except ApiError as e:
        return dict(status=400, title='Bad Request', detail=e.args[0], type='about:blank'), 400
    else:
        return dict(active=True, response=dict(external_id=external_id, external_attributes=external_attributes))


def get_destination_template_request(user, token_info, platform_name):
    from stratus_api.integrations import get_integration_function, validate_platform_name
    from stratus_api.core.exceptions import ApiError
    try:
        validate_platform_name(platform_name)
        template = get_integration_function(function_name='get_destination_template')(platform_name=platform_name)
    except ApiError as e:
        return dict(status=400, title='Bad Request', detail=e.args[0], type='about:blank'), 400
    else:
        return dict(active=True, response=template)
