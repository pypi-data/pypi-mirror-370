from agilix_api_fr8train.models.authentication import UpdatePasswordDefinition


def build_update_password_payload(update_password: UpdatePasswordDefinition) -> dict:
    return {"request": dict(update_password)}
