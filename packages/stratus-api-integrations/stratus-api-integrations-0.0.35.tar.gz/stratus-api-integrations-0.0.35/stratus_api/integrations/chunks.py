from stratus_api.integrations.distribution import DELIVERED_SCHEMA

delivered_headers = [i['name'] for i in DELIVERED_SCHEMA]
CHUNKED_FILE_GCS_PATH_FORMAT = "chunks/{year}/{month}/{day}/{hour}/{minute}/{job_uuid}/{chunk_number}.csv"


def create_file_chunks(bucket_name, file_pattern, job_uuid, file_headers, integration_settings, chunk_number=0,
                       delimiter='|'):
    import os
    from datetime import datetime
    chunk_records = 0
    start = datetime.utcnow().timestamp()
    chunk_pointer = None
    chunk_writer = None
    delivered_pointers = None
    delivered_writers = None
    delivered_file_paths = dict()
    checkpoint = get_file_checkpoint(file_pattern=file_pattern, job_uuid=job_uuid)
    if checkpoint is not None:
        chunk_number = checkpoint['chunk_number'] + 1
    chunk_file_path = ''
    line_number = None
    file_path = None
    for row, line_number, file_path in read_remote_csvs_as_stream(bucket_name=bucket_name, file_pattern=file_pattern,
                                                                  job_uuid=job_uuid,
                                                                  delimiter=delimiter):
        chunk_file_path, chunk_pointer, chunk_writer = add_row_to_chunk(
            job_uuid=job_uuid,
            file_headers=file_headers,
            row=row,
            delimiter=delimiter,
            chunk_number=chunk_number,
            writer=chunk_writer,
            pointer=chunk_pointer)
        delivered_file_paths, delivered_pointers, delivered_writers = add_row_to_delivered_path(
            job_uuid=job_uuid, file_headers=file_headers, row=row, pointers=delivered_pointers,
            writers=delivered_writers, delivered_paths=delivered_file_paths,
            chunk_number=chunk_number, timestamp=start)
        chunk_records += 1
        if 0 < integration_settings['chunk_size'] <= chunk_records:
            chunk_pointer.close()
            chunk_pointer = None
            for segment_uuid in delivered_pointers.keys():
                delivered_pointers[segment_uuid].close()
            delivered_pointers = None
            delivered_writers = None
            yield chunk_file_path, delivered_file_paths, chunk_number
            update_file_checkpoint(job_uuid=job_uuid, file_pattern=file_pattern, chunk_number=chunk_number,
                                   line_number=line_number, file_path=file_path)
            start = datetime.utcnow().timestamp()
            os.remove(chunk_file_path)
            for segment_uuid in delivered_file_paths.keys():
                os.remove(delivered_file_paths[segment_uuid])
            chunk_records = 0
            chunk_number += 1

    if chunk_records > 0:
        chunk_pointer.close()
        for segment_uuid in delivered_pointers.keys():
            delivered_pointers[segment_uuid].close()
        yield chunk_file_path, delivered_file_paths, chunk_number
        update_file_checkpoint(job_uuid=job_uuid, file_pattern=file_pattern, chunk_number=chunk_number,
                               line_number=line_number, file_path=file_path)
        os.remove(chunk_file_path)
        for segment_uuid in delivered_file_paths.keys():
            os.remove(delivered_file_paths[segment_uuid])


def add_row_to_chunk(row, chunk_number, job_uuid, file_headers, delimiter, pointer=None, writer=None):
    from stratus_api.core.settings import get_settings
    import os
    chunk_path_pattern = os.path.join(get_settings().get('upload_folder', '/apps/files/'),
                                      'upload-{job_uuid}-{chunk_number}.csv')
    chunk_path = chunk_path_pattern.format(chunk_number=chunk_number, job_uuid=job_uuid)

    return add_to_file(path=chunk_path, row=row, headers=file_headers, delimiter=delimiter, pointer=pointer,
                       writer=writer)


