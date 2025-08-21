# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0
"""The command schemas describe the API for the command model.

These are used internally by the platform and users typically won't encounter them.
"""

from __future__ import annotations

from typing import Literal, Optional, Union

import pydantic
from pydantic import StringConstraints
from typing_extensions import Annotated

from .base import DyffSchemaBaseModel, JsonMergePatchSemantics
from .platform import (
    DyffEntityType,
    EntityIdentifier,
    FamilyMember,
    FamilyMembers,
    LabelKeyType,
    LabelValueType,
    SchemaVersion,
    Status,
    TagNameType,
    summary_maxlen,
    title_maxlen,
)


class FamilyIdentifier(EntityIdentifier):
    """Identifies a single Family entity."""

    kind: Literal["Family"] = "Family"


class Command(SchemaVersion, DyffSchemaBaseModel):
    """Base class for Command messages.

    Commands define the API of the "command model" in our CQRS architecture.
    """

    command: Literal[
        "CreateEntity",
        "EditEntityDocumentation",
        "EditEntityLabels",
        "EditFamilyMembers",
        "ForgetEntity",
        "RestoreEntity",
        "UpdateEntityStatus",
    ]


# ----------------------------------------------------------------------------


class CreateEntity(Command):
    """Create a new entity."""

    command: Literal["CreateEntity"] = "CreateEntity"

    data: DyffEntityType = pydantic.Field(
        description="The full spec of the entity to create."
    )


# ----------------------------------------------------------------------------


class EditEntityDocumentationPatch(JsonMergePatchSemantics):
    """Same properties as DocumentationBase, but assigning None to a field is
    interpreted as a command to delete that field.

    Fields that are assigned explicitly remain unchanged.
    """

    title: Optional[Annotated[str, StringConstraints(max_length=title_maxlen())]] = (  # type: ignore
        pydantic.Field(
            default=None,
            description='A short plain string suitable as a title or "headline".'
            " Providing an explicit None value deletes the current value.",
        )
    )

    summary: Optional[Annotated[str, StringConstraints(max_length=summary_maxlen())]] = (  # type: ignore
        pydantic.Field(
            default=None,
            description="A brief summary, suitable for display in"
            " small UI elements. Providing an explicit None value deletes the"
            " current value.",
        )
    )

    fullPage: Optional[str] = pydantic.Field(
        default=None,
        description="Long-form documentation. Interpreted as"
        " Markdown. There are no length constraints, but be reasonable."
        " Providing an explicit None value deletes the current value.",
    )


class EditEntityDocumentationAttributes(DyffSchemaBaseModel):
    """Attributes for the EditEntityDocumentation command."""

    documentation: EditEntityDocumentationPatch = pydantic.Field(
        description="Edits to make to the documentation."
    )


class EditEntityDocumentationData(EntityIdentifier):
    """Payload data for the EditEntityDocumentation command."""

    attributes: EditEntityDocumentationAttributes = pydantic.Field(
        description="The command attributes"
    )


class EditEntityDocumentation(Command):
    """Edit the documentation associated with an entity.

    Setting a documentation field to null/None deletes the corresponding value. To
    preserve the existing value, leave the field *unset*.
    """

    command: Literal["EditEntityDocumentation"] = "EditEntityDocumentation"

    data: EditEntityDocumentationData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class EditEntityLabelsAttributes(JsonMergePatchSemantics):
    """Attributes for the EditEntityLabels command."""

    labels: dict[LabelKeyType, Optional[LabelValueType]] = pydantic.Field(
        default_factory=dict,
        description="A set of key-value labels for the resource."
        " Existing label keys that are not provided in the edit remain unchanged."
        " Providing an explicit None value deletes the corresponding key.",
    )


class EditEntityLabelsData(EntityIdentifier):
    """Payload data for the EditEntityLabels command."""

    attributes: EditEntityLabelsAttributes = pydantic.Field(
        description="The command attributes"
    )


