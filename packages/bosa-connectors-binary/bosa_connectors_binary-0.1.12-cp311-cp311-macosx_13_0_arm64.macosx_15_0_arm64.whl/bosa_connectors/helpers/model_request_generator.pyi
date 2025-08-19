from pydantic import BaseModel

def create_request_model(endpoint_name: str, schema: dict, service_prefix: str = 'Google', requires_auth: bool = False) -> type[BaseModel]:
    '''Create a Pydantic model for the request schema.

    Args:
        endpoint_name (str): The name of the endpoint.
        schema (dict): The schema definition for the endpoint.
        service_prefix (str, optional): The prefix for the service. Defaults to "Google".
        requires_auth (bool, optional): Whether the endpoint requires authentication. Defaults to False.

    Returns:
        Type[BaseModel]: The generated Pydantic model.
    '''
