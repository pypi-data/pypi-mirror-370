def merge_chunk(data: dict, chunk: dict):
    for key, chunk_value in chunk.items():
        if key in data:
            data_value = data[key]

            if isinstance(data_value, list) and isinstance(chunk_value, list):
                data[key].extend(chunk_value)
            elif isinstance(data_value, dict) and isinstance(chunk_value, dict):
                merge_chunk(data_value, chunk_value)
            else:
                data[key] = chunk_value
        else:
            data[key] = chunk_value

    return data
