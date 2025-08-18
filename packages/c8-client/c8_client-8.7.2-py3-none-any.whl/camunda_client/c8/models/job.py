from pydantic import Field

from camunda_client.utils import JsonBaseModel


class ActivateJobRequest(JsonBaseModel):
    """
    Request model to activate jobs of a given type.

    Attributes
    ----------
    worker : str or None
        The name of the worker activating the jobs, mostly used for logging purposes. (alias: ``worker``)
    job_type : str
        The job type, as defined in the BPMN process (e.g., <zeebe:taskDefinition type='payment-service' />). (alias: ``type``)
    max_jobs_to_activate : int
        The maximum number of jobs to activate by this request. (alias: ``maxJobsToActivate``)
    timeout : int
        A job returned after this call will not be activated by another call until the timeout (in ms) has been reached. (alias: ``timeout``)
    request_timeout : int or None
        The request will be completed when at least one job is activated or after the requestTimeout (in ms). (alias: ``requestTimeout``)
    fetch_variables : list of str or None
        A list of variables to fetch as the job variables; if empty, all visible variables at the time of activation for
        the scope of the job will be returned. (alias: ``fetchVariables``)
    tenant_ids : list of str or None
        A list of IDs of tenants for which to activate jobs. (alias: ``tenantIds``)
    """
    worker: str | None = Field(
        default=None, alias="worker",
        description="the name of the worker activating the jobs, mostly used for logging purposes"
    )
    job_type: str = Field(
        ..., alias="type",
        description="the job type, as defined in the BPMN process (e.g. <zeebe:taskDefinition type='payment-service' />)"
    )
    max_jobs_to_activate: int = Field(
        ..., alias="maxJobsToActivate", description="the maximum jobs to activate by this request"
    )
    timeout: int = Field(
        ..., alias="timeout",
        description="a job returned after this call will not be activated by another call until the timeout (in ms) has "
                    "been reached"
    )
    request_timeout: int | None = Field(
        default=None, alias="requestTimeout",
        description="The request will be completed when at least one job is activated or after the requestTimeout (in ms).")

    fetch_variables: list[str] | None = Field(
        default=None, alias="fetchVariable",
        description="a list of variables to fetch as the job variables; if empty, all visible variables at the time of "
                    "activation for the scope of the job will be returned"
    )
    tenant_ids: list[str] | None = Field(
        default=None, alias="tenantIds", description="a list of IDs of tenants for which to activate jobs"
    )


class ActivatedJob(JsonBaseModel):
    """
    Represents a job that has been activated from the Camunda job queue.

    Attributes
    ----------
    job_key : str
        The key, a unique identifier for the job. (alias: ``jobKey``)
    process_instance_key : str
        The job's process instance key. (alias: ``processInstanceKey``)
    process_definition_key : str
        The key of the job's process definition. (alias: ``processDefinitionKey``)
    element_instance_key : str
        The unique key identifying the associated task, unique within the scope of the process instance.
        (alias: ``elementInstanceKey``)
    job_type : str
        The type of the job, should match what was requested. (alias: ``type``)
    process_definition_id : str
        The BPMN process ID of the job's process definition. (alias: ``processDefinitionId``)
    process_definition_version : int
        The version of the job's process definition. (alias: ``processDefinitionVersion``)
    element_id : str
        The associated task element ID. (alias: ``elementId``)
    custom_headers : dict
        A set of custom headers defined during modelling; returned as a serialized JSON document.
        (alias: ``customHeaders``)
    worker : str
        The name of the worker which activated this job. (alias: ``worker``)
    retries : int
        The amount of retries left to this job; should always be positive. (alias: ``retries``)
    deadline : int
        When the job can be activated again, sent as a UNIX epoch timestamp. (alias: ``deadline``)
    variables : dict
        All variables visible to the task scope, computed at activation time. (alias: ``variables``)
    tenant_id : str
        The ID of the tenant that owns the job. (alias: ``tenantId``)
    """
    job_key: str = Field(
        ..., alias="jobKey",
        description="the key, a unique identifier for the job"
    )
    process_instance_key: str = Field(
        ..., alias="processInstanceKey",
        description="the job's process instance key"
    )
    process_definition_key: str = Field(
        ..., alias="processDefinitionKey",
        description="the key of the job's process definition"
    )
    element_instance_key: str = Field(
        ..., alias="elementInstanceKey",
        description="the unique key identifying the associated task, unique within the scope of the process instance"
    )
    job_type: str = Field(
        ..., alias="type",
        description="the type of the job (should match what was requested)"
    )
    process_definition_id: str = Field(
        ..., alias="processDefinitionId",
        description="the bpmn process ID of the job's process definition"
    )
    process_definition_version: int = Field(
        ..., alias="processDefinitionVersion",
        description="the version of the job's process definition"
    )
    element_id: str = Field(
        ..., alias="elementId",
        description="the associated task element ID"
    )
    custom_headers: dict = Field(
        ..., alias="customHeaders",
        description="a set of custom headers defined during modelling; returned as a serialized JSON document"
    )
    worker: str = Field(
        ..., alias="worker",
        description="the name of the worker which activated this job"
    )
    retries: int = Field(
        ..., alias="retries",
        description="the amount of retries left to this job (should always be positive)"
    )
    deadline: int = Field(
        ..., alias="deadline",
        description="when the job can be activated again, sent as a UNIX epoch timestamp"
    )
    variables: dict = Field(
        ..., alias="variables",
        description="All variables visible to the task scope, computed at activation time"
    )
    tenant_id: str = Field(
        ..., alias="tenantId",
        description="The ID of the tenant that owns the job"
    )


