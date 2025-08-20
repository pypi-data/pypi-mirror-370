from agilix_api_fr8train.models.generics import ListDefinition
from enum import Enum


class CourseCopyType(Enum):
    STATIC = "StaticCopy"
    DERIVATIVE_CHILD = "DerivativeChildCopy"
    DERIVATIVE_SIBLING = "DerivativeSiblingCopy"


class UpdateCourseDefinition:
    course_id: str
    domain_id: str
    title: str
    reference: str

    def __init__(self, course_id: str, domain_id: str, title: str, reference: str):
        self.course_id = course_id
        self.domain_id = domain_id
        self.title = title
        self.reference = reference

    def __iter__(self):
        yield "courseid", self.course_id
        yield "domainid", self.domain_id
        yield "title", self.title
        yield "reference", self.reference


class CopyCourseDefinition:
    course_id: int
    domain_id: int
    action: CourseCopyType
    reference: str
    status: int
    title: str
    type: str
    days: int

    def __init__(
        self,
        course_id: int,
        domain_id: int,
        title: str,
        action: CourseCopyType = CourseCopyType.STATIC,
        reference: str = "",
        status: int = 0,
        type: str = "Continuous",
        days: int = 365,
    ):
        self.course_id = course_id
        self.domain_id = domain_id
        self.action = action
        self.reference = reference
        self.status = status
        self.title = title
        self.type = type
        self.days = days

    def __iter__(self):
        yield "courseid", self.course_id
        yield "domainid", self.domain_id
        yield "action", self.action.value
        yield "reference", self.reference
        yield "status", self.status
        yield "title", self.title
        yield "type", self.type
        yield "days", self.days


class ListCourseDefinition(ListDefinition):
    pass
