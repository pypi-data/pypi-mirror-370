from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import base64


def xor_encode(s, key=42):
    xor_str = ''.join(chr(ord(c) ^ key) for c in s)
    encoded_bytes = base64.b64encode(xor_str.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def clean_data(data: dict) -> dict:
    """
    Cleans the input data by removing keys with None values.

    Args:
        data (dict): The input data.

    Returns:
        dict: The cleaned data.
    """
    return {k: v for k, v in data.items() if v is not None}

def join_url_params(base_url: str, params: dict) -> str:
    """
    Join URL with parameters while preserving existing query parameters.
    
    Args:
        base_url (str): Base URL that may contain existing parameters
        params (dict): New parameters to add
        
    Returns:
        str: URL with all parameters properly joined
    """
    # Parse the URL
    parsed = urlparse(base_url)
    
    # Get existing parameters
    existing_params = parse_qs(parsed.query)
    
    # Update with new parameters
    existing_params.update(params)
    
    # Reconstruct the URL
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(existing_params, doseq=True),
        parsed.fragment
    ))