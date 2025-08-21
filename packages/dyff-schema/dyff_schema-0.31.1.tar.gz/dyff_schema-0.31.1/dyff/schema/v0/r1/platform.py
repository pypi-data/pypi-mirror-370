# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0
# fmt: off
"""Schema for the internal data representation of Dyff entities.

We use the following naming convention:

    * ``<Entity>``: A full-fledged entity that is tracked by the platform. It has
      an .id and the other dynamic system attributes like 'status'.
    * ``<Entity>Base``: The attributes of the Entity that are also attributes of
      the corresponding CreateRequest. Example: Number of replicas to use for
      an evaluation.
    * ``Foreign<Entity>``: Like <Entity>, but without dynamic system fields
      like 'status'. This type is used when we want to embed the full
      description of a resource inside of an outer resource that depends on it.
      We include the full dependency data structure so that downstream
      components don't need to be able to look it up by ID.
"""

# fmt: on
# mypy: disable-error-code="import-untyped"
import abc
import enum
import urllib.parse
from datetime import datetime
from enum import Enum
from typing import Any, Literal, NamedTuple, Optional, Type, Union

import pyarrow
import pydantic
from pydantic import StringConstraints
from typing_extensions import Annotated, TypeAlias

from ... import named_data_schema, product_schema
from ...version import SomeSchemaVersion
from .base import DyffSchemaBaseModel
from .dataset import arrow, make_item_type, make_response_type
from .version import SCHEMA_VERSION, SchemaVersion

SYSTEM_ATTRIBUTES = frozenset(["creationTime", "status", "reason"])


def _k8s_quantity_regex():
    # This is copy-pasted from the regex that operator-sdk generates for resource.Quantity types
    return r"^(\+|-)?(([0-9]+(\.[0-9]*)?)|(\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\+|-)?(([0-9]+(\.[0-9]*)?)|(\.[0-9]+))))?$"


def _k8s_label_regex():
    """A k8s label is like a DNS label but also allows ``.`` an ``_`` as separator
    characters."""
    return r"[a-z0-9A-Z]([-_.a-z0-9A-Z]{0,61}[a-z0-9A-Z])?"


def _k8s_label_maxlen():
    """Max length of a k8s label, same as for a DNS label."""
    return 63


def _dns_label_regex():
    """Alphanumeric characters separated by ``-``, maximum of 63 characters."""
    return r"[a-zA-Z0-9]([-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?"


def _dns_label_maxlen():
    """Max length of a DNS label."""
    return 63


def _dns_domain_regex():
    """One or more DNS labels separated by dots (``.``).

    Note that its maximum length is 253 characters, but we can't enforce this in the
    regex.
    """
    return rf"{_dns_label_regex()}(\.{_dns_label_regex()})*"


def _k8s_domain_maxlen():
    """Max length of a k8s domain.

    The DNS domain standard specifies 255 characters, but this includes the trailing dot
    and null terminator. We never include a trailing dot in k8s-style domains.
    """
    return 253


def _k8s_label_key_regex():
    """The format of keys for labels and annotations. Optional subdomain prefix followed
    by a k8s label.

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/

    Valid label keys have two segments: an optional prefix and name, separated
    by a slash (``/``). The name segment is required and must have 63 characters
    or fewer, consisting of alphanumeric characters separated by ``-``, ``.``,
    or ``_`` characters. The prefix is optional. If specified, it must be a
    DNS subdomain followed by a ``/`` character.

    Examples:

        * my-multi_segment.key
        * dyff.io/reserved-key
    """
    return rf"^({_dns_domain_regex()}/)?{_dns_label_regex()}$"


def _k8s_label_key_maxlen():
    """Max length of a label key.

    The prefix segment, if present, has a max length of 253 characters. The
    name segment has a max length of 63 characters.

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    # subdomain + '/' + label
    # Note that the domain regex can't enforce its max length because it can
    # have an arbitrary number of parts (part1.part2...), but the label regex
    # *does* enforce a max length, so checking the overall length is sufficient
    # to limit the domain part to 253 characters.
    return _k8s_domain_maxlen() + 1 + _k8s_label_maxlen()


def _k8s_label_value_regex():
    """The format of values for labels.

    Label values must satisfy the following:

        * must have 63 characters or fewer (can be empty)
        * unless empty, must begin and end with an alphanumeric character (``[a-z0-9A-Z]``)
        * could contain dashes (``-``), underscores (``_``), dots (``.``), and alphanumerics between

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    return rf"^({_k8s_label_regex()})?$"


