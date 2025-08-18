from enum import Enum
from typing import Any


class ErrorCode(Enum):
    GENERIC_ERROR = 1,

    C8_AUTH_GET_TOKEN_FAILED = 101,
    C8_FAILED_TO_ACTIVATE_JOBS = 102,
    C8_FAILED_TO_COMPLETE_JOB = 103,
    C8_FAILED_TO_MARK_JOB_AS_FAILED = 104,
    C8_FAILED_TO_THROW_JOB_ERROR = 105,
    C8_JOB_WITH_ERROR = 106,
    C8_GET_CLUSTER_TOPOLOGY_FAILED = 107,
    C8_FAILED_TO_CREATE_PROCESS_INSTANCE = 108,
    C8_FAILED_TO_CANCEL_PROCESS_INSTANCE = 109,
    C8_FAILED_TO_MIGRATE_PROCESS_INSTANCE = 110,
    C8_FAILED_TO_MODIFY_PROCESS_INSTANCE = 111,
    C8_FAILED_TO_PUBLISH_MESSAGE = 112,
    C8_FAILED_TO_CORRELATE_MESSAGE = 113,
    C8_FAILED_TO_BROADCAST_SIGNAL = 114,

    C8_WORKER_SIG_TOO_MANY_ARGUMENTS = 201,
    C8_WORKER_SIG_FIRST_ARGUMENT_INVALID = 202,
    C8_WORKER_SIG_FIRST_ARGUMENT_NOT_JOB = 203,


ERROR_CODES_MESSAGE_MAP = {
    ErrorCode.GENERIC_ERROR: "Something went wrong {}",
    ErrorCode.C8_AUTH_GET_TOKEN_FAILED: "Cannot get auth token: {}",
    ErrorCode.C8_FAILED_TO_ACTIVATE_JOBS: "Cannot activate job of type {}: {}",
    ErrorCode.C8_FAILED_TO_COMPLETE_JOB: "Cannot complete job of type {} and key {}: {}",
    ErrorCode.C8_FAILED_TO_MARK_JOB_AS_FAILED: "Cannot mark job of type {} and key {} as failed: {}",
    ErrorCode.C8_FAILED_TO_THROW_JOB_ERROR: "Cannot throw error for job of type {} and key {}: {}",
    ErrorCode.C8_JOB_WITH_ERROR: "A business error occurred while processing a job of type {} and key {}: {}",
    ErrorCode.C8_GET_CLUSTER_TOPOLOGY_FAILED: "Cannot get cluster topology: {}",

    ErrorCode.C8_WORKER_SIG_TOO_MANY_ARGUMENTS: "Worker function '{}' for job type '{}' must accept exactly one "
                                                "argument. Found {}.",
    ErrorCode.C8_WORKER_SIG_FIRST_ARGUMENT_INVALID: "Worker function '{}' for job type '{}' first argument must be a "
                                                    "standard positional or keyword argument. Found {}",
    ErrorCode.C8_WORKER_SIG_FIRST_ARGUMENT_NOT_JOB: "Worker function '{}' for job type '{}' first argument must be "
                                                    "type-hinted as 'ActivatedJob'. Found '{}'",
    ErrorCode.C8_FAILED_TO_CREATE_PROCESS_INSTANCE: "Cannot create process instance: {}",
    ErrorCode.C8_FAILED_TO_CANCEL_PROCESS_INSTANCE: "Cannot cancel process instance with key {}: {}",
    ErrorCode.C8_FAILED_TO_MIGRATE_PROCESS_INSTANCE: "Cannot migrate process instance with key {}: {}",
    ErrorCode.C8_FAILED_TO_MODIFY_PROCESS_INSTANCE: "Cannot modify process instance with key {}: {}",
    ErrorCode.C8_FAILED_TO_PUBLISH_MESSAGE: "Cannot publish message: {}",
    ErrorCode.C8_FAILED_TO_CORRELATE_MESSAGE: "Cannot correlate message: {}",
    ErrorCode.C8_FAILED_TO_BROADCAST_SIGNAL: "Cannot broadcast signal: {}"

}


def error_code_message_mapper(error_code: ErrorCode, parameters: list[Any]):
    return (ERROR_CODES_MESSAGE_MAP
            .get(error_code)
            .format(*(parameters + ["n.a."] * (ERROR_CODES_MESSAGE_MAP.get(error_code).count("{}") - len(parameters))))
            or f"Unhandled error code {error_code}")
