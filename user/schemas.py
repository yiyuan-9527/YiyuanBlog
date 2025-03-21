from ninja import Field, Schema


class CreateUserRequest(Schema):
    email: str = Field(examples=['yiyuan@example.com'])
    password: str = Field(min_length=8, exmples=['password123'])


class LoginRequest(Schema):
    email: str = Field(examples=['yiyuan@example.com'])
    password: str = Field(examples=['password123'])
