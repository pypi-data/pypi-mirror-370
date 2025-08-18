# coding=UTF-8
import json
from cloudpss.utils import request


def graphql_request(query, variables=None, **kwargs):
    payload = {'query': query, 'variables': variables}
    
    r = request('POST', 'graphql', data=json.dumps(payload), **kwargs)

    return json.loads(r.text)
