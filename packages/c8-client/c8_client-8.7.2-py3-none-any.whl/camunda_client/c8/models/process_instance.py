from pydantic import Field, model_validator, ValidationError

from camunda_client.utils import JsonBaseModel


class ProcessInstanceStartInstructions(JsonBaseModel):
    """
    Instructions to start a process instance.

    Attributes
    ----------
    element_id : str
        Future extensions might include different types of start instructions, and the ability to set local variables
        for different flow scopes. For now, however, the start instruction is implicitly a 'startBeforeElement'
        instruction.
    """
    element_id: str = Field(
        ...,
        alias="elementId",
        description="Future extensions might include: different types of start instructions ability to set local "
                    "variables for different flow scopes For now, however, the start instruction is implicitly a "
                    "'startBeforeElement' instruction",
    )


class CreateProcessInstanceRequest(JsonBaseModel):
    """
    Request model to create a process instance.

    Attributes
    ----------
    process_definition_id : str | None
        The BPMN process ID of the process definition to start an instance of.
        Cannot be used together with processDefinitionKey.
    process_definition_version : int | None
        The version of the process. Only considered when a processDefinitionId is provided.
        By default, the latest version of the process is used.
    variables : dict | None
        JSON object that will instantiate the variables for the root variable scope of the process instance.
    tenant_id : str | None
        The tenant ID of the process definition.
    operation_reference : int | None
        A reference key chosen by the user that will be part of all records resulting from this operation.
        Must be > 0 if provided. Possible values: >= 1.
    start_instructions : list[ProcessInstanceStartInstructions] | None
        List of start instructions. By default, the process instance will start at the start event.
        If provided, the process instance will apply start instructions after it has been created.
    await_completion : bool
        Wait for the process instance to complete. If the process instance completion does not occur within
        the requestTimeout, the request will be closed. This can lead to a 504 response status.
        Disabled by default.
    fetch_variables : list[str]
        List of variable names to be included in the response.
        If empty, all visible variables in the root scope will be returned.
    request_timeout : int
        Timeout (in ms) the request waits for the process to complete.
        By default, or when set to 0, the generic request timeout configured in the cluster is applied.
    process_definition_key : str | None
        The unique key identifying the process definition, for example, returned for a process in the deploy resources
        endpoint. Cannot be used together with processDefinitionId.
    """
    process_definition_id: str | None = Field(
        default=None,
        alias="processDefinitionId",
        description="The BPMN process ID of the process definition to start an instance of.Cannot be used together with "
                    "processDefinitionKey.",
    )
    process_definition_version: int | None = Field(
        default=None,
        alias="processDefinitionVersion",
        description="The version of the process.Only considered when a processDefinitionId is provided. By default, "
                    "the latest version of the process is used.",
    )
    variables: dict | None = Field(
        default=None,
        alias="variables",
        description="JSON object that will instantiate the variables for the root variable scope of the process instance.",
    )
    tenant_id: str | None = Field(
        ..., alias="tenantId", description="The tenant ID of the process definition."
    )
    operation_reference: int | None = Field(
        default=None,
        alias="operationReference",
        description="A reference key chosen by the user that will be part of all records resulting from this operation. "
                    "Must be > 0 if provided. Possible values: >= 1",
    )

    start_instructions: list[ProcessInstanceStartInstructions] | None = Field(
        default=None,
        alias="startInstructions",
        description="List of start instructions. By default, the process instance will start at the start "
                    "event. If provided, the process instance will apply start instructions after it has been "
                    "created.",
    )

    await_completion: bool = Field(
        default=False,
        alias="awaitCompletion",
        description="Wait for the process instance to complete.If the process instance completion does not occur "
                    "within the requestTimeout, the request will be closed.This can lead to a 504 response status."
                    "Disabled by default.",
    )

    fetch_variables: list[str] = Field(
        default=[],
        alias="fetchVariables",
        description="List of variables names to be included in the response.If empty, all visible variables in the root "
                    "scope will be returned.",
    )

    request_timeout: int = Field(
        default=0,
        alias="requestTimeout",
        description="Timeout( in ms) the request waits for the process to complete.By default or when set to 0, the "
                    "generic request timeout configured in the cluster is applied.",
    )

    process_definition_key: str | None = Field(
        default=None,
        alias="processDefinitionKey",
        description="The unique key identifying the process definition, for example, returned for a process in the "
                    "deploy resources endpoint.Cannot be used together with processDefinitionId.",
    )

    @model_validator(mode="after")
    def check_exclusive_fields(self):
        if self.process_definition_id is not None and self.process_definition_key is not None:
            raise ValidationError(
                "CreateProcessInstanceRequest invalid; processDefinitionKey and processDefinitionId "
                "cannot be used together"
            )
        elif self.process_definition_id is None and self.process_definition_key is None:
            raise ValidationError(
                "CreateProcessInstanceRequest invalid; either processDefinitionKey or "
                "processDefinitionId must be defined"
            )
        return self


