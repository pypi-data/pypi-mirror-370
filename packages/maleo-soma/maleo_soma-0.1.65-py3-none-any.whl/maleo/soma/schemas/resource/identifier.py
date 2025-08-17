from pydantic import BaseModel, Field
from maleo.soma.mixins.general import Key, Name
from maleo.soma.types.base import OptionalString


class UrlSlug(BaseModel):
    url_slug: OptionalString = Field(None, description="URL Slug")


class ResourceIdentifier(Name, Key, UrlSlug):
    pass
