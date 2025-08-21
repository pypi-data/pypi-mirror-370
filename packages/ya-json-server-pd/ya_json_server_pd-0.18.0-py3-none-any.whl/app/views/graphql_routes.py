from strawberry.fastapi import GraphQLRouter

from app.config import GRAPHQL_IDE_ENABLE
from app.models.resources_graphql import graphql_schemas

graphql_router = GraphQLRouter(schema=graphql_schemas, graphiql=GRAPHQL_IDE_ENABLE)
