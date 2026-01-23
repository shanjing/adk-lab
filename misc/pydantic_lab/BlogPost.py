from typing import Literal, Annotated
from pydantic import BaseModel, ValidationError, Field
from functools import partial
from devtools import debug

import datetime

class BlogPost(BaseModel):
    title: Annotated[str, Field(min_length=10, max_length=100, description="The title of the blog post")]
    content: str
    view_count: int = 0
    is_published: bool = False
    bio: str | None = None

    status: Literal["draft", "published", "archived"] = "draft"
    slug: Annotated[str, Field(
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="The slug of the blog post"
        )]

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        description="The date and time the blog post was created"
    )

    published_at: datetime.datetime = Field(
        default_factory=partial(datetime.datetime.now, datetime.UTC))

    tags: list[str] = Field(
        default_factory=list, 
        description="A list of tags for the blog post"
    )


my_blog_post= BlogPost(
    title="My Blog Post",
    content="This is the content of my blog post",
    tags=["python", "programming", "blog"],
    slug="my-blog-post",
    status="published",
    view_count=100,
    is_published=True,
    published_at=datetime.datetime.now(datetime.UTC),
)

print(my_blog_post.model_dump_json(indent=4))

debug(my_blog_post)