class CreateProcessInstanceResponse(JsonBaseModel):
    """
    Response model returned after creating a process instance.

    Attributes
    ----------
    process_definition_id : str
        The BPMN process ID of the process definition which was used to create the process instance.
    process_definition_version : int
        The version of the process definition which was used to create the process instance.
    tenant_id : str
        The tenant ID of the created process instance.
    variables : dict
        All the variables visible in the root scope.
    process_definition_key : str
        The key of the process definition which was used to create the process instance.
    process_instance_key : str
        The unique identifier of the created process instance; to be used wherever a request needs a
        process instance key (e.g., CancelProcessInstanceRequest).
    """

    process_definition_id: str = Field(
        ...,
        alias="processDefinitionId",
        description="The BPMN process ID of the process definition which was used to create the process instance.",
    )

    process_definition_version: int = Field(
        ...,
        alias="processDefinitionVersion",
        description="The version of the process definition which was used to create the process instance.",
    )

    tenant_id: str = Field(
        ...,
        alias="tenantId",
        description="The tenant ID of the created process instance.",
    )

    variables: dict = Field(
        default={},
        alias="variables",
        description="All the variables visible in the root scope.",
    )

    process_definition_key: str = Field(
        ...,
        alias="processDefinitionKey",
        description="The key of the process definition which was used to create the process instance.",
    )

    process_instance_key: str = Field(
        ...,
        alias="processInstanceKey",
        description="The unique identifier of the created process instance; to be used wherever a request needs a "
                    "process instance key (e.g.CancelProcessInstanceRequest).",
    )


class MappingInstructions(JsonBaseModel):
    """
    Instructions describing how to map elements when migrating a process instance.

    Attributes
    ----------
    source_element_id : str
        The element ID to migrate from.
    target_element_id : str
        The element ID to migrate into.
    """
    source_element_id: str = Field(
        ..., alias="sourceElementId", description="The element ID to migrate from."
    )
    target_element_id: str = Field(
        ..., alias="targetElementId", description="The element ID to migrate into."
    )


class MigrateProcessInstanceRequest(JsonBaseModel):
    """
    Request model to migrate a process instance to a different process definition.

    Attributes
    ----------
    operation_reference : int | None
        A reference key chosen by the user that will be part of all records resulting from this operation.
        Must be > 0 if provided.
    target_process_definition_key : str
        The key of process definition to migrate the process instance to.
    mapping_instructions : list[MappingInstructions]
        Mapping instructions.
    """
    operation_reference: int | None = Field(
        default=None,
        alias="operationReference",
        description="A reference key chosen by the user that will be part of all records resulting from this operation. "
                    "Must be > 0 if provided.",
    )
    target_process_definition_key: str = Field(
        ...,
        alias="targetProcessDefinitionKey",
        description="The key of process definition to migrate the process instance to.",
    )
    mapping_instructions: list[MappingInstructions] = Field(
        ..., alias="mappingInstructions", description="Mapping instructions."
    )


class VariableInstruction(JsonBaseModel):
    """
    Instructions for creating variables within a specific scope of a process instance.

    Attributes
    ----------
    scope_id : str
        The ID of the element in which scope the variables should be created. Leave empty to create the
        variables in the global scope of the process instance.
    variables : dict
        JSON document that will instantiate the variables for the root variable scope of the process instance.
        It must be a JSON object, as variables will be mapped in a key-value fashion.
    """
    scope_id: str = Field(
        default="",
        alias="scopeId",
        description="The ID of the element in which scope the variables should be created. Leave empty to create the "
                    "variables in the global scope of the process instance",
    )
    variables: dict = Field(
        ...,
        alias="variables",
        description="JSON document that will instantiate the variables for the root variable scope of the process "
                    "instance. It must be a JSON object, as variables will be mapped in a key-value fashion.",
    )


class ActivateInstructions(JsonBaseModel):
    """
    Instructions describing which element should be activated and related variable instructions.

    Attributes
    ----------
    element_id : str
        The ID of the element that should be activated.
    variable_instructions : list[VariableInstruction]
        Variable instructions.
    ancestorElementInstanceKey : int | None
        The key of the ancestor scope the element instance should be created in. Set to -1 to create the
        new element instance within an existing element instance of the flow scope.
    """
    element_id: str = Field(
        ...,
        alias="elementId",
        description="The ID of the element that should be activated.",
    )
    variable_instructions: list[VariableInstruction] = Field(
        default=[], alias="variableInstructions", description="Variable instructions."
    )
    ancestorElementInstanceKey: int | None = Field(
        default=-1,
        alias="ancestorElementInstanceKey",
        description="The key of the ancestor scope the element instance should be created in. Set to -1 to create the "
                    "new element instance within an existing element instance of the flow scope.",
    )


class TerminateInstructions(JsonBaseModel):
    """
    Instructions describing which element instance should be terminated.

    Attributes
    ----------
    element_instance_key : str
        The ID of the element that should be terminated.
    """

    element_instance_key: str = Field(
        ...,
        alias="elementInstanceKey",
        description="The ID of the element that should be terminated.",
    )


class ModifyProcessInstanceRequest(JsonBaseModel):
    """
    Request model to modify a running process instance by activating or terminating elements.

    Attributes
    ----------
    operation_reference : int | None
        A reference key chosen by the user that will be part of all records resulting from this operation.
        Must be > 0 if provided.
    activate_instructions : list[ActivateInstructions]
        Activate instructions.
    terminate_instructions : list[TerminateInstructions]
        Terminate instructions.
    """
    operation_reference: int | None = Field(
        default=None,
        alias="operationReference",
        description="A reference key chosen by the user that will be part of all records resulting from this operation. "
                    "Must be > 0 if provided.",
    )
    activate_instructions: list[ActivateInstructions] = Field(
        default=[], alias="activateInstructions", description="Activate instructions"
    )
    terminate_instructions: list[TerminateInstructions] = Field(
        default=[], alias="terminateInstructions", description="Terminate Instructions"
    )

    @model_validator(mode="after")
    def validate_model(self):
        if self.operation_reference is None or self.operation_reference < 1:
            raise ValidationError("Attribute 'operation_reference' must be >= 1")
