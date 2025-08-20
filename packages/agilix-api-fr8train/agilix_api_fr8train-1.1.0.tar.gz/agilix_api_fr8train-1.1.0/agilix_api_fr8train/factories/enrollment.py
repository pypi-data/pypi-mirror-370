from agilix_api_fr8train.models.enrollments import UpdateEnrollmentsDefinition


def build_update_enrollments_payload(
    update_enrollments: list[UpdateEnrollmentsDefinition],
) -> dict:
    return {
        "requests": {"enrollment": list(map(lambda x: dict(x), update_enrollments))}
    }
