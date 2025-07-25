from ninja import Field, Schema


class CreateUserRequest(Schema):
    email: str = Field(examples=['yiyuan@example.com'])
    password: str = Field(min_length=8, exmples=['password123'])


class UpdateUserInfoIn(Schema):
    nickname: str | None = Field(max_length=20, examples=['寶淇姐姐'])


class PrivateUserInfoOut(Schema):
    id: int
    username: str | None = Field(examples=['寶淇姐姐'])
    email: str = Field(examples=['yiyuan@example.com'])
    bio: str | None = Field(examples=['個人簡介'])
    avatar: str | None = Field(examples=['https://example.com/avatar.jpg'])
    is_active: bool = Field(examples=[True, False])

    @classmethod
    def from_orm(cls, user):
        avatar_url = user.avatar.url if user.avatar else None
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            bio=user.bio,
            avatar=avatar_url,
            is_active=user.is_active,
        )


class LoginRequest(Schema):
    email: str = Field(examples=['yiyuan@example.com'])
    password: str = Field(examples=['password123'])


class RefreshTokenRequest(Schema):
    refresh_token: str = Field(examples=['refresh_token'])


class VerifyEmailRequest(Schema):
    active_token: str = Field(examples=['token123'])


class FollowToggleOut(Schema):
    is_following: bool = Field(examples=[True, False])
    follower_count: int = Field(examples=[10])
    following_count: int = Field(examples=[5])
