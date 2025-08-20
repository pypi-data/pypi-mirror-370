class ListUserEnrollmentsDefinition:
    user_id: int
    all_status: bool
    entity_id: int
    select: list

    def __init__(
        self,
        user_id: int,
        entity_id: int = None,
        all_status: bool = False,
        select: list = [],
    ):
        self.user_id = user_id
        self.all_status = all_status
        self.entity_id = entity_id
        self.select = select

    def __iter__(self):
        yield "userid", self.user_id
        if self.entity_id:
            yield "entityid", self.entity_id
        yield "allstatus", self.all_status
        if self.select:
            yield "select", ",".join(self.select)


class ListEntityEnrollmentsDefinition:
    entity_id: int
    all_status: bool
    select: list

    def __init__(
        self,
        entity_id: int,
        all_status: bool = False,
        select: list = [],
    ):
        self.entity_id = entity_id
        self.all_status = all_status
        self.select = select

    def __iter__(self):
        yield "entityid", self.entity_id
        yield "allstatus", self.all_status
        if self.select:
            yield "select", ",".join(self.select)


class UpdateEnrollmentsDefinition:
    enrollment_id: int
    status: int

    def __init__(
        self,
        enrollment_id: int,
        status: int = 1,
    ):
        self.enrollment_id = enrollment_id
        self.status = status

    def __iter__(self):
        yield "enrollmentid", self.enrollment_id
        yield "status", self.status