def _k8s_label_value_maxlen():
    """Max length of a label value.

    Label values must have 63 characters or fewer (can be empty).

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    return _k8s_label_maxlen()


def _oci_image_tag_regex():
    """Regex matching valid image tags according to the OCI spec.

    See: https://github.com/opencontainers/distribution-spec/blob/main/spec.md#pull
    """
    return r"^[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}$"


def _oci_image_tag_maxlen():
    """Max length of valid image tags according to the OCI spec.

    See: https://github.com/opencontainers/distribution-spec/blob/main/spec.md#pull
    """
    return 127


def identifier_regex():
    """Python identifiers start with a letter or an underscore, and consist of letters,
    numbers, and underscores."""
    return r"^[a-zA-Z_][a-zA-Z0-9_]*$"


def identifier_maxlen():
    """There isn't really a max length for Python identifiers, but this seems like a
    reasonable limit for our use."""
    return 127


def title_maxlen() -> int:
    return 140


def summary_maxlen() -> int:
    return 280


def entity_id_regex() -> str:
    """An entity ID is a 32-character HEX string.

    TODO: This doesn't check whether the hex string is a valid UUID.
    """
    return r"^[a-f0-9]{32}$"


class Entities(str, enum.Enum):
    """The kinds of entities in the dyff system."""

    Account = "Account"
    Analysis = "Analysis"
    Audit = "Audit"
    AuditProcedure = "AuditProcedure"
    Concern = "Concern"
    DataSource = "DataSource"
    Dataset = "Dataset"
    Documentation = "Documentation"
    Evaluation = "Evaluation"
    Family = "Family"
    Hazard = "Hazard"
    History = "History"
    InferenceService = "InferenceService"
    InferenceSession = "InferenceSession"
    Measurement = "Measurement"
    Method = "Method"
    Model = "Model"
    Module = "Module"
    Report = "Report"
    Revision = "Revision"
    SafetyCase = "SafetyCase"
    Score = "Score"
    UseCase = "UseCase"


class Resources(str, enum.Enum):
    """The resource names corresponding to entities that have API endpoints."""

    Analysis = "analyses"
    Audit = "audits"
    AuditProcedure = "auditprocedures"
    Concern = "concerns"
    Dataset = "datasets"
    DataSource = "datasources"
    Descriptor = "descriptors"
    Documentation = "documentation"
    Evaluation = "evaluations"
    Family = "families"
    Hazard = "hazards"
    History = "histories"
    InferenceService = "inferenceservices"
    InferenceSession = "inferencesessions"
    Measurement = "measurements"
    Method = "methods"
    Model = "models"
    Module = "modules"
    Report = "reports"
    Revision = "revisions"
    SafetyCase = "safetycases"
    Score = "scores"
    UseCase = "usecases"

    Task = "tasks"
    """
    .. deprecated:: 0.5.0

        The Task resource no longer exists, but removing this enum entry
        breaks existing API keys.
    """

    ChoresValidateSchema = "chores/validate-schema"
    """Administrative task: Schema validation operations."""

    ALL = "*"

    @staticmethod
    def for_kind(kind: Entities) -> "Resources":
        try:
            return Resources[kind.value]
        except KeyError:
            raise ValueError(f"No Resources for Entity kind: {kind}")


EntityKindLiteral = Literal[
    "Analysis",
    "Audit",
    "AuditProcedure",
    "DataSource",
    "Dataset",
    "Evaluation",
    "Family",
    "Hazard",
    "History",
    "InferenceService",
    "InferenceSession",
    "Measurement",
    "Method",
    "Model",
    "Module",
    "Report",
    "Revision",
    "SafetyCase",
    "UseCase",
]


EntityID: TypeAlias = Annotated[str, StringConstraints(pattern=entity_id_regex())]  # type: ignore


class DyffModelWithID(DyffSchemaBaseModel):
    id: str = pydantic.Field(description="Unique identifier of the entity")
    account: str = pydantic.Field(description="Account that owns the entity")


class EntityIdentifier(DyffSchemaBaseModel):
    """Identifies a single entity."""

    @staticmethod
    def of(entity: "DyffEntityType") -> "EntityIdentifier":
        """Create an identifier that identifies the given entity."""
        return EntityIdentifier(kind=entity.kind, id=entity.id)

    id: str = pydantic.Field(description="The .id of the entity.")
    kind: EntityKindLiteral = pydantic.Field(
        description="The .kind of the entity.",
    )


def LabelKey() -> type[str]:
    return Annotated[
        str,
        StringConstraints(
            pattern=_k8s_label_key_regex(), max_length=_k8s_label_key_maxlen()
        ),
    ]  # type: ignore [return-value]


def LabelValue() -> type[str]:
    return Annotated[
        str,
        StringConstraints(
            pattern=_k8s_label_value_regex(), max_length=_k8s_label_value_maxlen()
        ),
    ]  # type: ignore [return-value]


def TagName() -> type[str]:
    return Annotated[
        str,
        StringConstraints(
            pattern=_oci_image_tag_regex(), max_length=_oci_image_tag_maxlen()
        ),
    ]  # type: ignore [return-value]


LabelKeyType: TypeAlias = LabelKey()  # type: ignore

LabelValueType: TypeAlias = LabelValue()  # type: ignore

TagNameType: TypeAlias = TagName()  # type: ignore


class Label(DyffSchemaBaseModel):
    """A key-value label for a resource. Used to specify identifying attributes of
    resources that are meaningful to users but do not imply semantics in the dyff
    system.

    We follow the kubernetes label conventions closely. See:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/labels
    """

    key: LabelKeyType = pydantic.Field(  # type: ignore
        description="The label key is a DNS label with an optional DNS domain"
        " prefix. For example: 'my-key', 'your.com/key_0'. Keys prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.",
    )

    value: LabelValueType = pydantic.Field(  # type: ignore
        description="The label value consists of alphanumeric characters"
        " separated by '.', '-', or '_'.",
    )


class Labeled(DyffSchemaBaseModel):
    labels: dict[LabelKeyType, LabelValueType] = pydantic.Field(  # type: ignore
        default_factory=dict,
        description="A set of key-value labels for the resource. Used to"
        " specify identifying attributes of resources that are meaningful to"
        " users but do not imply semantics in the dyff system.\n\n"
        "The keys are DNS labels with an optional DNS domain prefix."
        " For example: 'my-key', 'your.com/key_0'. Keys prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.\n\n"
        "The label values are alphanumeric characters separated by"
        " '.', '-', or '_'.\n\n"
        "We follow the kubernetes label conventions closely."
        " See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels",
        # Forbid entries that don't match the key patternProperties
        json_schema_extra={"additionalProperties": False},
    )


class Annotation(DyffSchemaBaseModel):
    key: str = pydantic.Field(
        pattern=_k8s_label_key_regex(),
        max_length=_k8s_domain_maxlen(),
        description="The annotation key. A DNS label with an optional DNS domain prefix."
        " For example: 'my-key', 'your.com/key_0'. Names prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.\n\n"
        "See https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations"
        " for detailed naming rules.",
    )

    value: str = pydantic.Field(
        description="The annotation value. An arbitrary string."
    )


Quantity: TypeAlias = Annotated[str, StringConstraints(pattern=_k8s_quantity_regex())]  # type: ignore


class ServiceClass(str, enum.Enum):
    """Defines the "quality of service" characteristics of a resource allocation."""

    STANDARD = "standard"
    PREEMPTIBLE = "preemptible"


class ResourceAllocation(DyffSchemaBaseModel):
    quantities: dict[LabelKeyType, Quantity] = pydantic.Field(  # type: ignore
        default_factory=dict,
        description="Mapping of resource keys to quantities to be allocated.",
    )

    serviceClass: ServiceClass = pydantic.Field(description="The service class")


class Status(DyffSchemaBaseModel):
    status: str = pydantic.Field(
        description="Top-level resource status (assigned by system)"
    )

    reason: Optional[str] = pydantic.Field(
        default=None, description="Reason for current status (assigned by system)"
    )


class DocumentationBase(DyffSchemaBaseModel):
    title: Optional[str] = pydantic.Field(
        default=None,
        description='A short plain string suitable as a title or "headline".',
    )

    summary: Optional[str] = pydantic.Field(
        default=None,
        description="A brief summary, suitable for display in"
        " small UI elements. Interpreted as Markdown. Excessively long"
        " summaries may be truncated in the UI, especially on small displays.",
    )

    fullPage: Optional[str] = pydantic.Field(
        default=None,
        description="Long-form documentation. Interpreted as"
        " Markdown. There are no length constraints, but be reasonable.",
    )


class Documentation(SchemaVersion, DocumentationBase):
    entity: Optional[str] = pydantic.Field(
        default=None,
        description="The ID of the documented entity. This is Optional for"
        " backward compatibility but it will always be populated in API responses.",
    )


class Documented(DyffSchemaBaseModel):
    documentation: DocumentationBase = pydantic.Field(
        default_factory=DocumentationBase,
        description="Documentation of the resource. The content is used to"
        " populate various views in the web UI.",
    )


class Metadata(DyffSchemaBaseModel):
    pass


class Mutable(DyffSchemaBaseModel):
    etag: str
    lastModificationTime: datetime


class DyffEntityMetadata(DyffSchemaBaseModel):
    revision: Optional[str] = pydantic.Field(
        default=None,
        description="Unique identifier of the current revision of the entity.",
    )

    documentation: DocumentationBase = pydantic.Field(
        default_factory=DocumentationBase,
        description="Documentation of the resource. The content is used to"
        " populate various views in the web UI.",
    )


class DyffEntity(Status, Labeled, SchemaVersion, DyffModelWithID):
    kind: Literal[
        "Analysis",
        "Audit",
        "AuditProcedure",
        "DataSource",
        "Dataset",
        "Evaluation",
        "Family",
        "Hazard",
        "History",
        "InferenceService",
        "InferenceSession",
        "Measurement",
        "Method",
        "Model",
        "Module",
        "Report",
        "Revision",
        "SafetyCase",
        "UseCase",
    ]

    metadata: DyffEntityMetadata = pydantic.Field(
        default_factory=DyffEntityMetadata,
        description="Entity metadata",
    )

    annotations: list[Annotation] = pydantic.Field(
        default_factory=list,
        description="A set of key-value annotations for the resource. Used to"
        " attach arbitrary non-identifying metadata to resources."
        " We follow the kubernetes annotation conventions closely.\n\n"
        " See: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations",
    )

    creationTime: datetime = pydantic.Field(
        description="Resource creation time (assigned by system)"
    )

    lastTransitionTime: Optional[datetime] = pydantic.Field(
        default=None, description="Time of last (status, reason) change."
    )

    @abc.abstractmethod
    def dependencies(self) -> list[str]:
        """List of IDs of resources that this resource depends on.

        The workflow cannot start until all dependencies have reached a success
        status. Workflows waiting for dependencies have
        ``reason = UnsatisfiedDependency``. If any dependency reaches a failure
        status, this workflow will also fail with ``reason = FailedDependency``.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_allocation(self) -> Optional[ResourceAllocation]:
        """Resource allocation required to run this workflow, if any."""
        raise NotImplementedError()


class Frameworks(str, enum.Enum):
    transformers = "transformers"


class InferenceServiceSources(str, enum.Enum):
    upload = "upload"
    build = "build"


class APIFunctions(str, enum.Enum):
    """Categories of API operations to which access can be granted."""

    consume = "consume"
    """Use the resource as a dependency in another workflow.

    Example: running an ``Evaluation`` on a ``Dataset`` requires ``consume``
    permission for the ``Dataset``.
    """

    create = "create"
    """Create a new instance of the resource.

    For resources that require uploading artifacts (such as ``Dataset``), also
    grants access to the ``upload`` and ``finalize`` endpoints.
    """

    get = "get"
    """Retrieve a single resource instance by ID."""

    query = "query"
    """Query the resource collection."""

    edit = "edit"
    """Edit properties of existing resources."""

    download = "download"
    """
    .. deprecated:: 0.5.0

        This functionality has been consolidated into ``data``.
    """

    upload = "upload"
    """
    .. deprecated:: 0.5.0

        This functionality has been consolidated into ``create``.
    """

    data = "data"
    """Download the raw data associated with the resource."""

    strata = "strata"
    """
    .. deprecated:: 0.5.0

        Similar functionality will be added in the future but with a different
        interface.
    """

    terminate = "terminate"
    """Set the resource status to ``Terminated``."""

    delete = "delete"
    """Set the resource status to ``Deleted``."""

    all = "*"


class AccessGrant(DyffSchemaBaseModel):
    """Grants access to call particular functions on particular instances of particular
    resource types.

    Access grants are **additive**; the subject of a set of grants has permission to do
    something if any part of any of those grants gives the subject that permission.
    """

    resources: list[Resources] = pydantic.Field(
        min_length=1, description="List of resource types to which the grant applies"
    )
    functions: list[APIFunctions] = pydantic.Field(
        min_length=1,
        description="List of functions on those resources to which the grant applies",
    )
    accounts: list[str] = pydantic.Field(
        default_factory=list,
        description="The access grant applies to all resources owned by the listed accounts",
    )
    entities: list[str] = pydantic.Field(
        default_factory=list,
        description="The access grant applies to all resources with IDs listed in 'entities'",
    )


class Role(DyffSchemaBaseModel):
    """A set of permissions."""

    grants: list[AccessGrant] = pydantic.Field(
        default_factory=list, description="The permissions granted to the role."
    )


