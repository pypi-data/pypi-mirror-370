import yaml

def load_config_yaml(file_path):
    """
    Load configuration from a YAML file.

    Parameters:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Configuration loaded from the YAML file.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config