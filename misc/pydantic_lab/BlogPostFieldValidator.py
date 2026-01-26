from typing import Literal, Annotated
from pydantic import BaseModel, ValidationError, Field, field_validator
from functools import partial
from devtools import debug
import datetime


class BlogPost(BaseModel):
    title: Annotated[
        str,
        Field(min_length=10, max_length=100, description="The title of the blog post"),
    ]
    content: str

    updated_at: datetime.datetime | None = None

    view_count: int = 0
    is_published: bool = False
    status: Literal["draft", "published", "archived"] = "draft"

    slug: Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            description="The slug of the blog post",
        ),
    ]

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        description="The date and time the blog post was created",
    )

    published_at: datetime.datetime = Field(
        default_factory=partial(datetime.datetime.now, datetime.UTC)
    )

    tags: list[str] = Field(
        default_factory=list, description="A list of tags for the blog post"
    )

    # Custom Logic Validator
    # Regex can check characters, but logic (like "no duplicates") needs python code.
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        # 1. Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Tags must be unique")

        # 2. Check for "forbidden" words
        forbidden_words = {"spam", "clickbait"}
        for tag in v:
            if tag.lower() in forbidden_words:
                raise ValueError(f"Tag '{tag}' is not allowed")

        # 3. Normalization (Clean the data)
        return [tag.lower() for tag in v]

    # Advanced: Validating Title format
    @field_validator("title")
    @classmethod
    def title_must_not_be_all_caps(cls, v: str) -> str:
        if v.isupper():
            raise ValueError("Title cannot be all uppercase (stop shouting!)")
        return v.title()  # Auto-fix capitalization


# --- Usage Test ---

try:
    my_blog_post = BlogPost(
        title="MY BLOG POST IS LOUD",  # This triggers the Validator error!
        content="This is the content...",
        tags=["Python", "python", "Coding"],  # This triggers the "Unique" error!
        slug="my-blog-post",
        status="published",
        is_published=True,
    )
    debug(my_blog_post)

except ValidationError as e:
    print("--- ❌ VALIDATION FAILED ---")
    print(e.json(indent=4))

# --- Correct Usage ---
print("\n--- ✅ CORRECT USAGE ---")
good_post = BlogPost(
    title="My Quiet Blog Post",
    content="Content...",
    tags=["Python", "Coding", "AI AGENTIC"],  # Validator will lowercase these
    slug="my-valid-post",
)
debug(good_post)
