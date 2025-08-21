import simplex.core.error.handling
import simplex.core.error
import simplex.core.actions.fetch
from google.protobuf.json_format import Parse

import simplex.core.protos
import simplex.core.protos.generated
import simplex.core.protos.generated.EndPointArguments
import simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2
import simplex.core.protos.generated.project_pb2

def run_analysis(url: str, json_data: str, token: str) -> simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckOutput:

    fetch_string_results = simplex.core.actions.fetch.fetch_string(url, token, json_data)

    response_proto = simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckOutput()
    Parse(fetch_string_results.text, response_proto)

    # Check for errors in the response
    simplex.core.error.handling.check_for_errors(response_proto.project.log)

    return response_proto

def update_gamma(url: str, json_data: str, token: str) -> simplex.core.protos.generated.project_pb2.Data:

    fetch_string_results = simplex.core.actions.fetch.fetch_string(url, token, json_data)

    response_proto = simplex.core.protos.generated.project_pb2.Data()
    Parse(fetch_string_results.text, response_proto)
    return response_proto