class APIKey(Role):
    """A description of a Role (a set of permissions) granted to a single subject
    (either an account or a workload).

    Dyff API clients authenticate with a *token* that contains a cryptographically
    signed APIKey.
    """

    id: str = pydantic.Field(
        description="Unique ID of the resource. Maps to JWT 'jti' claim."
    )
    # TODO: Needs validator
    subject: str = pydantic.Field(
        description="Subject of access grants ('<kind>/<id>'). Maps to JWT 'sub' claim."
    )
    created: datetime = pydantic.Field(
        description="When the APIKey was created. Maps to JWT 'iat' claim."
    )
    expires: datetime = pydantic.Field(
        description="When the APIKey expires. Maps to JWT 'exp' claim."
    )
    secret: Optional[str] = pydantic.Field(
        default=None,
        description="For account keys: a secret value to check when verifying the APIKey",
    )


class Identity(DyffSchemaBaseModel):
    """The identity of an Account according to one or more external identity
    providers."""

    google: Optional[str] = pydantic.Field(default=None)


class Account(DyffSchemaBaseModel):
    """An Account in the system.

    All entities are owned by an Account.
    """

    name: str
    identity: Identity = pydantic.Field(default_factory=Identity)
    apiKeys: list[APIKey] = pydantic.Field(default_factory=list)
    # --- Added by system
    id: Optional[str] = None
    creationTime: Optional[datetime] = None


class FamilyMemberKind(str, enum.Enum):
    """The kinds of entities that can be members of a Family.

    These are resources for which it makes sense to have different versions or variants
    that evolve over time.
    """

    Dataset = "Dataset"
    InferenceService = "InferenceService"
    Method = "Method"
    Model = "Model"
    Module = "Module"


class FamilyMemberBase(DyffSchemaBaseModel):
    entity: EntityIdentifier = pydantic.Field(
        description="ID of the resource this member references.",
    )

    description: Optional[Annotated[str, StringConstraints(max_length=summary_maxlen())]] = pydantic.Field(  # type: ignore
        default=None,
        description="A short description of the member."
        " This should describe how this version of the resource"
        " is different from other versions.",
    )


class FamilyMember(FamilyMemberBase):
    name: TagNameType = pydantic.Field(
        description="An interpretable identifier for the member that is unique"
        " in the context of the corresponding Family.",
    )

    family: str = pydantic.Field(
        description="Identifier of the Family containing this tag."
    )

    creationTime: datetime = pydantic.Field(
        description="Tag creation time (assigned by system)"
    )


class FamilyMembers(DyffSchemaBaseModel):
    members: dict[TagNameType, FamilyMember] = pydantic.Field(
        default_factory=dict,
        description="Mapping of names to IDs of member resources.",
    )


class FamilyBase(DyffSchemaBaseModel):
    memberKind: FamilyMemberKind = pydantic.Field(
        description="The kind of resource that comprises the family.",
    )


class Family(DyffEntity, FamilyBase, FamilyMembers):
    kind: Literal["Family"] = "Family"

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class RevisionMetadata(DyffSchemaBaseModel):
    previousRevision: Optional[str] = pydantic.Field(
        default=None,
        description="The ID of the revision from which this revision was derived."
        "If None, then this is the first revision of the entity.",
    )
    creationTime: datetime = pydantic.Field(
        description="The time when the Revision was created"
    )


class ForeignRevision(RevisionMetadata):
    id: str = pydantic.Field(description="Unique identifier of the entity")


# Note: The 'Revision' class itself is defined all the way at the end of this
# file, because OpenAPI generation doesn't work with the Python < 3.10
# "ForwardDeclaration" syntax.


class History(DyffEntity):
    kind: Literal["History"] = "History"

    historyOf: str = pydantic.Field(
        description="The ID of the entity described by this History."
    )

    latest: ForeignRevision = pydantic.Field(description="The latest Revision")
    revisions: list[ForeignRevision] = pydantic.Field(
        description="The list of known Revisions, in chronological order (newest last)."
    )


class ConcernBase(Documented):
    pass


class Concern(ConcernBase, DyffEntity):
    def label_key(self) -> str:
        return f"{Resources[self.kind].value}.dyff.io/{self.id}"

    def label_value(self) -> str:
        return "1"

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class Hazard(Concern):
    kind: Literal["Hazard"] = Entities.Hazard.value


class UseCase(Concern):
    kind: Literal["UseCase"] = Entities.UseCase.value


# ----------------------------------------------------------------------------


class Digest(DyffSchemaBaseModel):
    md5: Optional[str] = pydantic.Field(
        default=None, description="md5 digest of artifact data"
    )


class Artifact(DyffSchemaBaseModel):
    # TODO: In v1, rename this to 'contentType' or something and commit to making it the MIME type
    kind: Optional[str] = pydantic.Field(
        default=None, description="The kind of artifact"
    )
    path: str = pydantic.Field(
        description="The relative path of the artifact within the tree"
    )
    digest: Digest = pydantic.Field(
        default_factory=Digest,
        description="One or more message digests (hashes) of the artifact data",
    )


class StorageSignedURL(DyffSchemaBaseModel):
    url: str = pydantic.Field(description="The signed URL")
    method: str = pydantic.Field(description="The HTTP method applicable to the URL")
    headers: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Mandatory headers that must be passed with the request",
    )


class ArtifactURL(DyffSchemaBaseModel):
    artifact: Artifact
    signedURL: StorageSignedURL


class AuditRequirement(DyffSchemaBaseModel):
    """An evaluation report that must exist in order to apply an AuditProcedure."""

    dataset: str
    rubric: str


class AuditProcedure(DyffEntity):
    """An audit procedure that can be run against a set of evaluation reports."""

    kind: Literal["AuditProcedure"] = Entities.AuditProcedure.value

    name: str
    requirements: list[AuditRequirement] = pydantic.Field(default_factory=list)

    def dependencies(self) -> list[str]:
        # Note that ``requirements`` are not "dependencies" because they don't
        # refer to a specific entity
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class Audit(DyffEntity):
    """An instance of applying an AuditProcedure to an InferenceService."""

    kind: Literal["Audit"] = Entities.Audit.value

    auditProcedure: str = pydantic.Field(description="The AuditProcedure to run.")

    inferenceService: str = pydantic.Field(description="The InferenceService to audit.")

    def dependencies(self) -> list[str]:
        return [self.auditProcedure, self.inferenceService]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class DataSource(DyffEntity):
    """A source of raw data from which a Dataset can be built."""

    kind: Literal["DataSource"] = Entities.DataSource.value

    name: str
    sourceKind: str
    source: Optional[str] = None

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ArchiveFormat(DyffSchemaBaseModel):
    """Specification of the archives that comprise a DataSource."""

    name: str
    format: str


class ExtractorStep(DyffSchemaBaseModel):
    """Description of a step in the process of turning a hierarchical DataSource into a
    Dataset."""

    action: str
    name: Optional[str] = None
    type: Optional[str] = None


class DyffDataSchema(DyffSchemaBaseModel):
    components: list[str] = pydantic.Field(
        min_length=1,
        description="A list of named dyff data schemas. The final schema is"
        " the composition of these component schemas.",
    )
    schemaVersion: SomeSchemaVersion = pydantic.Field(
        default=SCHEMA_VERSION,  # type: ignore [arg-type]
        description="The dyff schema version",
    )

    def model_type(self) -> Type[DyffSchemaBaseModel]:
        """The composite model type."""
        return product_schema(
            named_data_schema(c, self.schemaVersion) for c in self.components
        )


