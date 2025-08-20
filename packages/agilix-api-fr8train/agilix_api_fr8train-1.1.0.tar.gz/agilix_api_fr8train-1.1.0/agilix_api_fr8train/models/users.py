from agilix_api_fr8train.models.generics import ListDefinition


class ListUserDefinition(ListDefinition):
    pass


class CreateUserDefinition:
    username: str
    password: str
    firstname: str
    lastname: str
    email: str
    domain_id: int
    reference: str
    role_id: int

    def __init__(
        self,
        username: str,
        password: str,
        firstname: str,
        lastname: str,
        email: str,
        domain_id: int,
        role_id: int,
        reference: str = "",
    ):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.domain_id = domain_id
        self.reference = reference
        self.role_id = role_id

    def __iter__(self):
        yield "username", self.username
        yield "password", self.password
        yield "firstname", self.firstname
        yield "lastname", self.lastname
        yield "email", self.email
        yield "domainid", self.domain_id
        yield "reference", self.reference
        yield "roleid", self.role_id


class UpdateUserDefinition:
    user_id: int
    domain_id: int
    username: str
    firstname: str
    lastname: str
    email: str
    reference: str

    def __init__(
        self,
        user_id: int,
        domain_id: int,
        username: str,
        firstname: str,
        lastname: str,
        email: str,
        reference: str = "",
    ):
        self.user_id = user_id
        self.domain_id = domain_id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.reference = reference

    def __iter__(self):
        yield "userid", self.user_id
        yield "domainid", self.domain_id
        yield "username", self.username
        yield "firstname", self.firstname
        yield "lastname", self.lastname
        yield "email", self.email
        yield "reference", self.reference
