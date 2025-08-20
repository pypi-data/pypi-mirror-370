from agilix_api_fr8train.models.generics import ListDefinition


class CreateDomainDefinition:
    name: str
    userspace: str
    parent_id: int
    reference: str

    def __init__(self, name: str, userspace: str, parent_id: int, reference: str = ""):
        self.name = name
        self.userspace = userspace
        self.parent_id = parent_id
        self.reference = reference

    def __iter__(self):
        yield "name", self.name
        yield "userspace", self.userspace
        yield "parentid", self.parent_id
        yield "reference", self.reference


class ListDomainDefinition(ListDefinition):
    pass


class UpdateDomainDefinition:
    domain_id: int
    name: str
    parent_id: int
    reference: str
    userspace: str

    def __init__(
        self,
        domain_id: int,
        parent_id: int,
        userspace: str,
        name: str = "",
        reference: str = "",
    ):
        self.domain_id = domain_id
        self.name = name
        self.userspace = userspace
        self.parent_id = parent_id
        self.reference = reference

    def __iter__(self):
        yield "domainid", self.domain_id
        yield "name", self.name
        yield "userspace", self.userspace
        yield "parentid", self.parent_id
        yield "reference", self.reference