class DataSchema(DyffSchemaBaseModel):
    arrowSchema: str = pydantic.Field(
        description="The schema in Arrow format, encoded with"
        " dyff.schema.arrow.encode_schema(). This is required, but can be"
        " populated from a DyffDataSchema.",
    )
    dyffSchema: Optional[DyffDataSchema] = pydantic.Field(
        default=None, description="The schema in DyffDataSchema format"
    )
    jsonSchema: Optional[dict[str, Any]] = pydantic.Field(
        default=None, description="The schema in JSON Schema format"
    )

    @staticmethod
    def from_model(model: Type[DyffSchemaBaseModel]) -> "DataSchema":
        arrowSchema = arrow.encode_schema(arrow.arrow_schema(model))
        jsonSchema = model.model_json_schema()
        return DataSchema(arrowSchema=arrowSchema, jsonSchema=jsonSchema)

    @staticmethod
    def make_input_schema(
        schema: Union[pyarrow.Schema, Type[DyffSchemaBaseModel], DyffDataSchema],
    ) -> "DataSchema":
        """Construct a complete ``DataSchema`` for inference inputs.

        This function will add required special fields for input data and then
        convert the augmented schema as necessary to populate at least the
        required ``arrowSchema`` field in the resulting ``DataSchema``.
        """
        if isinstance(schema, pyarrow.Schema):
            arrowSchema = arrow.encode_schema(arrow.make_item_schema(schema))
            return DataSchema(arrowSchema=arrowSchema)
        elif isinstance(schema, DyffDataSchema):
            item_model = make_item_type(schema.model_type())
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(item_model))
            jsonSchema = item_model.model_json_schema()
            return DataSchema(
                arrowSchema=arrowSchema, dyffSchema=schema, jsonSchema=jsonSchema
            )
        else:
            item_model = make_item_type(schema)
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(item_model))
            jsonSchema = item_model.model_json_schema()
            return DataSchema(arrowSchema=arrowSchema, jsonSchema=jsonSchema)

    @staticmethod
    def make_output_schema(
        schema: Union[pyarrow.Schema, Type[DyffSchemaBaseModel], DyffDataSchema],
    ) -> "DataSchema":
        """Construct a complete ``DataSchema`` for inference outputs.

        This function will add required special fields for input data and then
        convert the augmented schema as necessary to populate at least the
        required ``arrowSchema`` field in the resulting ``DataSchema``.
        """
        if isinstance(schema, pyarrow.Schema):
            arrowSchema = arrow.encode_schema(arrow.make_response_schema(schema))
            return DataSchema(arrowSchema=arrowSchema)
        elif isinstance(schema, DyffDataSchema):
            response_model = make_response_type(schema.model_type())
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(response_model))
            jsonSchema = response_model.model_json_schema()
            return DataSchema(
                arrowSchema=arrowSchema, dyffSchema=schema, jsonSchema=jsonSchema
            )
        else:
            response_model = make_response_type(schema)
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(response_model))
            jsonSchema = response_model.model_json_schema()
            return DataSchema(arrowSchema=arrowSchema, jsonSchema=jsonSchema)


class SchemaAdapter(DyffSchemaBaseModel):
    kind: str = pydantic.Field(
        description="Name of a schema adapter available on the platform",
    )

    configuration: Optional[dict[str, Any]] = pydantic.Field(
        default=None,
        description="Configuration for the schema adapter. Must be encodable as JSON.",
    )


class DataView(DyffSchemaBaseModel):
    id: str = pydantic.Field(description="Unique ID of the DataView")
    viewOf: str = pydantic.Field(
        description="ID of the resource that this is a view of"
    )
    schema_: DataSchema = pydantic.Field(
        alias="schema", description="Schema of the output of this view"
    )
    adapterPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Adapter pipeline to apply to produce the view"
    )


class DatasetBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the Dataset")
    artifacts: list[Artifact] = pydantic.Field(
        min_length=1, description="Artifacts that comprise the dataset"
    )
    schema_: DataSchema = pydantic.Field(
        alias="schema", description="Schema of the dataset"
    )
    views: list[DataView] = pydantic.Field(
        default_factory=list,
        description="Available views of the data that alter its schema.",
    )


class Dataset(DyffEntity, DatasetBase):
    """An "ingested" data set in our standardized PyArrow format."""

    kind: Literal["Dataset"] = Entities.Dataset.value

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ModelSourceKinds(str, enum.Enum):
    GitLFS = "GitLFS"
    HuggingFaceHub = "HuggingFaceHub"
    Mock = "Mock"
    OpenLLM = "OpenLLM"
    Upload = "Upload"


class ModelSourceGitLFS(DyffSchemaBaseModel):
    url: pydantic.HttpUrl = pydantic.Field(
        description="The URL of the Git LFS repository"
    )


class ModelSourceHuggingFaceHub(DyffSchemaBaseModel):
    """These arguments are forwarded to huggingface_hub.snapshot_download()"""

    repoID: str
    revision: str
    allowPatterns: Optional[list[str]] = None
    ignorePatterns: Optional[list[str]] = None


class ModelSourceOpenLLM(DyffSchemaBaseModel):
    modelKind: str = pydantic.Field(
        description="The kind of model (c.f. 'openllm build <modelKind>')"
    )

    modelID: str = pydantic.Field(
        description="The specific model identifier (c.f. 'openllm build ... --model-id <modelId>')",
    )

    modelVersion: str = pydantic.Field(
        description="The version of the model (e.g., a git commit hash)"
    )


class ModelSource(DyffSchemaBaseModel):
    kind: ModelSourceKinds = pydantic.Field(description="The kind of model source")

    gitLFS: Optional[ModelSourceGitLFS] = pydantic.Field(
        default=None, description="Specification of a Git LFS source"
    )

    huggingFaceHub: Optional[ModelSourceHuggingFaceHub] = pydantic.Field(
        default=None, description="Specification of a HuggingFace Hub source"
    )

    openLLM: Optional[ModelSourceOpenLLM] = pydantic.Field(
        default=None, description="Specification of an OpenLLM source"
    )


class AcceleratorGPU(DyffSchemaBaseModel):
    hardwareTypes: list[str] = pydantic.Field(
        min_length=1,
        description="Acceptable GPU hardware types.",
    )
    count: int = pydantic.Field(default=1, description="Number of GPUs required.")
    memory: Optional[Quantity] = pydantic.Field(
        default=None,
        description="[DEPRECATED] Amount of GPU memory required, in k8s Quantity notation",
    )


class Accelerator(DyffSchemaBaseModel):
    kind: str = pydantic.Field(
        description="The kind of accelerator; available kinds are {{GPU}}"
    )
    gpu: Optional[AcceleratorGPU] = pydantic.Field(
        default=None, description="GPU accelerator options"
    )


class ModelResources(DyffSchemaBaseModel):
    storage: Quantity = pydantic.Field(
        description="Amount of storage required for packaged model, in k8s Quantity notation",
    )

    memory: Optional[Quantity] = pydantic.Field(
        default=None,
        description="Amount of memory required to run the model on CPU, in k8s Quantity notation",
    )


class ModelStorageMedium(str, enum.Enum):
    Mock = "Mock"
    ObjectStorage = "ObjectStorage"
    PersistentVolume = "PersistentVolume"
    FUSEVolume = "FUSEVolume"


class ModelArtifactKind(str, enum.Enum):
    HuggingFaceCache = "HuggingFaceCache"
    Mock = "Mock"


class ModelArtifactHuggingFaceCache(DyffSchemaBaseModel):
    repoID: str = pydantic.Field(
        description="Name of the model in the HuggingFace cache"
    )
    revision: str = pydantic.Field(description="Model revision")

    def snapshot_path(self) -> str:
        return f"models--{self.repoID.replace('/', '--')}/snapshots/{self.revision}"


class ModelArtifact(DyffSchemaBaseModel):
    kind: ModelArtifactKind = pydantic.Field(
        description="How the model data is represented"
    )
    huggingFaceCache: Optional[ModelArtifactHuggingFaceCache] = pydantic.Field(
        default=None, description="Model stored in a HuggingFace cache"
    )


class ModelStorage(DyffSchemaBaseModel):
    medium: ModelStorageMedium = pydantic.Field(description="Storage medium")


class ModelBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the Model.")

    artifact: ModelArtifact = pydantic.Field(
        description="How the model data is represented"
    )

    storage: ModelStorage = pydantic.Field(description="How the model data is stored")


class ModelSpec(ModelBase):
    source: ModelSource = pydantic.Field(
        description="Source from which the model artifact was obtained"
    )

    resources: ModelResources = pydantic.Field(
        description="Resource requirements of the model."
    )

    accelerators: Optional[list[Accelerator]] = pydantic.Field(
        default=None,
        description="Accelerator hardware that is compatible with the model.",
    )


class Model(DyffEntity, ModelSpec):
    """A Model is the "raw" form of an inference model, from which one or more
    InferenceServices may be built."""

    kind: Literal["Model"] = Entities.Model.value

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class InferenceServiceBuilder(DyffSchemaBaseModel):
    kind: str
    args: Optional[list[str]] = None


class InferenceServiceRunnerKind(str, Enum):
    BENTOML_SERVICE_OPENLLM = "bentoml_service_openllm"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"
    STANDALONE = "standalone"
    VLLM = "vllm"


