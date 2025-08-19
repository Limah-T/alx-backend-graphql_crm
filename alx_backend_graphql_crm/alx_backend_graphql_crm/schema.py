from graphene_django import DjangoObjectType
from graphene import ObjectType
import graphene
from crm.models import CRMModel

class CRMModelType(DjangoObjectType):
    """GraphQL type for CRMModel."""
    class Meta:
        model = CRMModel
        fields = ('id', 'name')

class Query(ObjectType):
    crm_model = graphene.Field(CRMModelType)
    all_crm_models = graphene.List(CRMModelType)

    def resolve_all_crm_models(self, info):
        return CRMModel.objects.all()

    def resolve_crm_model(self, info):
        return CRMModel.objects.first()

schema = graphene.Schema(query=Query)