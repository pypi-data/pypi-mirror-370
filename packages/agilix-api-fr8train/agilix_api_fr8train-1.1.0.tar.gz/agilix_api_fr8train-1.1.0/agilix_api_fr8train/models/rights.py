class GetActorRightsDefinition:
    actor_id: int
    entity_types: list[str]

    def __init__(self, actor_id: int, entity_types: list[str]):
        self.actor_id = actor_id
        self.entity_types = entity_types

    def __iter__(self):
        yield "actorid", self.actor_id
        yield "entitytypes", "|".join(self.entity_types)


class UpdateRightsDefinition:
    actor_id: int
    entity_id: int
    role_id: int
    flags: int

    def __init__(
        self, actor_id: int, entity_id: int, role_id: int = None, flags: int = 0
    ):
        self.actor_id = actor_id
        self.entity_id = entity_id
        self.role_id = role_id
        self.flags = flags

    def __iter__(self):
        yield "actorid", self.actor_id
        yield "entityid", self.entity_id
        if self.role_id:
            yield "roleid", self.role_id
        else:
            yield "flags", self.flags