class ContainerImageSource(DyffSchemaBaseModel):
    host: str = pydantic.Field(description="The host of the container image registry.")
    name: str = pydantic.Field(
        description="The name of the image",
        # https://github.com/opencontainers/distribution-spec/blob/main/spec.md#pull
        pattern=r"^[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*(\/[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*)*$",
    )
    digest: str = pydantic.Field(
        description="The digest of the image. The image is always pulled by"
        " digest, even if 'tag' is specified.",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    tag: Optional[TagNameType] = pydantic.Field(
        default=None,
        description="The tag of the image. Although the image is always pulled"
        " by digest, including the tag is strongly recommended as it is often"
        " the main source of versioning information.",
    )

    def url(self) -> str:
        return f"{self.host}/{self.name}@{self.digest}"

    @pydantic.field_validator("host")
    def validate_host(cls, v: str):
        if "/" in v:
            raise ValueError(
                "host: slashes not allowed; do not specify a scheme or path"
            )
        if "_" in v:
            # https://docs.docker.com/reference/cli/docker/image/tag/#description
            raise ValueError(
                "host: image registry hostnames may not contain underscores"
            )

        # This works because we know there are no slashes in the value
        # "Following the syntax specifications in RFC 1808, urlparse recognizes
        # a netloc only if it is properly introduced by ‘//’. Otherwise the
        # input is presumed to be a relative URL and thus to start with a path
        # component."
        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        parsed = urllib.parse.urlparse(f"//{v}")
        if (
            parsed.scheme
            or parsed.path
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "host: must be 'hostname' or 'hostname:port', and nothing else"
            )

        return v


class InferenceServiceRunner(DyffSchemaBaseModel):
    kind: InferenceServiceRunnerKind

    # TODO: (DYFF-421) Make .image required
    image: Optional[ContainerImageSource] = pydantic.Field(
        default=None,
        description="The container image that implements the runner. This field is"
        " optional for schema backwards-compatibility, but creating new"
        " services with image=None will result in an error.",
    )

    args: Optional[list[str]] = pydantic.Field(
        default=None, description="Command line arguments to forward to the runner"
    )

    accelerator: Optional[Accelerator] = pydantic.Field(
        default=None, description="Optional accelerator hardware to use, per node."
    )

    resources: ModelResources = pydantic.Field(
        description="Resource requirements to run the service, per node."
    )

    nodes: int = pydantic.Field(
        default=1,
        ge=1,
        description="Number of nodes. The resource specs apply to *each node*.",
    )


class InferenceInterface(DyffSchemaBaseModel):
    endpoint: str = pydantic.Field(description="HTTP endpoint for inference.")

    outputSchema: DataSchema = pydantic.Field(
        description="Schema of the inference outputs.",
    )

    inputPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Input adapter pipeline."
    )

    outputPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Output adapter pipeline."
    )


class ForeignModel(DyffModelWithID, ModelBase):
    pass


class InferenceServiceBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the service.")

    builder: Optional[InferenceServiceBuilder] = pydantic.Field(
        default=None,
        description="Configuration of the Builder used to build the service.",
    )

    # FIXME: (DYFF-261) .runner should be required
    runner: Optional[InferenceServiceRunner] = pydantic.Field(
        default=None, description="Configuration of the Runner used to run the service."
    )

    interface: InferenceInterface = pydantic.Field(
        description="How to move data in and out of the service."
    )

    outputViews: list[DataView] = pydantic.Field(
        default_factory=list,
        description="Views of the output data for different purposes.",
    )


class InferenceServiceSpec(InferenceServiceBase):
    model: Optional[ForeignModel] = pydantic.Field(
        default=None,
        description="The Model backing this InferenceService, if applicable.",
    )


class InferenceService(DyffEntity, InferenceServiceSpec):
    """An InferenceService is an inference model packaged as a Web service."""

    kind: Literal["InferenceService"] = Entities.InferenceService.value

    def dependencies(self) -> list[str]:
        result = []
        if self.model is not None:
            result.append(self.model.id)
        return result

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ForeignInferenceService(DyffModelWithID, InferenceServiceSpec):
    pass


class InferenceSessionBase(DyffSchemaBaseModel):
    expires: Optional[datetime] = pydantic.Field(
        default=None,
        description="Expiration time for the session. Use of this field is recommended to avoid accidental compute costs.",
    )

    replicas: int = pydantic.Field(default=1, description="Number of model replicas")

    accelerator: Optional[Accelerator] = pydantic.Field(
        default=None, description="Accelerator hardware to use, per node."
    )

    useSpotPods: bool = pydantic.Field(
        default=True,
        description="Use preemptible 'spot pods' for cheaper computation."
        " Note that some accelerator types may not be available in non-spot pods.",
    )


class InferenceSessionSpec(InferenceSessionBase):
    inferenceService: ForeignInferenceService = pydantic.Field(
        description="InferenceService ID"
    )


class InferenceSession(DyffEntity, InferenceSessionSpec):
    """An InferenceSession is a deployment of an InferenceService that exposes an API
    for interactive queries."""

    kind: Literal["InferenceSession"] = Entities.InferenceSession.value

    def dependencies(self) -> list[str]:
        return [self.inferenceService.id]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class InferenceSessionAndToken(DyffSchemaBaseModel):
    inferencesession: InferenceSession
    token: str


class InferenceSessionReference(DyffSchemaBaseModel):
    session: str = pydantic.Field(
        description="The ID of a running inference session.",
    )

    interface: InferenceInterface = pydantic.Field(
        description="How to move data in and out of the service."
    )


class DatasetFilter(DyffSchemaBaseModel):
    """A rule for restrcting which instances in a Dataset are returned."""

    field: str
    relation: str
    value: str


class TaskSchema(DyffSchemaBaseModel):
    # InferenceServices must consume a *subset* of this schema
    input: DataSchema
    # InferenceServices must output a *superset* of this schema
    output: DataSchema
    # This will be an enumerated tag specifying task semantics (e.g., Classification, TextGeneration)
    objective: str


class EvaluationClientConfiguration(DyffSchemaBaseModel):
    badRequestPolicy: Literal["Abort", "Skip"] = pydantic.Field(
        default="Abort",
        description="What to do if an inference call raises a 400 Bad Request"
        " or a similar error that indicates a problem with the input instance."
        " Abort (default): the evaluation fails immediately."
        " Skip: output None for the bad instance and continue.",
    )

    transientErrorRetryLimit: int = pydantic.Field(
        default=120,
        ge=0,
        description="How many times to retry transient errors before the"
        " evaluation fails. The count is reset after a successful inference."
        " Note that transient errors often occur during inference service"
        " startup. The maximum time that the evaluation will wait for a"
        " service (re)start is (retry limit) * (retry delay).",
    )

    transientErrorRetryDelaySeconds: int = pydantic.Field(
        default=30,
        ge=1,
        description="How long to wait before retrying a transient error."
        " Note that transient errors often occur during inference service"
        " startup. The maximum time that the evaluation will wait for a"
        " service (re)start is (retry limit) * (retry delay).",
    )

    duplicateOutputPolicy: Literal["Deduplicate", "Error", "Ignore"] = pydantic.Field(
        default="Deduplicate",
        description="What to do if there are missing outputs."
        " Deduplicate (default): output only one of the duplicates, chosen"
        " arbitrarily. Error: the evaluation fails. Ignore: duplicates are"
        " retained in the output."
        " Setting this to Error is discouraged because duplicates can"
        " arise in normal operation if the client restarts due to"
        " a transient failure.",
    )

    missingOutputPolicy: Literal["Error", "Ignore"] = pydantic.Field(
        default="Error",
        description="What to do if there are missing outputs."
        " Error (default): the evaluation fails. Ignore: no error.",
    )

    requestTimeoutSeconds: int = pydantic.Field(
        default=30, ge=0, description="The timeout delay for requests."
    )


class EvaluationBase(DyffSchemaBaseModel):
    dataset: str = pydantic.Field(description="The Dataset to evaluate on.")

    replications: int = pydantic.Field(
        default=1, description="Number of replications to run."
    )

    # TODO: This should be in the client config object
    workersPerReplica: Optional[int] = pydantic.Field(
        default=None,
        description="Number of data workers per inference service replica.",
    )

    client: EvaluationClientConfiguration = pydantic.Field(
        default_factory=EvaluationClientConfiguration,
        description="Configuration for the evaluation client.",
    )


class Evaluation(DyffEntity, EvaluationBase):
    """A description of how to run an InferenceService on a Dataset to obtain a set of
    evaluation results."""

    kind: Literal["Evaluation"] = Entities.Evaluation.value

    inferenceSession: InferenceSessionSpec = pydantic.Field(
        description="Specification of the InferenceSession that will perform"
        " inference for the evaluation.",
    )

    inferenceSessionReference: Optional[str] = pydantic.Field(
        default=None,
        description="ID of a running inference session that will be used"
        " for the evaluation instead of starting a new one.",
    )

    def dependencies(self) -> list[str]:
        # TODO: It would be nice if the session could be a dependency,
        # so that the client doesn't start until the session is ready, but
        # dyff-orchestrator can't handle dependencies on sessions currently.
        return [self.dataset, self.inferenceSession.inferenceService.id]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ModuleBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the Module")
    artifacts: list[Artifact] = pydantic.Field(
        min_length=1, description="Artifacts that comprise the Module implementation"
    )


class Module(DyffEntity, ModuleBase):
    """An extension module that can be loaded into Report workflows."""

    kind: Literal["Module"] = Entities.Module.value

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ReportBase(DyffSchemaBaseModel):
    rubric: str = pydantic.Field(
        description="The scoring rubric to apply (e.g., 'classification.TopKAccuracy').",
    )

    evaluation: str = pydantic.Field(
        description="The evaluation (and corresponding output data) to run the report on."
    )

    modules: list[str] = pydantic.Field(
        default_factory=list,
        description="Additional modules to load into the report environment",
    )


