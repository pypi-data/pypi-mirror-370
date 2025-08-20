import re
from urllib.parse import urlparse

from constants.constants import generic_error_message
from model_garden.model_provider import ModelProvider


class Utils:
  @staticmethod
  def get_headers(api_key: str, content_type: str = "application/json"):
    return {"Content-Type": content_type, "x-api-key": api_key, "Accept": "*/*"}

  @staticmethod
  def handleApiCallFailure(res, status_code):
    if status_code == 401:
      Utils.print_error_and_exit(
        "You are Unauthorized. Please check your API Key"
      )
    if res.get("detail", None):
      errMsg = res["detail"]
    elif res.get("errorMessage", None):
      errMsg = res["errorMessage"]
    elif res.get("error", None):
      errMsg = res["error"]
    else:
      errMsg = generic_error_message if (res == None or res == "") else res
    raise Exception(errMsg)

  @staticmethod
  def print_error_and_exit(msg=None):
    msg = msg if msg is not None else generic_error_message
    print(msg)
    raise Exception(msg)
    # exit()

  @staticmethod
  def validate_json_path(path):
    """ Validates the JSON path to ensure keys are alphanumeric or underscore """
    invalid_key_pattern = re.compile(r'[^a-zA-Z0-9.\[\]]')

    if invalid_key_pattern.search(path):
        raise ValueError(f"Invalid JSON path: '{path}'. Keys can only contain letters, digits, and arrays like [0].")

    if re.search(r'\[\D+\]', path):
        raise ValueError(f"Invalid array index in path: '{path}'. Array indices must be numeric.")

  @staticmethod
  def get_value_from_json_path(data: dict, json_path: str):
      keys = re.split(r'[.\[\]]+', json_path)
      keys = [k for k in keys if k]
      value = data
      for key in keys:
          if key.isdigit():
              key = int(key)
              if isinstance(value, list) and len(value) > key:
                  value = value[key]
              else:
                  return None
          else:
              if isinstance(value, dict) and key in value:
                  value = value[key]
              else:
                  return None
      return value

  @staticmethod
  def create_nested_dict(json_path, input_dict):
    def set_nested_value(d, keys, value):
        """ Helper function to set a nested value in a dictionary """
        for i, key in enumerate(keys[:-1]):
            if isinstance(key, int):
                # Handle lists (convert previous level to a list if needed)
                if not isinstance(d, list):
                    d[keys[i-1]] = []  # Convert previous dict entry into a list
                    d = d[keys[i-1]]
                # Ensure the list has enough elements to access the desired index
                while len(d) <= key:
                    d.append({})
                d = d[key]  # Move to the list entry
            else:
                # Handle dictionaries
                if key not in d:
                    d[key] = {}
                d = d[key]

        # Handle the final key or index
        if isinstance(keys[-1], int):
            # We set this to the 0th index
            if not isinstance(d, list):
                d[keys[-2]] = []  # Convert to a list if necessary
                d = d[keys[-2]]
            while len(d) <= 0:  # Always target index 0
                d.append({})
            d[0] = {keys[-1]: value}  # Add value to the 0th index
        else:
            d[keys[-1]] = value

    def parse_json_path(path):
        """ Parses the JSON path and returns a list of keys and indices """
        path = re.sub(r'\[(\d+)\]', '[0]', path)  # Replace any array index with 0 for processing
        keys = []
        for part in path.split('.'):
            match = re.findall(r'(\w+)|\[(\d+)\]', part)
            for key, idx in match:
                if key:
                    keys.append(key)
                if idx:
                    keys.append(int(idx))
        return keys

    keys = parse_json_path(json_path)
    result = {}
    set_nested_value(result, keys, input_dict)

    return result

  @staticmethod
  def validate_url(url: str , service_name: str =None) -> str:
    if url is None:
      return None

    ip_pattern = r"^(?:http:\/\/|https:\/\/)?\b(?:\d{1,3}\.){3}\d{1,3}\b$"
    domain_pattern = r"^(?:http:\/\/|https:\/\/)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    parsed_url = urlparse(url)

    is_valid_ip = re.match(ip_pattern, parsed_url.netloc)
    is_valid_domain = re.match(domain_pattern, parsed_url.netloc)

    if is_valid_ip or is_valid_domain:
        return url
    else:
        error_message = "Invalid URL."
        if service_name:
            error_message += f" Please provide a valid URL for the {service_name} service."
        raise ValueError(error_message)

  @staticmethod
  def get_model_provider_name(provider: ModelProvider) -> str:
        if provider == ModelProvider.VERTEX_AI_MODEL:
            return "vertexai"
        elif provider == ModelProvider.HUGGING_FACE_MODEL:
            return "huggingface"
        elif provider == ModelProvider.CUSTOM_MODEL:
            return "custom"
        elif provider == ModelProvider.BERRYDB_MODEL:
            return "berrydb"
        else:
            raise ValueError("Unsupported Model Provider!")