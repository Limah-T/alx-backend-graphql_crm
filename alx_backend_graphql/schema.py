from graphene_django import DjangoObjectType
from graphene import ObjectType
import graphene
from crm.models import CRMModel

class CRMModelType(DjangoObjectType):
    """GraphQL type for CRMModel."""
    class Meta:
        model = CRMModel
        fields = ('id', 'name')

class Query(graphene.ObjectType):
    crm_model = graphene.Field(CRMModelType)
    all_crm_models = graphene.List(CRMModelType)

    def resolve_all_crm_models(self, info):
        return CRMModel.objects.all()

    def resolve_crm_model(self, info):
        return CRMModel.objects.first()


schema = graphene.Schema(query=Query)

# import graphene
# from crm.schema import Query as CRMQuery, Mutation as CRMMutation

# class Query(CRMQuery, graphene.ObjectType):
#     pass

# class Mutation(CRMMutation, graphene.ObjectType):
#     pass

# schema = graphene.Schema(query=Query, mutation=Mutation)