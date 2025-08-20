from celery import shared_task


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True)
def download_performances_report_task(self, platform_name, destination, start_date, end_date):
    from stratus_api.integrations import get_integration_function
    return get_integration_function(function_name='download_performance_report')(destination=destination,
                                                                                 platform_name=platform_name,
                                                                                 start_date=start_date,
                                                                                 end_date=end_date)
