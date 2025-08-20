from fnmatch import fnmatch
import re
import agilix_api_fr8train.factories.api as ApiFactory
import agilix_api_fr8train.factories.domain as DomainFactory
import agilix_api_fr8train.factories.user as UserFactory
import agilix_api_fr8train.factories.course as CourseFactory
import agilix_api_fr8train.factories.rights as RightsFactory
import agilix_api_fr8train.factories.authentication as AuthenticationFactory
import agilix_api_fr8train.factories.enrollment as EnrollmentFactory
import agilix_api_fr8train.factories.submission as SubmissionFactory

from agilix_api_fr8train.models.connection import Connection

from agilix_api_fr8train.models.courses import (
    UpdateCourseDefinition,
    CopyCourseDefinition,
    ListCourseDefinition,
)
from agilix_api_fr8train.models.domains import (
    CreateDomainDefinition,
    ListDomainDefinition,
    UpdateDomainDefinition,
)
from agilix_api_fr8train.models.users import (
    ListUserDefinition,
    CreateUserDefinition,
    UpdateUserDefinition,
)
from agilix_api_fr8train.models.rights import (
    GetActorRightsDefinition,
    UpdateRightsDefinition,
)

from agilix_api_fr8train.models.enrollments import (
    ListUserEnrollmentsDefinition,
    ListEntityEnrollmentsDefinition,
    UpdateEnrollmentsDefinition,
)
from agilix_api_fr8train.models.authentication import UpdatePasswordDefinition

from agilix_api_fr8train.models.submissions import PutTeacherResponsesDefinition


