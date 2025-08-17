def camel(snake_str):
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def camelize_dict(init_dict: dict):
    new_dict = {}
    for key, value in init_dict.items():
        new_key = camel(key)
        if isinstance(value, list):
            new_dict[new_key] = list(map(camelize_dict, value))
        elif isinstance(value, dict):
            new_dict[new_key] = camelize_dict(value)
        else:
            new_dict[new_key] = value
    return new_dict
