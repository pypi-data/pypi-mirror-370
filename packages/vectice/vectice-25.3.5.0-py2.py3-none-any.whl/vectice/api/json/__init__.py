from __future__ import annotations

from vectice.api.json.artifact_version import ArtifactVersion, VersionStrategy
from vectice.api.json.code import CodeInput, CodeOutput
from vectice.api.json.dataset_register import DatasetRegisterOutput
from vectice.api.json.entity_file import EntityFileOutput
from vectice.api.json.files_metadata import FileMetadata, FileMetadataType
from vectice.api.json.iteration import (
    IterationOutput,
    IterationStatus,
    IterationStepArtifact,
    IterationStepArtifactInput,
    IterationStepArtifactType,
    IterationUpdateInput,
)
from vectice.api.json.last_assets import ActivityTargetType, UserActivity
from vectice.api.json.metric import MetricInput, MetricOutput
from vectice.api.json.model_register import ModelRegisterInput, ModelRegisterOutput
from vectice.api.json.model_version import ModelVersionInput, ModelVersionOutput, ModelVersionStatus
from vectice.api.json.organization_config import OrgConfigOutput
from vectice.api.json.page import Page
from vectice.api.json.paged_response import PagedResponse
from vectice.api.json.phase import PhaseOutput
from vectice.api.json.project import ProjectOutput
from vectice.api.json.project_template import ProjectTemplateOutput
from vectice.api.json.property import PropertyInput, PropertyOutput
from vectice.api.json.public_config import ArtifactName, PublicConfigOutput
from vectice.api.json.requirement import RequirementOutput
from vectice.api.json.section import SectionOutput
from vectice.api.json.user_and_workspace import UserAndDefaultWorkspaceOutput
from vectice.api.json.workspace import WorkspaceInput, WorkspaceOutput

__all__ = [
    "ArtifactVersion",
    "VersionStrategy",
    "EntityFileOutput",
    "CodeInput",
    "CodeOutput",
    "UserAndDefaultWorkspaceOutput",
    "MetricInput",
    "MetricOutput",
    "ModelRegisterInput",
    "ModelRegisterOutput",
    "ModelVersionInput",
    "ModelVersionOutput",
    "ModelVersionStatus",
    "PagedResponse",
    "ProjectOutput",
    "PropertyInput",
    "PropertyOutput",
    "FileMetadata",
    "FileMetadataType",
    "WorkspaceOutput",
    "WorkspaceInput",
    "Page",
    "PhaseOutput",
    "RequirementOutput",
    "SectionOutput",
    "IterationUpdateInput",
    "IterationOutput",
    "IterationStatus",
    "IterationStepArtifactInput",
    "IterationStepArtifact",
    "IterationStepArtifactType",
    "DatasetRegisterOutput",
    "ModelRegisterOutput",
    "ActivityTargetType",
    "UserActivity",
    "ArtifactName",
    "PublicConfigOutput",
    "OrgConfigOutput",
    "ProjectTemplateOutput",
]
