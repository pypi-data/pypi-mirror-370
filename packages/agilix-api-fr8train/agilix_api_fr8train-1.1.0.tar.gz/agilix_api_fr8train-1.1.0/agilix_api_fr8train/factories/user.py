from agilix_api_fr8train.models.users import CreateUserDefinition
from agilix_api_fr8train.models.users import UpdateUserDefinition


def build_create_user_payload(new_user_list: list[CreateUserDefinition]):
    return {"requests": {"user": list(map(lambda x: dict(x), new_user_list))}}


def build_update_user_payload(user_list: list[UpdateUserDefinition]):
    return {"requests": {"user": list(map(lambda x: dict(x), user_list))}}


def build_delete_user_payload(user_list: list[int]):
    return {"requests": {"user": list(map(lambda x: {"userid": x}, user_list))}}