class Report(DyffEntity, ReportBase):
    """A Report transforms raw model outputs into some useful statistics.

    .. deprecated:: 0.8.0

        Report functionality has been refactored into the
        Method/Measurement/Analysis apparatus. Creation of new Reports is
        disabled.
    """

    kind: Literal["Report"] = Entities.Report.value

    dataset: str = pydantic.Field(description="The input dataset.")

    inferenceService: str = pydantic.Field(
        description="The inference service used in the evaluation"
    )

    model: Optional[str] = pydantic.Field(
        default=None,
        description="The model backing the inference service, if applicable",
    )

    datasetView: Optional[DataView] = pydantic.Field(
        default=None,
        description="View of the input dataset required by the report (e.g., ground-truth labels).",
    )

    evaluationView: Optional[DataView] = pydantic.Field(
        default=None,
        description="View of the evaluation output data required by the report.",
    )

    def dependencies(self) -> list[str]:
        return [self.evaluation] + self.modules

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class QueryableDyffEntity(DyffSchemaBaseModel):
    id: str = pydantic.Field(description="Unique identifier of the entity")
    name: str = pydantic.Field(description="Descriptive name of the resource")


class MeasurementLevel(str, enum.Enum):
    Dataset = "Dataset"
    Instance = "Instance"


class AnalysisOutputQueryFields(DyffSchemaBaseModel):
    analysis: Optional[str] = pydantic.Field(
        default=None,
        description="ID of the Analysis that produced the output.",
    )

    method: QueryableDyffEntity = pydantic.Field(
        description="Identifying information about the Method that was run to produce the output."
    )

    inputs: Optional[list[str]] = pydantic.Field(
        default=None,
        description="IDs of resources that were inputs to the Analysis.",
    )


class MeasurementSpec(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="Descriptive name of the Measurement.")
    description: Optional[str] = pydantic.Field(
        default=None, description="Long-form description, interpreted as Markdown."
    )
    level: MeasurementLevel = pydantic.Field(description="Measurement level")
    schema_: DataSchema = pydantic.Field(
        alias="schema",
        description="Schema of the measurement data. Instance-level measurements must include an _index_ field.",
    )


class SafetyCaseSpec(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="Descriptive name of the SafetyCase.")
    description: Optional[str] = pydantic.Field(
        default=None, description="Long-form description, interpreted as Markdown."
    )


class MethodImplementationKind(str, enum.Enum):
    JupyterNotebook = "JupyterNotebook"
    PythonFunction = "PythonFunction"

    PythonRubric = "PythonRubric"
    """A Rubric generates an instance-level measurement, consuming a Dataset and an
    Evaluation.

    .. deprecated:: 0.8.0

        Report functionality has been refactored into the
        Method/Measurement/Analysis apparatus. Creation of new Reports is
        disabled.
    """


class MethodImplementationJupyterNotebook(DyffSchemaBaseModel):
    notebookModule: str = pydantic.Field(
        description="ID of the Module that contains the notebook file."
        " This does *not* add the Module as a dependency; you must do that separately."
    )
    notebookPath: str = pydantic.Field(
        description="Path to the notebook file relative to the Module root directory."
    )


class MethodImplementationPythonFunction(DyffSchemaBaseModel):
    fullyQualifiedName: str = pydantic.Field(
        description="The fully-qualified name of the Python function to call."
    )


class MethodImplementationPythonRubric(DyffSchemaBaseModel):
    """A Rubric generates an instance-level measurement, consuming a Dataset and an
    Evaluation.

    .. deprecated:: 0.8.0

        Report functionality has been refactored into the
        Method/Measurement/Analysis apparatus. Creation of new Reports is
        disabled.
    """

    fullyQualifiedName: str = pydantic.Field(
        description="The fully-qualified name of the Python Rubric to run."
    )


class MethodImplementation(DyffSchemaBaseModel):
    kind: str = pydantic.Field(description="The kind of implementation")
    pythonFunction: Optional[MethodImplementationPythonFunction] = pydantic.Field(
        default=None, description="Specification of a Python function to call."
    )
    pythonRubric: Optional[MethodImplementationPythonRubric] = pydantic.Field(
        default=None, description="@deprecated Specification of a Python Rubric to run."
    )
    jupyterNotebook: Optional[MethodImplementationJupyterNotebook] = pydantic.Field(
        default=None, description="Specification of a Jupyter notebook to run."
    )


class MethodInputKind(str, enum.Enum):
    Dataset = Entities.Dataset.value
    Evaluation = Entities.Evaluation.value
    Measurement = Entities.Measurement.value

    Report = Entities.Report.value
    """
    .. deprecated:: 0.8.0

        The Report entity is deprecated, but we accept it as an analysis input
        for backward compatibility.
    """


class MethodOutputKind(str, enum.Enum):
    Measurement = Entities.Measurement.value
    SafetyCase = Entities.SafetyCase.value


class MethodParameter(DyffSchemaBaseModel):
    keyword: str = pydantic.Field(
        description="The parameter is referred to by 'keyword' in the context of the method implementation."
    )
    description: Optional[str] = pydantic.Field(
        default=None, description="Long-form description, interpreted as Markdown."
    )


class MethodInput(DyffSchemaBaseModel):
    kind: MethodInputKind = pydantic.Field(description="The kind of input artifact.")
    keyword: str = pydantic.Field(
        description="The input is referred to by 'keyword' in the context of the method implementation."
    )
    description: Optional[str] = pydantic.Field(
        default=None, description="Long-form description, interpreted as Markdown."
    )


class MethodOutput(DyffSchemaBaseModel):
    kind: MethodOutputKind = pydantic.Field(description="The kind of output artifact")
    measurement: Optional[MeasurementSpec] = pydantic.Field(
        default=None, description="Specification of a Measurement output."
    )
    safetyCase: Optional[SafetyCaseSpec] = pydantic.Field(
        default=None, description="Specification of a SafetyCase output."
    )


class MethodScope(str, enum.Enum):
    InferenceService = Entities.InferenceService.value
    Evaluation = Entities.Evaluation.value


class ScoreSpec(DyffSchemaBaseModel):
    name: str = pydantic.Field(
        description="The name of the score. Used as a key for retrieving score data."
        " Must be unique within the Method context.",
        pattern=identifier_regex(),
        max_length=identifier_maxlen(),
    )

    title: str = pydantic.Field(
        description="The title text to use when displaying score information.",
        max_length=title_maxlen(),
    )

    summary: str = pydantic.Field(
        description="A short text description of what the score measures.",
        max_length=summary_maxlen(),
    )

    valence: Literal["positive", "negative", "neutral"] = pydantic.Field(
        default="neutral",
        description="A score has 'positive' valence if 'more is better',"
        " 'negative' valence if 'less is better', and 'neutral' valence if"
        " 'better' is not meaningful for this score.",
    )

    priority: Literal["primary", "secondary"] = pydantic.Field(
        default="primary",
        description="The 'primary' score will be displayed in any UI widgets"
        " that expect a single score. There must be exactly 1 primary score.",
    )

    minimum: Optional[float] = pydantic.Field(
        default=None, description="The minimum possible value, if known."
    )

    maximum: Optional[float] = pydantic.Field(
        default=None, description="The maximum possible value, if known."
    )

    format: str = pydantic.Field(
        default="{quantity:.1f}",
        # Must use the 'quantity' key in the format string:
        # (Maybe string not ending in '}')(something like '{quantity:f}')(maybe another string)
        pattern=r"^(.*[^{])?[{]quantity(:[^}]*)?[}]([^}].*)?$",
        description="A Python 'format' string describing how to render the score"
        " as a string. You *must* use the keyword 'quantity' in the format"
        " string, and you may use 'unit' as well (e.g., '{quantity:.2f} {unit}')."
        " It is *strongly recommended* that you limit the output precision"
        " appropriately; use ':.0f' for integer-valued scores.",
    )

    unit: Optional[str] = pydantic.Field(
        default=None,
        description="The unit of measure, if applicable (e.g., 'meters', 'kJ/g')."
        " Use standard SI abbreviations where possible for better indexing.",
    )

    def quantity_string(self, quantity: float) -> str:
        """Formats the given quantity as a string, according to the formatting
        information stored in this ScoreSpec."""
        return self.format_quantity(self.format, quantity, unit=self.unit)

    @pydantic.model_validator(mode="after")
    def _validate_minimum_maximum(cls, values):
        minimum = values.minimum
        maximum = values.maximum
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(f"minimum {minimum} is greater than maximum {maximum}")
        return values

    @pydantic.field_validator("format")
    def _validate_format(cls, v):
        x = cls.format_quantity(v, 3.14, unit="kg")
        y = cls.format_quantity(v, -2.03, unit="kg")
        if x == y:
            # Formatted results for different quantities should be different
            raise ValueError("format string does not mention 'quantity'")

        return v

    @classmethod
    def format_quantity(
        cls, format: str, quantity: float, *, unit: Optional[str] = None
    ) -> str:
        return format.format(quantity=quantity, unit=unit)


class MethodBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="Descriptive name of the Method.")

    scope: MethodScope = pydantic.Field(
        description="The scope of the Method. The Method produces outputs that"
        " are specific to one entity of the type specified in the .scope field."
    )

    description: Optional[str] = pydantic.Field(
        default=None, description="Long-form description, interpreted as Markdown."
    )

    implementation: MethodImplementation = pydantic.Field(
        description="How the Method is implemented."
    )

    parameters: list[MethodParameter] = pydantic.Field(
        default_factory=list,
        description="Configuration parameters accepted by the Method. Values are available at ctx.args(keyword)",
    )

    inputs: list[MethodInput] = pydantic.Field(
        default_factory=list,
        description="Input data entities consumed by the Method. Available at ctx.inputs(keyword)",
    )

    output: MethodOutput = pydantic.Field(
        description="Specification of the Method output."
    )

    scores: list[ScoreSpec] = pydantic.Field(
        default_factory=list,
        description="Specifications of the Scores that this Method produces.",
    )

    modules: list[str] = pydantic.Field(
        default_factory=list,
        description="Modules to load into the analysis environment",
    )

    analysisImage: Optional[ContainerImageSource] = pydantic.Field(
        default=None,
        description="Optional container image to use for running analysis methods."
        " If specified, analysis will run in this custom container instead of"
        " the default analysis environment.",
    )

    @pydantic.field_validator("scores")
    def _scores_validator(cls, scores: list[ScoreSpec]):
        if len(scores) > 0:
            primary_count = sum(score.priority == "primary" for score in scores)
            if primary_count != 1:
                raise ValueError(
                    "scores: Must have exactly one score with .priority == 'primary'"
                )
        return scores


class MethodMetadata(Metadata):
    concerns: list[Concern] = pydantic.Field(
        default_factory=list, description="The Concerns applicable to this Method."
    )


class ModelMetadata(Metadata):
    pass


class Method(DyffEntity, MethodBase):
    kind: Literal["Method"] = Entities.Method.value

    def dependencies(self) -> list[str]:
        return self.modules

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class EntityIDMarker:
    """Marker class to indicate that a field contains an entity ID that supports
    family@tag resolution."""


# Type alias for entity ID fields that support family@tag resolution
EntityIDField: TypeAlias = Annotated[str, EntityIDMarker]


class AnalysisInput(DyffSchemaBaseModel):
    keyword: str = pydantic.Field(
        description="The 'keyword' specified for this input in the MethodSpec."
    )
    entity: EntityIDField = pydantic.Field(
        description="The ID of the entity whose data should be made available as 'keyword'."
    )


class AnalysisArgument(DyffSchemaBaseModel):
    keyword: str = pydantic.Field(
        description="The 'keyword' of the corresponding ModelParameter."
    )
    value: str = pydantic.Field(
        description="The value of of the argument."
        " Always a string; implementations are responsible for parsing."
    )


class ForeignMethod(DyffModelWithID, MethodBase):
    pass


class AnalysisScope(DyffSchemaBaseModel):
    """The specific entities to which the analysis applies.

    When applying an InferenceService-scoped Method, at least
    ``.inferenceService`` must be set.

    When applying an Evaluation-scoped Method, at least ``.evaluation``,
    ``.inferenceService``, and ``.dataset`` must be set.
    """

    dataset: Optional[str] = pydantic.Field(
        default=None, description="The Dataset to which the analysis applies."
    )
    inferenceService: Optional[str] = pydantic.Field(
        default=None, description="The InferenceService to which the analysis applies."
    )
    evaluation: Optional[str] = pydantic.Field(
        default=None, description="The Evaluation to which the analysis applies."
    )
    model: Optional[str] = pydantic.Field(
        default=None, description="The Model to which the analysis applies."
    )


class AnalysisBase(DyffSchemaBaseModel):
    scope: AnalysisScope = pydantic.Field(
        default_factory=AnalysisScope,
        description="The specific entities to which the analysis results apply."
        " At a minimum, the field corresponding to method.scope must be set.",
    )

    arguments: list[AnalysisArgument] = pydantic.Field(
        default_factory=list,
        description="Arguments to pass to the Method implementation.",
    )

    inputs: list[AnalysisInput] = pydantic.Field(
        default_factory=list, description="Mapping of keywords to data entities."
    )


class AnalysisData(DyffSchemaBaseModel):
    """Arbitrary additional data for the Analysis, specified as a key-value pair where
    the value is the data encoded in base64."""

    key: str = pydantic.Field(
        description="Key identifying the data. For data about a Dyff entity,"
        " this should be the entity's ID."
    )

    value: str = pydantic.Field(
        # Canonical base64 encoding
        # https://stackoverflow.com/a/64467300/3709935
        pattern=r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/][AQgw]==|[A-Za-z0-9+/]{2}[AEIMQUYcgkosw048]=)?$",
        description="Arbitrary data encoded in base64.",
    )


class Analysis(AnalysisBase):
    method: ForeignMethod = pydantic.Field(
        description="The analysis Method to run.",
    )

    data: list[AnalysisData] = pydantic.Field(
        default_factory=list, description="Additional data to supply to the analysis."
    )


class Measurement(DyffEntity, MeasurementSpec, Analysis):
    kind: Literal["Measurement"] = Entities.Measurement.value

    def dependencies(self) -> list[str]:
        return [self.method.id] + [x.entity for x in self.inputs]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class SafetyCase(DyffEntity, SafetyCaseSpec, Analysis):
    kind: Literal["SafetyCase"] = Entities.SafetyCase.value

    def dependencies(self) -> list[str]:
        return [self.method.id] + [x.entity for x in self.inputs]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ScoreMetadataRefs(AnalysisScope):
    """References to other Dyff entities related to a Score."""

    method: str = pydantic.Field(description="The Method that generates the score.")


class ScoreMetadata(DyffSchemaBaseModel):
    """Metadata about a Score entity."""

    refs: ScoreMetadataRefs = pydantic.Field(
        description="References to other related Dyff entities."
    )


class ScoreData(ScoreSpec):
    """ScoreData is an "instance" of a ScoreSpec containing the concrete measured value
    for the score."""

    metadata: ScoreMetadata = pydantic.Field(
        description="Metadata about the score; used for indexing.",
    )

    analysis: str = pydantic.Field(
        description="The Analysis that generated the current score instance."
    )

    quantity: float = pydantic.Field(
        description="The numeric quantity associated with the score."
    )

    quantityString: str = pydantic.Field(
        description="The formatted string representation of .quantity,"
        " after processing with the .format specification."
    )

    text: str = pydantic.Field(
        description="A short text description of what the quantity means.",
        max_length=summary_maxlen(),
    )


class Score(ScoreData):
    """A Score is a numeric quantity describing an aspect of system performance.

    Conceptually, a Score is an "instance" of a ScoreSpec.
    """

    kind: Literal["Score"] = Entities.Score.value

    id: str = pydantic.Field(description="Unique identifier of the entity")


# ---------------------------------------------------------------------------
# Status enumerations


class _JobStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to all "job" entities
    (entities that involve computation tasks)."""

    complete: str = "Complete"
    failed: str = "Failed"


JobStatus = _JobStatus()


class _ResourceStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to all "resource"
    entities."""

    ready: str = "Ready"
    error: str = "Error"


ResourceStatus = _ResourceStatus()


