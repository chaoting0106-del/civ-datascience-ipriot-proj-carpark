def parse_config(config_file: str) -> dict:
    """Set up config into json file"""
    import json    
    with open(config_file) as input_file:
        config = json.load(input_file)
    return config["CarParks"][0]

if __name__ == '__main__':
    cfg_data=parse_config("samples_and_snippets\\config.json")
    print(cfg_data)
