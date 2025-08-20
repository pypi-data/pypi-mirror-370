
def parse_to_ascii(str_value):
    str_value_bytes = str_value.encode()
    str_value_as_ascii = str_value_bytes.decode(
        'ascii', 'ignore'
    )

    return str_value_as_ascii
