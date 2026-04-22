import strawberry


from app.core.graphql.query import Query as CoreQuery
from app.core.graphql.mutation import Mutation as CoreMutation
from app.auth.graphql.query import Query as AuthQuery
from app.auth.graphql.mutation import Mutation as AuthMutation
from app.talent.graphql.query import Query as TalentQuery
from app.talent.graphql.mutation import Mutation as TalentMutation

@strawberry.type
class Query(CoreQuery, AuthQuery, TalentQuery):
    pass

@strawberry.type
class Mutation(CoreMutation, AuthMutation, TalentMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