class Api:
    _conn: Connection

    def __init__(self):
        self._conn = ApiFactory.build_api_connection()

        # PACKAGED MODULAR SCOPES
        self.courses = self.Courses(self._conn)
        self.domains = self.Domains(self._conn)
        self.users = self.Users(self._conn)
        self.rights = self.Rights(self._conn)
        self.utils = self.Utils(self._conn)
        self.enrollments = self.Enrollments(self._conn)
        self.authentication = self.Authentication(self._conn)
        self.submissions = self.Submissions(self._conn)

    def get_home_domain_id(self) -> int:
        return self._conn.home_domain_id

    class Submissions:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def put_teacher_responses(
            self, teacher_responses: list[PutTeacherResponsesDefinition]
        ) -> list:
            response = self._conn.post(
                "putteacherresponses",
                payload=SubmissionFactory.build_put_teacher_responses_payload(
                    teacher_responses
                ),
            )

            return response.get("response", {}).get("responses", {}).get("response", [])

    class Authentication:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def update_password(self, update_password: UpdatePasswordDefinition) -> dict:
            response = self._conn.post(
                cmd=None,
                payload=AuthenticationFactory.build_update_password_payload(
                    update_password
                ),
            )

            return response.get("response", {})

    class Enrollments:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def list_user_enrollments(
            self, user_enrollments: ListUserEnrollmentsDefinition
        ) -> list:
            response = self._conn.get(
                "listuserenrollments", params=dict(user_enrollments)
            )

            return (
                response.get("response", {})
                .get("enrollments", {})
                .get("enrollment", [])
            )

        def get_enrollment_gradebook(self, enrollment_id: int) -> dict:
            response = self._conn.get(
                "getenrollmentgradebook2", params={"enrollmentid": enrollment_id}
            )

            return response.get("response", {}).get("enrollment", {})

        def update_enrollments(self, update: list[UpdateEnrollmentsDefinition]) -> list:
            response = self._conn.post(
                "updateenrollments",
                payload=EnrollmentFactory.build_update_enrollments_payload(update),
            )

            return response.get("response", {}).get("responses", {}).get("response", [])

        def list_entity_enrollments(
            self, entity_enrollments: ListEntityEnrollmentsDefinition
        ) -> list:
            response = self._conn.get(
                "listentityenrollments", params=dict(entity_enrollments)
            )

            return (
                response.get("response", {})
                .get("enrollments", {})
                .get("enrollment", [])
            )

    class Courses:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def list_courses(self, list_courses: ListCourseDefinition) -> list:
            response = self._conn.get("listcourses", params=dict(list_courses))

            return response.get("response", {}).get("courses", {}).get("course", [])

        def get_course(self, course_id: int, select: list = []) -> dict:
            response = self._conn.get(
                "getcourse2",
                params={
                    "courseid": course_id,
                    "select": select if ",".join(select) else "",
                },
            )

            return response.get("response", {}).get("course", {})

        def copy_courses(self, course_list: list[CopyCourseDefinition]):  # -> list:
            payload = CourseFactory.build_copy_course_payload(course_list)

            response = self._conn.post("copycourses", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def update_courses(self, course_list: list[UpdateCourseDefinition]) -> list:
            payload = {"requests": {"course": course_list}}

            response = self._conn.post("updatecourses", payload=payload)

            course_responses = list(
                map(
                    lambda x: (
                        x.get("code") == "OK"
                        if x.get("code") == "OK"
                        else x.get("message", "Generic Error")
                    ),
                    response.get("response", {})
                    .get("responses", {})
                    .get("response", []),
                )
            )

            return course_responses

        def delete_courses(self, course_id: list):
            payload = {
                "requests": {"course": list(map(lambda x: {"courseid": x}, course_id))}
            }

            response = self._conn.post("deletecourses", payload=payload)

            course_responses = list(
                map(
                    lambda x: (
                        x.get("code") == "OK"
                        if x.get("code") == "OK"
                        else x.get("message", "Generic Error")
                    ),
                    response.get("response", {})
                    .get("responses", {})
                    .get("response", []),
                )
            )

            return course_responses

    class Domains:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def list_domains(self, list_domain: ListDomainDefinition) -> list:
            response = self._conn.get("listdomains", params=dict(list_domain))

            return response.get("response", {}).get("domains", {}).get("domain", [])

        def create_domains(self, domain_list: list[CreateDomainDefinition]) -> list:
            payload = DomainFactory.build_create_domain_payload(domain_list)

            response = self._conn.post("createdomains", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def update_domains(self, domain_list: list[UpdateDomainDefinition]) -> list:
            payload = DomainFactory.build_update_domain_payload(domain_list)

            response = self._conn.post("updatedomains", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def get_domain(self, domain_id: int, select: str = "") -> dict:
            response = self._conn.get(
                "getdomain2", params={"domainid": domain_id, "select": select}
            )

            return response.get("response", {}).get("domain", {})

        def get_domain_settings(self, domain_id: int, path: str) -> dict:
            response = self._conn.get(
                "getdomainsettings", params={"domainid": domain_id, "path": path}
            )

            return response.get("response", {}).get("settings", {})

        def set_domain_settings(self, domain_id: int, path: str, settings: dict):
            response = self._conn.post(
                cmd="getdomainsettings",
                params={"domainid": domain_id, "path": path},
                payload={"settings": settings},
            )

            return response

    class Users:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def list_users(self, list_users: ListUserDefinition) -> list:
            response = self._conn.get("listusers", params=dict(list_users))

            return response.get("response", {}).get("users", {}).get("user", [])

        def create_users(self, user_list: list[CreateUserDefinition]) -> list:
            payload = UserFactory.build_create_user_payload(user_list)

            response = self._conn.post("createusers2", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def update_users(self, user_list: list[UpdateUserDefinition]) -> list:
            payload = UserFactory.build_update_user_payload(user_list)

            response = self._conn.post("updateusers", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def delete_users(self, delete_user_list: list[int]) -> list:
            payload = UserFactory.build_delete_user_payload(delete_user_list)

            response = self._conn.post("deleteusers", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

        def restore_user(self, user_id: int) -> dict:
            response = self._conn.post("restoreuser", params={"userid": user_id})

            return response.get("response", {})

        def get_user(self, user_id: int, select: list = []) -> dict:
            response = self._conn.get(
                "getuser2",
                params={"userid": user_id, "select": ",".join(select)},
            )

            return response.get("response", {}).get("user", {})

    class Rights:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def list_roles(self, domain_id: int) -> list:
            response = self._conn.get("listroles", params={"domainid": domain_id})

            return response.get("response", {}).get("roles", {}).get("role", [])

        def get_actor_rights(self, rights: GetActorRightsDefinition) -> dict:
            response = self._conn.get("getactorrights", params=dict(rights))

            return response.get("response", {}).get("entities", {})

        def get_role(self, role_id: int) -> list:
            response = self._conn.get("getrole", params={"roleid": role_id})

            return response.get("response", {}).get("role", [])

        def update_rights(self, update_list: list[UpdateRightsDefinition]) -> list:
            payload = RightsFactory.build_update_rights_payload(update_list)

            response = self._conn.post("updaterights", payload=payload)

            return response.get("response", {}).get("responses", {}).get("response", [])

    class Utils:
        _conn: Connection

        def __init__(self, connection: Connection):
            self._conn = connection

        def build_domain_tree(self, top: int, domain_list: list) -> dict:
            hung_on_tree = {}
            domain_tree = {
                "domain_id": top,
                "name": "Home Domain",
                "userspace": None,
                "children": {},
            }

            for domain in domain_list:
                parent_id = int(domain.get("parentid"))

                # FIRST ROW
                if parent_id == top:
                    domain_tree["children"][domain.get("id")] = {
                        "domain_id": domain.get("id"),
                        "name": domain.get("name"),
                        "userspace": domain.get("userspace"),
                        "children": {},
                    }
                    hung_on_tree[domain.get("id")] = domain.get("name")
                    continue

            while len(hung_on_tree.items()) < len(domain_list):
                for domain in domain_list:
                    domain_tree["children"], hung_on_tree = (
                        self.__build_domain_tree_recursive(
                            _children=domain_tree["children"],
                            _domain=domain,
                            _hung_on_tree=hung_on_tree,
                            finish_total=len(domain_list),
                        )
                    )

                    if len(hung_on_tree.items()) == len(domain_list):
                        break

            return domain_tree

        def __build_domain_tree_recursive(
            self, _children: dict, _domain: dict, _hung_on_tree: dict, finish_total: int
        ) -> tuple:
            # GO THROUGH ALL THE CHILDREN TO MATCH THE DOMAIN WITH THEM AS THE PARENT
            # WE'RE NEXT LEVEL DOWN, SO "CHILDREN" ARE POSSIBLE PARENTS
            domain_parent_id = _domain.get("parentid")
            if domain_parent_id in _children:
                # IF THE DOMAIN'S PARENTID IS THIS CHILD'S ID ADD AND RETURN
                _children[domain_parent_id]["children"][_domain.get("id")] = {
                    "domain_id": _domain.get("id"),
                    "name": _domain.get("name"),
                    "userspace": _domain.get("userspace"),
                    "children": {},
                }
                _hung_on_tree[_domain.get("id")] = _domain.get("name")

                return _children, _hung_on_tree
            else:
                for id, child in _children.items():
                    # IF THE CHILD HAS CHILDREN NEXT GEN THIS SUCKER
                    if len(child["children"].items()) > 0:
                        _children[id]["children"], _hung_on_tree = (
                            self.__build_domain_tree_recursive(
                                child["children"], _domain, _hung_on_tree, finish_total
                            )
                        )

                        if len(_hung_on_tree.items()) == finish_total:
                            return _children, _hung_on_tree

            return _children, _hung_on_tree

        def __is_match(self, userspace: str) -> bool:
            return fnmatch(userspace, "st*m")

        def __specific_use_cases_course_title(self, course_title: str) -> str:
            if "ACCOM" in course_title:
                return f"{course_title[(course_title.find("ACCOM")+6):]}_ACCOM".strip()

            if "BYU" in course_title:
                return course_title[course_title.find("BYU") :]

            return course_title

        def course_naming_engine(
            self,
            course_title: str,
            target_domain_name: str,
            target_domain_id: int,
            target_domain_userspace: str,
            target_parent_userspace: str,
        ) -> str:
            import us

            # DETERMINE IF PROPERLY FORMATTED COURSE TITLE
            if course_title.lower().startswith("master stellar virtual"):
                actual_course_title = course_title[23:]
                state_abbr = us.states.lookup(target_domain_name)

                if state_abbr:
                    state_abbr = f"{state_abbr.abbr} "
                else:
                    state_abbr = ""

                if target_domain_id == 213069655:  # INDIANA
                    actual_course_title = self.__specific_use_cases_course_title(
                        actual_course_title
                    )

                    return f"{actual_course_title}_INDESA_M"
                elif target_domain_id == 232031823:  # TRI STAR (TN)
                    actual_course_title = self.__specific_use_cases_course_title(
                        actual_course_title
                    )

                    return f"{actual_course_title}_TRI STAR_M"
                elif target_domain_userspace and self.__is_match(
                    target_domain_userspace
                ):  # STATE LEVEL
                    if (
                        "BYU" in actual_course_title
                    ):  # EXPECTING PATTERN MASTER BYU ....
                        if "ACCOM" in actual_course_title:
                            return f"MASTER {state_abbr}" + actual_course_title

                        byu_idx = actual_course_title.find("BYU")
                        return (
                            actual_course_title[:byu_idx]
                            + state_abbr
                            + actual_course_title[byu_idx:]
                        )

                    return f"MASTER {state_abbr}Stellar Virtual {actual_course_title}"
                elif target_parent_userspace and self.__is_match(
                    target_parent_userspace
                ):  # SCHOOL LEVEL
                    actual_course_title = self.__specific_use_cases_course_title(
                        actual_course_title
                    )

                    return f"{actual_course_title}_{target_domain_userspace.upper()}_M"
                # JUST RETURN THE TITLE
            else:
                state_abbr = us.states.lookup(target_domain_name)

                if state_abbr:
                    state_abbr = f"{state_abbr.abbr} "
                else:
                    state_abbr = ""

                # CAN STILL WORK THE SCHOOL-LEVEL COURSES
                # TREATING THE WHOLE TITLE AS THE COURSE TITLE
                if target_domain_id == 213069655:  # INDIANA
                    course_title = self.__specific_use_cases_course_title(course_title)

                    return f"{course_title}_INDESA_M"
                elif target_domain_id == 232031823:  # TRI STAR (TN)
                    course_title = self.__specific_use_cases_course_title(course_title)

                    return f"{course_title}_TRI STAR_M"
                elif target_domain_userspace and self.__is_match(
                    target_domain_userspace
                ):  # STATE LEVEL
                    if "BYU" in course_title:  # EXPECTING PATTERN MASTER BYU ....
                        if "ACCOM" in course_title:
                            return f"MASTER {state_abbr}" + course_title

                        byu_idx = course_title.find("BYU")
                        return (
                            course_title[:byu_idx] + state_abbr + course_title[byu_idx:]
                        )

                    return f"MASTER {state_abbr}Stellar Virtual {course_title}"
                elif target_parent_userspace and self.__is_match(
                    target_parent_userspace
                ):
                    # IF WE HIT HERE WE'VE CONFIRMED UNCONVENTIONAL COURSE NAMING
                    # AND WE'VE HIT A SCHOOL LEVEL DOMAIN
                    # TRY FOR STATE LEVEL DOMAIN NAMING SCHEMA
                    pattern = r"MASTER [A-Z]{2} Stellar Virtual "
                    match = re.search(pattern, course_title)
                    if match:
                        course_title = re.sub(pattern, "", course_title)
                    course_title = self.__specific_use_cases_course_title(course_title)

                    return f"{course_title}_{target_domain_userspace.upper()}_M"

            return course_title  # JUST RETURN THE TITLE