class _EntityStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to most entity types."""

    created: str = "Created"
    schedulable: str = "Schedulable"
    admitted: str = "Admitted"
    terminated: str = "Terminated"
    deleted: str = "Deleted"
    ready: str = ResourceStatus.ready
    complete: str = JobStatus.complete
    error: str = ResourceStatus.error
    failed: str = JobStatus.failed


EntityStatus = _EntityStatus()


class _EntityStatusReason(NamedTuple):
    """The set of basic ``reason`` values that are applicable to most entity types."""

    quota_limit: str = "QuotaLimit"
    unsatisfied_dependency: str = "UnsatisfiedDependency"
    failed_dependency: str = "FailedDependency"
    terminate_command: str = "TerminateCommand"
    delete_command: str = "DeleteCommand"
    expired: str = "Expired"
    interrupted: str = "Interrupted"


EntityStatusReason = _EntityStatusReason()


class _AuditStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Audit`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


AuditStatus = _AuditStatus()


class _DataSources(NamedTuple):
    huggingface: str = "huggingface"
    upload: str = "upload"
    zenodo: str = "zenodo"


DataSources = _DataSources()


class _DataSourceStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``DataSource`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


DataSourceStatus = _DataSourceStatus()


class _DataSourceStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``DataSource`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    fetch_failed: str = "FetchFailed"
    upload_failed: str = "UploadFailed"


DataSourceStatusReason = _DataSourceStatusReason()


class _DatasetStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Dataset`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


DatasetStatus = _DatasetStatus()


class _DatasetStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Dataset`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    data_source_missing: str = "DataSourceMissing"
    ingest_failed: str = "IngestFailed"
    waiting_for_data_source: str = "WaitingForDataSource"


DatasetStatusReason = _DatasetStatusReason()


class _EvaluationStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Evaluation`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


EvaluationStatus = _EvaluationStatus()


class _EvaluationStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Evaluation`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    incomplete: str = "Incomplete"
    unverified: str = "Unverified"
    restarted: str = "Restarted"


EvaluationStatusReason = _EvaluationStatusReason()


class _ModelStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Model`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


ModelStatus = _ModelStatus()


class _ModelStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Model`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    fetch_failed: str = "FetchFailed"


ModelStatusReason = _ModelStatusReason()


class _InferenceServiceStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``InferenceService``
    entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


InferenceServiceStatus = _InferenceServiceStatus()


class _InferenceServiceStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``InferenceService``
    entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    build_failed: str = "BuildFailed"
    no_such_model: str = "NoSuchModel"
    waiting_for_model: str = "WaitingForModel"


InferenceServiceStatusReason = _InferenceServiceStatusReason()


class _ReportStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Report`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


ReportStatus = _ReportStatus()


class _ReportStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Report`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    no_such_evaluation: str = "NoSuchEvaluation"
    waiting_for_evaluation: str = "WaitingForEvaluation"


ReportStatusReason = _ReportStatusReason()


def is_status_terminal(status: str) -> bool:
    return status in [
        EntityStatus.complete,
        EntityStatus.error,
        EntityStatus.failed,
        EntityStatus.ready,
        EntityStatus.terminated,
        EntityStatus.deleted,
    ]


def is_status_failure(status: str) -> bool:
    return status in [EntityStatus.error, EntityStatus.failed]


def is_status_success(status: str) -> bool:
    return status in [EntityStatus.complete, EntityStatus.ready]


_ENTITY_CLASS = {
    Entities.Analysis: Analysis,
    Entities.Audit: Audit,
    Entities.AuditProcedure: AuditProcedure,
    Entities.Dataset: Dataset,
    Entities.DataSource: DataSource,
    Entities.Evaluation: Evaluation,
    Entities.InferenceService: InferenceService,
    Entities.InferenceSession: InferenceSession,
    Entities.Measurement: Measurement,
    Entities.Method: Method,
    Entities.Model: Model,
    Entities.Module: Module,
    Entities.Report: Report,
    Entities.SafetyCase: SafetyCase,
}


def entity_class(kind: Entities):
    return _ENTITY_CLASS[kind]


_DyffEntityTypeRevisable = Union[
    Audit,
    AuditProcedure,
    DataSource,
    Dataset,
    Evaluation,
    Family,
    Hazard,
    InferenceService,
    InferenceSession,
    Measurement,
    Method,
    Model,
    Module,
    Report,
    SafetyCase,
    UseCase,
]


class RevisionData(DyffSchemaBaseModel):
    format: Literal["Snapshot", "JsonMergePatch"]
    snapshot: Optional[_DyffEntityTypeRevisable] = pydantic.Field(
        default=None, description="A full snapshot of the entity."
    )
    jsonMergePatch: Optional[str] = pydantic.Field(
        default=None,
        description="A JsonMergePatch, serialized as a string, that will"
        " transform the *current* revision into the *previous* revision.",
    )


# Note: This class is defined here because OpenAPI generation doesn't work
# with the Python < 3.10 "ForwardDeclaration" syntax. You get an error like:
#
# Traceback (most recent call last):
#   File "/home/jessehostetler/dsri/code/dyff/dyff-api/./scripts/generate-openapi-definitions.py", line 15, in <module>
#     get_openapi(
#   File "/home/jessehostetler/dsri/code/dyff/venv/lib/python3.9/site-packages/fastapi/openapi/utils.py", line 422, in get_openapi
#     definitions = get_model_definitions(
#   File "/home/jessehostetler/dsri/code/dyff/venv/lib/python3.9/site-packages/fastapi/utils.py", line 60, in get_model_definitions
#     m_schema, m_definitions, m_nested_models = model_process_schema(
#   File "pydantic/schema.py", line 581, in pydantic.schema.model_process_schema
#   File "pydantic/schema.py", line 622, in pydantic.schema.model_type_schema
#   File "pydantic/schema.py", line 255, in pydantic.schema.field_schema
#   File "pydantic/schema.py", line 527, in pydantic.schema.field_type_schema
#   File "pydantic/schema.py", line 926, in pydantic.schema.field_singleton_schema
#   File "/home/jessehostetler/.asdf/installs/python/3.9.18/lib/python3.9/abc.py", line 123, in __subclasscheck__
#     return _abc_subclasscheck(cls, subclass)
# TypeError: issubclass() arg 1 must be a class
class Revision(DyffEntity, RevisionMetadata):
    kind: Literal["Revision"] = "Revision"

    revisionOf: str = pydantic.Field(
        description="The ID of the entity that this is a revision of"
    )

    data: RevisionData = pydantic.Field(
        description="The associated entity revision data",
    )

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


DyffEntityType = Union[_DyffEntityTypeRevisable, History, Revision]


__all__ = [
    "SYSTEM_ATTRIBUTES",
    "Accelerator",
    "AcceleratorGPU",
    "AccessGrant",
    "Account",
    "Analysis",
    "AnalysisArgument",
    "AnalysisBase",
    "AnalysisData",
    "AnalysisInput",
    "AnalysisOutputQueryFields",
    "AnalysisScope",
    "Annotation",
    "APIFunctions",
    "APIKey",
    "ArchiveFormat",
    "Artifact",
    "ArtifactURL",
    "Audit",
    "AuditProcedure",
    "AuditRequirement",
    "Concern",
    "ConcernBase",
    "ContainerImageSource",
    "DataSchema",
    "Dataset",
    "DatasetBase",
    "DatasetFilter",
    "DataSource",
    "DataSources",
    "DataView",
    "Digest",
    "Documentation",
    "DocumentationBase",
    "Documented",
    "DyffDataSchema",
    "DyffEntity",
    "DyffEntityType",
    "DyffModelWithID",
    "DyffSchemaBaseModel",
    "Entities",
    "EntityID",
    "EntityIdentifier",
    "EntityIDField",
    "EntityIDMarker",
    "EntityKindLiteral",
    "Evaluation",
    "EvaluationBase",
    "EvaluationClientConfiguration",
    "ExtractorStep",
    "Family",
    "FamilyBase",
    "FamilyMember",
    "FamilyMemberBase",
    "FamilyMemberKind",
    "FamilyMembers",
    "ForeignInferenceService",
    "ForeignMethod",
    "ForeignModel",
    "ForeignRevision",
    "Frameworks",
    "Hazard",
    "History",
    "Identity",
    "InferenceInterface",
    "InferenceService",
    "InferenceServiceBase",
    "InferenceServiceBuilder",
    "InferenceServiceRunner",
    "InferenceServiceRunnerKind",
    "InferenceServiceSources",
    "InferenceServiceSpec",
    "InferenceSession",
    "InferenceSessionAndToken",
    "InferenceSessionBase",
    "InferenceSessionReference",
    "InferenceSessionSpec",
    "Label",
    "LabelKey",
    "LabelKeyType",
    "LabelValue",
    "LabelValueType",
    "Labeled",
    "Measurement",
    "MeasurementLevel",
    "MeasurementSpec",
    "Method",
    "MethodBase",
    "MethodImplementation",
    "MethodImplementationJupyterNotebook",
    "MethodImplementationKind",
    "MethodImplementationPythonFunction",
    "MethodImplementationPythonRubric",
    "MethodInput",
    "MethodInputKind",
    "MethodOutput",
    "MethodOutputKind",
    "MethodParameter",
    "MethodScope",
    "Model",
    "ModelArtifact",
    "ModelArtifactHuggingFaceCache",
    "ModelArtifactKind",
    "ModelBase",
    "ModelStorageMedium",
    "ModelResources",
    "ModelSource",
    "ModelSourceGitLFS",
    "ModelSourceHuggingFaceHub",
    "ModelSourceKinds",
    "ModelSourceOpenLLM",
    "ModelSpec",
    "ModelStorage",
    "Module",
    "ModuleBase",
    "QueryableDyffEntity",
    "Report",
    "ReportBase",
    "Resources",
    "Revision",
    "RevisionData",
    "RevisionMetadata",
    "Role",
    "SafetyCase",
    "SafetyCaseSpec",
    "SchemaAdapter",
    "Score",
    "ScoreData",
    "ScoreSpec",
    "ScoreMetadata",
    "ScoreMetadataRefs",
    "Status",
    "StorageSignedURL",
    "TagName",
    "TagNameType",
    "TaskSchema",
    "UseCase",
    "entity_class",
    "JobStatus",
    "EntityStatus",
    "EntityStatusReason",
    "AuditStatus",
    "DataSourceStatus",
    "DatasetStatus",
    "DatasetStatusReason",
    "EvaluationStatus",
    "EvaluationStatusReason",
    "InferenceServiceStatus",
    "InferenceServiceStatusReason",
    "ModelStatus",
    "ModelStatusReason",
    "ReportStatus",
    "ReportStatusReason",
    "identifier_regex",
    "identifier_maxlen",
    "is_status_terminal",
    "is_status_failure",
    "is_status_success",
    "summary_maxlen",
    "title_maxlen",
]
