from pydantic import BaseModel, model_validator
from typing import Literal
import datetime

class BlogPost(BaseModel):
    title: str
    status: Literal["draft", "published"] = "draft"
    published_at: datetime.datetime | None = None

    # THE MODEL VALIDATOR
    # mode='after' means "Run this AFTER all individual fields are checked"
    @model_validator(mode='after')
    def check_publication_rules(self):
        
        # Rule: If status is 'published', we MUST have a date.
        if self.status == 'published' and self.published_at is None:
            raise ValueError("Post is marked 'published' but is missing 'published_at' date.")
            
        # Rule: If status is 'draft', we SHOULD NOT have a date (optional logic)
        if self.status == 'draft' and self.published_at is not None:
             raise ValueError("Draft posts cannot have a publication date yet.")
             
        return self

# --- Test Cases ---

# ❌ Fails (Logic Error)
try:
    BlogPost(title="My Post", status="published", published_at=None)
except Exception as e:
    print(e) 
    # Output: Value error, Post is marked 'published' but is missing 'published_at' date.

# ✅ Works
post = BlogPost(
    title="My Post", 
    status="published", 
    published_at=datetime.datetime.now()
)