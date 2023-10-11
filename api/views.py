from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from core.models import Opportunity, Domain, Skill, User_Profile, Application
from .serializers import OpportunitySerializer, SkillSerializer, DomainSerializer, ApplicationSerializer, UserProfileSerializer


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


""" Apply to opportunity """
@api_view(['POST'])
def ApplyOpportunity(request, opp_id):
    user = request.user
    opportunity = get_object_or_404(Opportunity, id=opp_id)
    try:
        application = Application.objects.get(applicant=user, opportunity=opportunity)
        return Response({"detail": "You have already applied to this opportunity"}, status=status.HTTP_400_BAD_REQUEST)
    except Application.DoesNotExist:
        user_profile = User_Profile.objects.filter(user=user)
        if user_profile:
            application = Application.objects.create(applicant=user, opportunity=opportunity)
            return Response({"detail": "Application created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "User profile not created"}, status=status.HTTP_400_BAD_REQUEST)


""" Withdraw application - some changes required """
@api_view(['POST'])
def WithdrawApplication(request, app_id):
    # first check if application exists with given id, then check if request.user and applicant are same and then do rest
    user = request.user
    try:
        application = Application.objects.get(id=app_id, applicant=user)
        application.delete()
        return Response({"detail": "Application withdrawn successfully"}, status=status.HTTP_200_OK)
    except Application.DoesNotExist:
        return Response({"detail": "You have not applied to this opportunity"}, status=status.HTTP_400_BAD_REQUEST)


""" Endpoint to list applications created by user"""
class ApplicationList(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(applicant=self.request.user)


""" Endpoint to list applications of the opportunity created by user """
@api_view(['GET'])
def  GetApplications(request, opp_id):
    user = request.user
    try:
        user_opportunity = Opportunity.objects.get(owner=user, id=opp_id)
    except ObjectDoesNotExist:
        return  Response({"detail": "Opportunity not found or not owned by the user"}, status=status.HTTP_404_NOT_FOUND)
    applications = Application.objects.filter(opportunity=user_opportunity)
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


""" Endpoint to process the application """
@api_view(['POST'])
def ProcessApplication(request, app_id, action):
    user = request.user
    feedback = request.data.get('feedback', '')
    try:
        application = Application.objects.get(opportunity__owner=user, id=app_id)
    except Application.DoesNotExist:
        return Response({"detail": "Application not found or not associated with your opportunity"}, status=status.HTTP_404_NOT_FOUND)
    
    if action=='accept':
        application.status = 'A'
    elif action=='reject':
        application.status = 'R'
    else:
        return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    application.feedback = feedback
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data, status=status.HTTP_200_OK)


""" Endpoint to list domains """
class DomainsList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


""" Endpoint to list skills """
class SkillsList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


""" CRUD Endpoint for user profile """
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User_Profile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


""" Endpoint to view user profile """
@api_view(['GET'])
def GetUserProfile(request, user_id):
    try:
        user_profile = User_Profile.objects.get(user=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return  Response({"detail": "User Profile with given id not found"}, status=status.HTTP_404_NOT_FOUND)
