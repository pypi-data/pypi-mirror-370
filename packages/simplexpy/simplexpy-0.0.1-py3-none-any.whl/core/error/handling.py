from dataclasses import dataclass

import logging

import simplex.core.protos.generated

import simplex.core
import simplex
import simplex.core.protos.generated.Utils
import simplex.core.protos.generated.Utils.log_pb2
import simplex.core.protos.generated.project_pb2

# ANSI escape codes for colors
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_for_errors(log : simplex.core.protos.generated.Utils.log_pb2.Log):
    """
    Navigates through the proto object to check for errors.
    If an error is found, raises a RuntimeError with details.
    """



    log_entries = log.entries
    for entry in log_entries:
        if entry.type == simplex.core.protos.generated.Utils.log_pb2.LOG_TYPE_ERROR:
            raise RuntimeError(f"{RED}Error detected: text={entry.text}{RESET}")
        elif entry.type == simplex.core.protos.generated.Utils.log_pb2.LOG_TYPE_WARNING:
            logging.warning(f"{YELLOW}Warning detected: text={entry.text}{RESET}")