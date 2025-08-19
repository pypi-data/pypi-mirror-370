import json




def dump_as_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def strip_json_comments(string: str):
    lines = string.splitlines()
    cleaned_lines = []
    in_string = False
    
    for line in lines:
        cleaned_line = []
        i = 0
        while i < len(line):
            if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                in_string = not in_string
            
            if not in_string and line[i:i+2] == '//':
                break
            
            cleaned_line.append(line[i])
            i += 1

        cleaned_lines.append(''.join(cleaned_line))
    
    cleaned_json_str = ''.join(cleaned_lines)
    return cleaned_json_str


def get_from_json(file_path) -> dict:
    with open(file_path, 'r') as file:
        data = file.read()
    
    try:
        json_data = json.loads(strip_json_comments(data))
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")

    return json_data