class ActivatedJobResponse(JsonBaseModel):
    """
    Response model containing the list of activated jobs.

    Attributes
    ----------
    jobs : list[ActivatedJob]
        The list of activated jobs returned by the Camunda API. (alias: ``jobs``)
    """
    jobs: list[ActivatedJob] = Field(..., alias="jobs")


class JobFailedRequest(JsonBaseModel):
    """
    Request model for reporting a failed job to the Camunda API.

    Attributes
    ----------
    retries : int
        The amount of retries the job should have left. (alias: ``retries``)
    error_message : str | None
        An optional message describing why the job failed. Useful when a job runs out of retries
        and an incident is raised, as it can help explain the cause. (alias: ``errorMessage``)
    retry_back_off : int
        The backoff timeout in milliseconds before the next retry attempt. (alias: ``retryBackOff``)
    variables : dict | None
        JSON object that will instantiate the variables at the local scope of the job's associated task. (alias: ``variables``)
    """
    retries: int = Field(
        default=0, alias="retries",
        description="The amount of retries the job should have left"
    )
    error_message: str | None = Field(
        default=None, alias="errorMessage",
        description="An optional message describing why the job failed. This is particularly useful if a job runs out "
                    "of retries and an incident is raised, as this message can help explain why an incident was raised."
    )
    retry_back_off: int = Field(
        default=0, alias="retryBackOff",
        description="The backoff timeout (in ms) for the next retry."
    )
    variables: dict | None = Field(
        default=None, alias="variables",
        description="JSON object that will instantiate the variables at the local scope of the job's associated task."
    )


class ThrowErrorForJobRequest(JsonBaseModel):
    """
    Request model for throwing a BPMN error for a job in the Camunda API.

    Attributes
    ----------
    error_code : str
        The error code that will be matched with an error catch event. (alias: ``errorCode``)
    error_message : str | None
        An optional message providing additional context for the error. (alias: ``errorMessage``)
    variables : dict | None
        JSON object that will instantiate the variables at the local scope of the error catch event
        that catches the thrown error. (alias: ``variables``)
    """

    error_code: str = Field(
        ..., alias="errorCode",
        description="The error code that will be matched with an error catch event."
    )
    error_message: str | None = Field(
        default=None, alias="errorMessage",
        description="An error message that provides additional context."
    )
    variables: dict | None = Field(
        default=None, alias="variables",
        description="JSON object that will instantiate the variables at the local scope of the error catch event that "
                    "catches the thrown error."
    )
