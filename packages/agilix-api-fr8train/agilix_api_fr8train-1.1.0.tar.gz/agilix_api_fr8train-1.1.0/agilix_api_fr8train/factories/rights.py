from agilix_api_fr8train.models.rights import UpdateRightsDefinition


def build_update_rights_payload(rights_list: list[UpdateRightsDefinition]):
    return {"requests": {"rights": list(map(lambda x: dict(x), rights_list))}}
