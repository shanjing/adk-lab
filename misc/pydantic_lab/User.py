from pydantic import BaseModel, ValidationError
import datetime


class User(BaseModel):
    name: str
    full_name: str | None = None
    verified_at: datetime.datetime | None = None
    occupation: str
    email: str
    is_active: bool = True
    bio: str | None = None


try:
    user = User(
        name="John Doe",
        occupation=12.34,
        email="john.doe@example.com",
    )
except ValidationError as e:
    print(e)
    print(e.errors())
    exit()

user.bio = "I am a stock trader"
print(f" user.name: {user.name}, user.bio: {user.bio}\n\n")
print(user.model_dump())
print(user.model_dump_json(indent=4))
