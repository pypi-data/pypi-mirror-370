import inspect
from ..API.base import APIRegistryCMD

async def handle_api_command(api_name, nsfw, query, limit=1):
    api = APIRegistryCMD.get_api(api_name)
    if not api:
        raise ValueError(f"Unknown API: {api_name}")

    if query and query.isdigit():
        query = int(query)

    func = api['nsfw' if nsfw else 'sfw']

    func_params = inspect.signature(func).parameters
    kwarg_name = 'fetch_limit' if 'fetch_limit' in func_params else 'limit'
    
    kwargs = {kwarg_name: limit} if limit > 1 else {}

    if query:
        if isinstance(query, int):
            return await func(query, **kwargs)
        else:
            return await func(tag=query, **kwargs)
    else:
        return await func(**kwargs)

async def handle_tags_command(api_name):
    handler = APIRegistryCMD.get_tag_handler(api_name)
    if not handler:
        raise ValueError(f"Tag retrieval not supported for {api_name}")
    
    return await handler()