class EditEntityLabels(Command):
    """Edit the labels associated with an entity.

    Setting a label field to null/None deletes the corresponding value. To preserve the
    existing value, leave the field *unset*.
    """

    command: Literal["EditEntityLabels"] = "EditEntityLabels"

    data: EditEntityLabelsData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class EditFamilyMembersAttributes(JsonMergePatchSemantics):
    """Attributes for the EditFamilyMembers command."""

    members: dict[TagNameType, Optional[FamilyMember]] = pydantic.Field(
        description="Mapping of names to IDs of member resources.",
    )


class EditFamilyMembersData(FamilyMembers, FamilyIdentifier):
    """Payload data for the EditFamilyMembers command."""

    attributes: EditFamilyMembersAttributes = pydantic.Field(
        description="The command attributes"
    )


class EditFamilyMembers(Command):
    """Edit the labels associated with an entity.

    Setting a tag value to null/None deletes the corresponding value. To preserve the
    existing value, leave the field *unset*.
    """

    command: Literal["EditFamilyMembers"] = "EditFamilyMembers"

    data: EditFamilyMembersData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class ForgetEntity(Command):
    """Forget (permanently delete) an entity."""

    command: Literal["ForgetEntity"] = "ForgetEntity"

    data: EntityIdentifier = pydantic.Field(description="The entity to forget.")


# ----------------------------------------------------------------------------


class RestoreEntityAttributes(DyffSchemaBaseModel):
    entity: DyffEntityType = pydantic.Field(
        description="The full spec of the entity to restore."
    )

    ifRevisionMatch: Optional[str] = pydantic.Field(
        default=None,
        description="Do not change the entity if its revision does not match"
        " the given revision.",
    )

    ifRevisionUndefined: Optional[bool] = pydantic.Field(
        default=None,
        description="Allow changing entities that have no revision."
        " By default, entities with no revision will be changed if and only if"
        " no other matching criteria are specified."
        " This should be the case only for legacy data.",
    )


class RestoreEntityData(EntityIdentifier):
    attributes: RestoreEntityAttributes = pydantic.Field(
        description="The command attributes"
    )


class RestoreEntity(Command):
    """Restore an entity to a given state."""

    command: Literal["RestoreEntity"] = "RestoreEntity"

    data: RestoreEntityData = pydantic.Field(description="The command data.")


# ----------------------------------------------------------------------------


class UpdateEntityStatusAttributes(JsonMergePatchSemantics):
    """Attributes for the UpdateEntityStatus command."""

    status: str = pydantic.Field(description=Status.model_fields["status"].description)

    reason: Optional[str] = pydantic.Field(
        description=Status.model_fields["reason"].description
    )


class UpdateEntityStatusData(EntityIdentifier):
    """Payload data for the UpdateEntityStatus command."""

    attributes: UpdateEntityStatusAttributes = pydantic.Field(
        description="The command attributes"
    )


class UpdateEntityStatus(Command):
    """Update the status fields of an entity."""

    command: Literal["UpdateEntityStatus"] = "UpdateEntityStatus"

    data: UpdateEntityStatusData = pydantic.Field(description="The status update data.")


# ----------------------------------------------------------------------------


DyffCommandType = Union[
    CreateEntity,
    EditEntityDocumentation,
    EditEntityLabels,
    EditFamilyMembers,
    ForgetEntity,
    RestoreEntity,
    UpdateEntityStatus,
]


__all__ = [
    "Command",
    "CreateEntity",
    "DyffCommandType",
    "EditEntityDocumentation",
    "EditEntityDocumentationAttributes",
    "EditEntityDocumentationData",
    "EditEntityDocumentationPatch",
    "EditEntityLabels",
    "EditEntityLabelsAttributes",
    "EditEntityLabelsData",
    "EditFamilyMembers",
    "EditFamilyMembersAttributes",
    "EditFamilyMembersData",
    "EntityIdentifier",
    "FamilyIdentifier",
    "ForgetEntity",
    "RestoreEntity",
    "RestoreEntityAttributes",
    "RestoreEntityData",
    "UpdateEntityStatus",
    "UpdateEntityStatusAttributes",
    "UpdateEntityStatusData",
]
