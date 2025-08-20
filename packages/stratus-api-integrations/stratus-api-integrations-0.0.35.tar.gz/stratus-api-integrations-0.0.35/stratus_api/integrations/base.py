__integration_settings__ = None
__integration_functions__ = None


def configure_integration(get_platform_names, create_destination, create_segment, get_destination_template,
                          get_segment_template, distribute_file, settings=None, download_performance_report=None):
    global __integration_settings__
    global __integration_functions__
    function_mapping = dict(
        get_platform_names=get_platform_names,
        get_destination_template=get_destination_template, create_segment=create_segment,
        create_destination=create_destination, distribute_file=distribute_file,
        get_segment_template=get_segment_template
    )
    if download_performance_report is not None:
        function_mapping['download_performance_report'] = download_performance_report
    validate_function_mapping(function_mappings=function_mapping)
    __integration_functions__ = function_mapping
    if settings is None:
        settings = dict()
    enriched_settings = validate_settings(settings=settings, settings_type='integration')

    __integration_settings__ = enriched_settings
    return __integration_functions__, __integration_settings__


def validate_function_mapping(function_mappings):
    from stratus_api.core.exceptions import ApiError
    required_functions = {
        'get_platform_names': {},
        'create_destination': {'name', 'settings', 'platform_name', 'destination_uuid', 'account_uuid', 'product_uuid'},
        'create_segment': {'name', 'platform_name', 'destination', 'segment_uuid', 'settings'},
        'get_segment_template': {'platform_name'},
        'get_destination_template': {'platform_name'},
        'distribute_file': {'platform_name', 'segments', 'destination', 'local_path', 'chunk_number', 'start_time',
                            'operations', 'id_types'}
    }
    optional_functions = {
        'download_performance_report': {'destination', 'platform_name','start_date', 'end_date'}
    }
    if set(function_mappings.keys()) < set(required_functions.keys()):
        raise ApiError('Invalid or Missing required functions')
    if set(optional_functions.keys()) < set(
            {k for k in function_mappings.keys() if k not in required_functions.keys()}):
        raise ApiError('Invalid Optional functions')
    for mapping, func in function_mappings.items():
        func_code = func.__code__
        if set(func_code.co_varnames[:func_code.co_argcount]) != set(
                {**required_functions, **optional_functions}[mapping]):
            raise ApiError('{mapping} function contains missing/invalid parameters'.format(mapping=mapping))
    return True


def get_settings_schema(**kwargs):
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "chunk_size"
        ],
        "properties": {
            "chunk_size": {
                "type": "integer",
                "description": """Number of records to send to the integration at one time. Set to 0 to combine into 
                one large file""",
                "default": 10000,
            },
            "chunk_multiplier": {
                "type": "integer",
                "description": """Number of records to send to the integration at one time. Set to 0 to combine into 
                    one large file""",
                "default": 100,
            },
            "parallelize": {
                "type": "boolean",
                "description": """deliver data in parallel to speed up delivery""",
                "default": False,
            },
        }
    }


def get_integration_settings():
    global __integration_settings__
    return __integration_settings__


def get_integration_function(function_name):
    global __integration_functions__
    return __integration_functions__[function_name]


def get_schema_values_recursive(schema, value_name, recursion=False):
    example = dict()
    if schema.get('properties'):
        for k, v in schema.get('properties').items():
            value = get_schema_values_recursive(schema=v, value_name=value_name, recursion=True)
            if value is not None:
                example[k] = value
    else:
        example = schema.get(value_name)
    return dict() if not recursion and example is None else example


def validate_settings(settings, settings_type, token_info=None, platform_name=None):
    import jsonschema
    from stratus_api.core.exceptions import ApiError
    from stratus_api.integrations import get_integration_function, get_schema_values_recursive

    if 'rate' in settings.keys():
        if token_info is not None and 'post:rate' not in token_info['scope']:
            print(token_info)

    template_mapping = dict(
        destination=get_integration_function(function_name='get_destination_template'),
        segment=get_integration_function(function_name='get_segment_template'),
        integration=get_settings_schema
    )
    template = template_mapping[settings_type](platform_name=platform_name)
    enriched_settings = get_schema_values_recursive(schema=template, value_name='default')
    enriched_settings.update(settings)
    try:
        jsonschema.validate(enriched_settings, template)
    except jsonschema.ValidationError as e:
        raise ApiError(e.args[0])
    return enriched_settings


def create_entity(entity_type, name, platform_name, settings, token_info, **kwargs):
    validate_platform_name(platform_name=platform_name)
    enriched_settings = validate_settings(platform_name=platform_name, settings=settings,
                                          token_info=token_info,
                                          settings_type=entity_type)
    create_external_entity = get_integration_function(function_name='create_{entity}'.format(entity=entity_type))
    external_id, external_attributes = create_external_entity(
        name=name, platform_name=platform_name,
        settings=enriched_settings,
        **kwargs
    )
    return external_id, external_attributes


def validate_platform_name(platform_name):
    from stratus_api.core.exceptions import ApiError
    if platform_name not in get_integration_function(function_name='get_platform_names')():
        raise ApiError("{platform_name} not a valid platform name".format(platform_name=platform_name))
    return True
