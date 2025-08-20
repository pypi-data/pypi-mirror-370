from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_result, retry_if_exception_type, \
    RetryError, retry_any
from stratus_api.core.settings import get_settings

UPLOADED_FILE_GCS_PATH_FORMAT = "{year}/{month}/{day}/{hour}/{segment_uuid}/{job_uuid}/uploaded.{chunk_number}.csv"

DELIVERED_SCHEMA = [
    dict(name='segment_uuid', type='STRING'),
    dict(name='internal_user_id', type='STRING'),
    dict(name='external_user_id', type='STRING'),
    dict(name='id_type', type='STRING'),
    dict(name='operation', type='BOOLEAN'),
    dict(name='integration_job_uuid', type='STRING'),
    dict(name='policy_uuid', type='STRING'),
    dict(name='created_ts', type='TIMESTAMP'),
]

INTEGRATION_LOG_SCHEMA = [
    dict(name='integration_job_uuid', type='STRING'),
    dict(name='segment_uuid', type='STRING'),
    dict(name='file_pattern', type='STRING'),
    dict(name='created_ts', type='TIMESTAMP'),
    dict(name='id_type', type='STRING', mode='REPEATED'),
    dict(name='operation', type='STRING', mode='REPEATED'),
    # dict(name='id_type', type='STRING'),
    # dict(name='operation', type='STRING'),
    dict(name='status', type='STRING'),
]


def log_integration(rows):
    from stratus_api.core.settings import get_settings
    from stratus_api.bigquery import stream_records_to_bigquery
    from stratus_api.bigquery.bigquery import create_table
    from stratus_api.events import publish_event, create_topic

    errors = stream_records_to_bigquery(rows=rows, row_ids=None,
                                        project_id=get_settings()['integration_log_project_id'],
                                        table_name=get_settings()['integration_log_table'],
                                        dataset_name=get_settings()['integration_log_dataset'])
    if errors:
        raise Exception(errors)

    for row in rows:
        publish_event(topic_name=get_settings()['integration_log_topic'], attributes=dict(),
                      event_type='integration', payload=row)


def compose_integration_logs(job_uuid, segments, file_pattern, time, id_types, operations, status):
    rows = []
    for segment in segments:
        rows.append(dict(
            integration_job_uuid=job_uuid,
            segment_uuid=segment['segment_uuid'],
            file_pattern=file_pattern,
            created_ts=time,
            id_type=id_types,
            operation=operations,
            status=status
        ))
    return rows


def get_delivery_error_type(exception):
    from .exceptions import AuthenticationError, ConfigurationError, NotFoundError
    if isinstance(exception, AuthenticationError):
        error_type = 'Authentication Error'
    elif isinstance(exception, ConfigurationError):
        error_type = 'Configuration Error'
    elif isinstance(exception, NotFoundError):
        error_type = 'Not Found Error'
    else:
        error_type = 'Delivery Failure'
    return error_type


def deliver_data(job_uuid, bucket_name, file_pattern, platform_name, destination, file_headers, segments, id_types,
                 operations, chunk_start_number, start_time=None, **kwargs):
    from stratus_api.integrations import get_integration_settings
    from stratus_api.integrations.chunks import create_file_chunks
    from datetime import datetime
    from stratus_api.integrations.chunks import get_file_checkpoint
    if start_time is None:
        start_time = datetime.utcnow()
    else:
        start_time = datetime.utcfromtimestamp(start_time)
    if '*' in file_pattern and get_file_checkpoint(file_pattern=file_pattern, job_uuid=job_uuid) is None:
        rows = compose_integration_logs(job_uuid, segments, file_pattern, int(start_time.timestamp()), id_types,
                                        operations, 'started')
        log_integration(rows)

    segment_mapping = {i['segment_uuid']: i for i in segments}
    for local_path, delivered_paths, chunk_number, in create_file_chunks(
            bucket_name=bucket_name,
            file_pattern=file_pattern,
            integration_settings=get_integration_settings(),
            file_headers=file_headers,
            job_uuid=job_uuid,
            chunk_number=chunk_start_number
    ):
        chunk_start = datetime.utcnow()
        tb = None
        error_type = None
        try:
            success = distribution_retry_wrapper(
                destination=destination, platform_name=platform_name, segments=segment_mapping, local_path=local_path,
                chunk_number=chunk_number, start_time=start_time, id_types=id_types, operations=operations
            )
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            success = False
            error_type = get_delivery_error_type(exception=e)
            if get_settings()['environment'] not in {'qa', 'prod'}:
                raise e
        if success:
            for segment_uuid, delivered_path in delivered_paths.items():
                load_delivered_data(
                    local_path=delivered_path,
                    job_uuid=job_uuid,
                    chunk_number=chunk_number,
                    segment_uuid=segment_uuid
                )
        log_chunk_delivery(success=success, start=chunk_start, chunk_number=chunk_number, destination=destination,
                           segments=segment_mapping, job_uuid=job_uuid, platform_name=platform_name, traceback=tb,
                           error_type=error_type)

    end_time = datetime.utcnow()

    rows = compose_integration_logs(job_uuid, segments, file_pattern, int(end_time.timestamp()), id_types, operations,
                                    'completed')
    if '*' in file_pattern:
        log_integration(rows)

    return dict(job_uuid=job_uuid, file_pattern=file_pattern, chunk_start_number=chunk_start_number)


def log_chunk_delivery(success, start, destination, chunk_number, segments, job_uuid, platform_name, error_type=None,
                       traceback=None):
    from stratus_api.core import log_event
    from datetime import datetime
    payload = dict(
        job_uuid=job_uuid,
        platform_name=platform_name,
        success=success,
        chunk_number=chunk_number
    )
    if traceback:
        payload['traceback'] = traceback
    log_event(
        level='info',
        start=start,
        end=datetime.utcnow(),
        status='success' if success else 'failure',
        process_type='segment_delivery',
        failure_classification=error_type,
        payload=payload,
        attributes=dict(
            destination_uuid=destination['destination_uuid'],
            platform_uuid=destination['platform_uuid'],
            account_uuid=destination['account_uuid'],
            product_uuid=destination['product_uuid'],
            segment_uuids=list(segments.keys()),
            platform_name=platform_name
        ),
    )


def distribution_failed(value):
    return value is False


@retry(stop=stop_after_attempt(3), reraise=True, wait=wait_random_exponential(multiplier=.5, max=5),
       retry=retry_any(retry_if_result(distribution_failed), retry_if_exception_type(Exception)))
def distribution_retry_wrapper(**kwargs):
    from stratus_api.integrations import get_integration_function
    distribute_file = get_integration_function(function_name='distribute_file')
    return distribute_file(**kwargs)


def distribution_retry_logger(retry_state):
    pass


def load_delivered_data(job_uuid, local_path, chunk_number, segment_uuid):
    from stratus_api.storage.gcs import upload_file_to_gcs
    from datetime import datetime
    now = datetime.utcnow()
    upload_file_to_gcs(
        local_path=local_path,
        file_path=UPLOADED_FILE_GCS_PATH_FORMAT.format(
            job_uuid=job_uuid,
            chunk_number=chunk_number,
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            segment_uuid=segment_uuid
        )
    )
    return True


def close_delivery(job_uuid):
    return job_uuid, True
