def download_performance_report_request(body):
    from stratus_api.integrations import get_integration_function, validate_platform_name
    from stratus_api.integrations.tasks.performances import download_performances_report_task
    from stratus_api.core.exceptions import ApiError
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    body['start_date'] = body.get('start_date') if body.get('start_date') else today
    body['end_date'] = body.get('end_date') if body.get('end_date') else today
    if datetime.strptime(body['start_date'], '%Y-%m-%d') > datetime.strptime(body['end_date'], '%Y-%m-%d'):
        return dict(status=400, title='Bad Request', detail='invalid date range', type='about:blank'), 400
    platform_name = body['platform_name']
    try:
        validate_platform_name(platform_name=platform_name)
    except ApiError as e:
        return dict(status=400, title='Bad Request', detail=e.args[0], type='about:blank'), 400
    try:
        get_integration_function(function_name='download_performance_report')
    except KeyError:
        return dict(status=400, title='Bad Request', detail="Platform does not support ", type='about:blank'), 400
    else:
        download_performances_report_task.delay(**body)
        return None, 204