def add_row_to_delivered_path(row, chunk_number, job_uuid, file_headers, timestamp, pointers=None,
                              writers=None, delivered_paths=None):
    from stratus_api.core.settings import get_settings
    import os
    delivered_path_pattern = os.path.join(get_settings().get('upload_folder', '/apps/files/'),
                                          'delivered-{segment_uuid}-{job_uuid}-{chunk_number}.csv')

    if pointers is None:
        pointers = dict()
        writers = dict()
        delivered_paths = dict()

    for segment_uuid, operation in {k: row[idx] for idx, k in enumerate(file_headers) if
                                    k not in ['internal_user_id', 'external_user_id', 'id_type', 'policy_uuid',
                                              'created_ts'] and row[
                                        idx] != ''}.items():
        delivered_path = delivered_path_pattern.format(chunk_number=chunk_number, job_uuid=job_uuid,
                                                       segment_uuid=segment_uuid)
        delivered_path, pointer, writer = add_to_file(
            path=delivered_path, row=[
                segment_uuid,
                row[file_headers.index('internal_user_id')],
                row[file_headers.index('external_user_id')],
                row[file_headers.index('id_type')],
                operation,
                job_uuid,
                row[file_headers.index('policy_uuid')],
                timestamp
            ], headers=delivered_headers, delimiter=',',
            pointer=pointers.get(segment_uuid),
            writer=writers.get(segment_uuid),
        )
        delivered_paths[segment_uuid] = delivered_path
        pointers[segment_uuid]=pointer
        writers[segment_uuid]=writer
    return delivered_paths, pointers, writers


def add_to_file(path, row, headers, delimiter, pointer, writer, add_headers=True):
    import csv
    if pointer is None:
        pointer = open(path, 'wt')
        writer = csv.writer(pointer, headers, delimiter=delimiter)
        if add_headers:
            writer.writerow(headers)
    writer.writerow(row)
    return path, pointer, writer


def read_remote_csvs_as_stream(bucket_name, file_pattern, job_uuid, delimiter='|'):
    from stratus_api.storage.gcs import download_from_storage, get_filenames_by_pattern
    import os
    import csv
    checkpoint = get_file_checkpoint(file_pattern=file_pattern, job_uuid=job_uuid)
    process_file = False
    for file_path in get_filenames_by_pattern(bucket_name=bucket_name, file_path=file_pattern):
        if not process_file and (checkpoint is None or file_path == checkpoint['file_path']):
            process_file = True
        if process_file:
            local_path = download_from_storage(bucket_name=bucket_name, file_path=file_path, job_id=job_uuid)
            process_row = False
            with open(local_path, 'rt') as f:
                reader = csv.reader(f, delimiter=delimiter)
                for idx, row in enumerate(reader):
                    if not process_row and (checkpoint is None or (
                            idx > checkpoint['line_number'] and checkpoint['file_path'] == file_path)):
                        process_row = True
                    if process_row:
                        yield row, idx, file_path
            os.remove(local_path)


def update_file_checkpoint(job_uuid, file_pattern, file_path, chunk_number, line_number):
    from stratus_api.integrations.cache import cache_data
    key = generate_file_cache_key(file_pattern=file_pattern, job_uuid=job_uuid)
    return cache_data(key=key, value=dict(file_path=file_path, chunk_number=chunk_number, line_number=line_number),
                      expiration_seconds=86400)


def get_file_checkpoint(file_pattern, job_uuid):
    from stratus_api.integrations.cache import get_cached_data
    key = generate_file_cache_key(file_pattern=file_pattern, job_uuid=job_uuid)
    return get_cached_data(key=key)


def generate_file_cache_key(file_pattern, job_uuid):
    from stratus_api.core.common import generate_hash_id
    return generate_hash_id(dict(file_pattern=file_pattern, job_uuid=job_uuid))


