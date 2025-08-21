from datetime import datetime
from marshmallow import fields
from s4.platform.entity.entity import Entity, EntitySchema
from s4.platform.internal.base_schema import BaseSchema
from typing import Optional


class Claim(object):
    def __init__(self, *, iri: str, activity_id: Optional[str] = None, activity_name: Optional[str] = None,
                 process_definition_iri: Optional[str] = None, entities: list[Entity], is_external_task: bool,
                 invalidated_by: Optional[str] = None, external_task_output: Optional[str] = None,
                 external_task_error_output: Optional[str] = None, claimed_at_time: datetime, claimed_by_iri: str):
        self.iri = iri
        self.activity_id = activity_id
        self.activity_name = activity_name
        self.process_definition_iri = process_definition_iri
        self.entities = entities
        self.is_external_task = is_external_task
        self.invalidated_by = invalidated_by
        self.external_task_output = external_task_output
        self.external_task_error_output = external_task_error_output
        self.claimed_at_time = claimed_at_time
        self.claimed_by_iri = claimed_by_iri


class ClaimSchema(BaseSchema):
    def __init__(self, **kwargs):
        super().__init__(Claim, **kwargs)

    iri = fields.Str(load_only=True)
    activity_id = fields.Str(load_only=True, allow_none=True)
    activity_name = fields.Str(load_only=True, allow_none=True)
    process_definition_iri = fields.Str(load_only=True, allow_none=True)
    entities = fields.List(fields.Nested(EntitySchema), load_only=True)
    is_external_task = fields.Bool(load_only=True)
    invalidated_by = fields.Str(load_only=True, allow_none=True)
    external_task_output = fields.Str(load_only=True, allow_none=True)
    external_task_error_output = fields.Str(load_only=True, allow_none=True)
    claimed_at_time = fields.DateTime(load_only=True)
    claimed_by_iri = fields.Str(load_only=True)


class AdHocClaimRequest(object):
    def __init__(self, *, entity_iris: list[str]):
        self.entity_iris = entity_iris


class AdHocClaimRequestSchema(BaseSchema):
    def __init__(self, **kwargs):
        super().__init__(AdHocClaimRequest, **kwargs)
    entity_iris = fields.List(fields.Str)
