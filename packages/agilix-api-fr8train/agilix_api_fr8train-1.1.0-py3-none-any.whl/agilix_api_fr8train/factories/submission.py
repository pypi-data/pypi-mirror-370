from agilix_api_fr8train.models.submissions import PutTeacherResponsesDefinition


def build_put_teacher_responses_payload(
    teacher_responses: list[PutTeacherResponsesDefinition],
) -> dict:
    return {
        "requests": {"teacherresponse": list(map(lambda x: dict(x), teacher_responses))}
    }
