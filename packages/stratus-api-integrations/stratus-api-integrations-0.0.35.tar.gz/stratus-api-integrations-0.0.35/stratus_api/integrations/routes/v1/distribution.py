def distribute_file_request(user, token_info, body):
    from stratus_api.integrations.tasks.distributions import deliver_data_task, chunk_data_task
    from stratus_api.integrations.base import validate_platform_name, get_integration_settings
    from stratus_api.core.common import generate_random_id
    from stratus_api.core.exceptions import ApiError
    from stratus_api.core.settings import get_app_settings
    try:
        validate_platform_name(body['platform_name'])
    except ApiError as e:
        return dict(status=400, title='Bad Request', detail=e.args[0], type='about:blank'), 400
    else:
        app_settings = get_app_settings()
        eta = None
        if app_settings.get('is_distribution_limit', False):
            eta = get_distribution_eta(segment=body['segments'][0])
        job_uuid = generate_random_id()
        if get_integration_settings()['parallelize']:
            chunk_data_task.s(**body, job_uuid=job_uuid).apply_async(eta=eta)
        else:
            deliver_data_task.s(**body, job_uuid=job_uuid).apply_async(eta=eta)
        return dict(active=True, response=dict(job_uuid=job_uuid)), 200


def get_distribution_eta(segment):
    """
        checks if ETA is set at platform level or segment level and returns if value present
    :param segment:
    :return:
    """
    from datetime import datetime
    from stratus_api.core.settings import get_app_settings
    from stratus_api.integrations.cache import get_cached_data

    app_settings = get_app_settings()
    platform_name = app_settings['platform_name']
    date_format = app_settings.get('distribution_eta_date_format', '%d-%m-%Y %H:%M:%S')
    eta_info = None
    if app_settings['distribution_limit_level'] == 'platform_level':
        eta_info = get_cached_data(f"{platform_name}_eta_info")
    elif app_settings['distribution_limit_level'] == 'segment_level':
        segment_uuid = segment['segment_uuid'].replace('-', '_')
        eta_info = get_cached_data(f"{platform_name}_{segment_uuid}_eta_info")
    if eta_info:
        return datetime.strptime(eta_info['eta'], date_format)
    return None
