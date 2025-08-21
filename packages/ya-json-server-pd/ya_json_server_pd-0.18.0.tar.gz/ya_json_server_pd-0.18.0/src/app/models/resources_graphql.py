from dataclasses import make_dataclass
from typing import Annotated, Union

import strawberry
from strawberry.tools import merge_types

from app.controllers.resources_graphql import get_items_as_fields, get_resources_data
from app.handlers.commons import format_as_class_name
from app.models.db_json_content import JsonContentModel

json_content_mdl = JsonContentModel()
resourses_json_schema = json_content_mdl.get_resources_list_and_one_data()


def make_resources_class_from_sample(sample_data):
    rs_class_union = []
    for k, v in sample_data:
        rs_name = k
        rs_attributes = get_items_as_fields(v.items())
        class_name = format_as_class_name(rs_name)

        rs_class_union.append(
            strawberry.type(make_dataclass(class_name, fields=rs_attributes))
        )
    return rs_class_union


resources_class_union = make_resources_class_from_sample(resourses_json_schema.items())
ResourcesItems = Annotated[
    Union[*resources_class_union], strawberry.union("ResourcesItems")
]


@strawberry.type
class ResourceQuery:
    # getConsonant: list[ResourcesItems] = strawberry.field(resolver=get_resources_data)
    @strawberry.field
    def getConsonant(self) -> list[ResourcesItems]:
        return get_resources_data(resources_class_union)


resource_schema = strawberry.Schema(query=ResourceQuery)

graphql_queries = merge_types(
    "Query",
    (resource_schema.query,),
)

graphql_schemas = strawberry.Schema(query=graphql_queries)
