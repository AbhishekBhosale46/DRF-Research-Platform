from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from core.models import Opportunity, Opportunity_Type, Domain, Skill, User_Profile
from .serializers import OpportunitySerializer, OpportunityTypeSerializer,SkillSerializer, DomainSerializer


""" CRUD endpoint for user's opportunity """
class UserOpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(owner=self.request.user)

    # Add uer profile validation 
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

""" Endpoint to list, retrive all opportunities """
class OpportunityList(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer