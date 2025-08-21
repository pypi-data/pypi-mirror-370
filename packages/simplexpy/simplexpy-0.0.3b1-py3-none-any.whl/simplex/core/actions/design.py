import simplex.core.actions.fetch
from google.protobuf.json_format import Parse

import simplex.core.protos
import simplex.core.protos.generated
import simplex.core.protos.generated.EndPointArguments
import simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2
import simplex.core.protos.generated.project_pb2

def run_design(url: str, json_data: str, token: str) -> simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckOutput:

    fetch_string_results = simplex.core.actions.fetch.fetch_string(url, token, json_data)

    response_proto = simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckOutput()
    Parse(fetch_string_results.text, response_proto)
    return response_proto