from celery import shared_task


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True)
def deliver_data_task(self, platform_name, bucket_name, file_pattern, segments, destination, file_headers, job_uuid,
                      id_types, operations, chunk_start_number=0, start_time=None, **kwargs):
    from stratus_api.integrations.distribution import deliver_data
    return deliver_data(bucket_name=bucket_name, platform_name=platform_name, file_pattern=file_pattern,
                        job_uuid=job_uuid, segments=segments, destination=destination, file_headers=file_headers,
                        id_types=id_types, operations=operations, chunk_start_number=chunk_start_number, start_time=start_time)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True)
def chunk_data_task(self, platform_name, bucket_name, file_pattern, segments, destination, file_headers, job_uuid,
                    id_types, operations, **kwargs):
    from stratus_api.integrations.chunks import create_parallel_chunks
    return create_parallel_chunks(bucket_name=bucket_name, platform_name=platform_name, file_pattern=file_pattern,
                                  job_uuid=job_uuid, segments=segments, destination=destination,
                                  file_headers=file_headers,
                                  id_types=id_types, operations=operations)
