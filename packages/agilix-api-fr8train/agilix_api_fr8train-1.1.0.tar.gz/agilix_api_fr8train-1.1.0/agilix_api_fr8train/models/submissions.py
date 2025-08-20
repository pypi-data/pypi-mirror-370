class PutTeacherResponsesDefinition:
    enrollment_id: int
    item_id: any
    letter: str
    type: str
    submitted_date: str
    mask: int
    status: int
    points_assigned: any
    points_possible: float
    zero_unscored: bool

    def __init__(
        self,
        enrollment_id: int,
        item_id: any,
        letter: str = None,
        type: str = None,
        submitted_date: str = None,
        mask: int = None,
        status: int = None,
        points_assigned: any = None,
        points_possible: float = None,
        zero_unscored: bool = False,
    ):
        self.enrollment_id = enrollment_id
        self.item_id = item_id
        self.letter = letter
        self.type = type
        self.submitted_date = submitted_date
        self.mask = mask
        self.status = status
        self.points_assigned = points_assigned
        self.points_possible = points_possible
        self.zero_unscored = zero_unscored

    def __iter__(self):
        yield "enrollmentid", self.enrollment_id
        yield "itemid", self.item_id
        yield "type", self.type
        if self.letter:
            yield "letter", self.letter
        if self.type:
            yield "type", self.type
        if self.submitted_date:
            yield "submitteddate", self.submitted_date
        if self.mask:
            yield "mask", self.mask
        if self.status:
            yield "status", self.status
        if self.points_assigned:
            yield "pointsassigned", self.points_assigned
        if self.points_possible:
            yield "pointspossible", self.points_possible
        if self.zero_unscored:
            yield "zerounscored", self.zero_unscored