def create_parallel_chunks(job_uuid, bucket_name, file_pattern, platform_name, destination, file_headers, segments,
                           id_types, operations, delimiter='|', **kwargs):
    from stratus_api.integrations.base import get_integration_settings
    from stratus_api.core.settings import get_settings
    from stratus_api.integrations.distribution import compose_integration_logs, log_integration
    import os
    from datetime import datetime
    import math
    chunk_multiplier = get_integration_settings()['chunk_multiplier']
    chunk_size = get_integration_settings()['chunk_size'] * chunk_multiplier
    checkpoint = get_file_checkpoint(file_pattern=file_pattern, job_uuid=job_uuid)
    if checkpoint is not None:
        chunk_number = checkpoint['chunk_number'] + 1
    else:
        chunk_number = 0
    chunk_records = 0
    chunk_pointer = None
    chunk_writer = None
    chunk_path = ''
    chunk_path_pattern = os.path.join(get_settings().get('upload_folder', '/apps/files/'),
                                      'chunk-{job_uuid}-{chunk_number}.csv')
    start_time = datetime.utcnow()
    if get_file_checkpoint(file_pattern=file_pattern, job_uuid=job_uuid) is None:
        rows = compose_integration_logs(job_uuid, segments, file_pattern, int(start_time.timestamp()), id_types,
                                        operations,
                                        'started')
        log_integration(rows)
    total_chunks = 0
    for row, line_number, file_path in read_remote_csvs_as_stream(
            bucket_name=bucket_name, file_pattern=file_pattern, job_uuid=job_uuid,
            delimiter='|'):

        chunk_path = chunk_path_pattern.format(chunk_number=chunk_number, job_uuid=job_uuid)
        chunk_records += 1

        chunk_path, chunk_pointer, chunk_writer = add_to_file(path=chunk_path, row=row, headers=file_headers,
                                                              delimiter=delimiter, pointer=chunk_pointer,
                                                              writer=chunk_writer, add_headers=False)
        if 0 < chunk_size <= chunk_records:
            push_chunks_to_distribute(
                chunk_pointer=chunk_pointer, chunk_multiplier=chunk_multiplier, chunk_path=chunk_path,
                platform_name=platform_name,
                job_uuid=job_uuid, segments=segments, destination=destination,
                file_headers=file_headers, id_types=id_types, operations=operations,
                chunk_number=chunk_number, start_time=start_time
            )
            chunk_number += chunk_multiplier
            update_file_checkpoint(job_uuid=job_uuid, file_pattern=file_pattern, file_path=file_path,
                                   chunk_number=chunk_number, line_number=line_number)
            chunk_records = 0
            chunk_pointer = None

    if chunk_records > 0:
        total_chunks = 1 if chunk_size == 0 else chunk_number + math.ceil(
            chunk_records / (chunk_size / chunk_multiplier))
        push_chunks_to_distribute(
            chunk_pointer=chunk_pointer, chunk_multiplier=chunk_multiplier, chunk_path=chunk_path,
            platform_name=platform_name,
            job_uuid=job_uuid, segments=segments, destination=destination,
            file_headers=file_headers, id_types=id_types, operations=operations,
            chunk_number=chunk_number, start_time=start_time
        )
    rows = compose_integration_logs(job_uuid, segments, file_pattern, int(start_time.timestamp()), id_types, operations,
                                    'completed')
    log_integration(rows)
    return dict(job_uuid=job_uuid, total_chunks=total_chunks)


def push_chunks_to_distribute(chunk_pointer, chunk_path, job_uuid,
                              platform_name, start_time,
                              destination, file_headers, segments, id_types, operations, chunk_number, **kwargs):
    from stratus_api.integrations.tasks.distributions import deliver_data_task
    from stratus_api.storage.gcs import upload_file_to_gcs
    from stratus_api.core.settings import get_settings
    import os
    from datetime import datetime
    now = datetime.utcnow()
    chunk_pointer.close()
    bucket_name = get_settings()['bucket_name']
    file_path = CHUNKED_FILE_GCS_PATH_FORMAT.format(
        job_uuid=job_uuid,
        chunk_number=chunk_number,
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute)
    upload_file_to_gcs(local_path=chunk_path, file_path=file_path, bucket_name=bucket_name)
    deliver_data_task.delay(bucket_name=bucket_name, platform_name=platform_name,
                            file_pattern=file_path,
                            start_time=start_time.timestamp(),
                            job_uuid=job_uuid, segments=segments, destination=destination, file_headers=file_headers,
                            id_types=id_types, operations=operations, chunk_start_number=chunk_number)
    os.remove(chunk_path)
    return True
