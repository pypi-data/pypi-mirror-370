class UpdatePasswordDefinition:
    user_id: int
    password: str

    def __init__(self, user_id: int, password: str):
        self.user_id = user_id
        self.password = password

    def __iter__(self):
        yield "cmd", "updatepassword"
        yield "oldpassword", ""
        yield "userid", self.user_id
        yield "password", self.password
