from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserOpportunityViewSet, OpportunityList, ApplyOpportunity, WithdrawApplication, ApplicationList, GetApplications

router = DefaultRouter()
router.register('opportunities/me', UserOpportunityViewSet)
router.register('opportunities/all', OpportunityList)
router.register('applications', ApplicationList)

urlpatterns = [
    path('', include(router.urls)),
    path('opportunities/<int:opp_id>/apply', ApplyOpportunity),
    path('applications/<int:app_id>/withdraw', WithdrawApplication),
    path('opportunities/me/<int:opp_id>/applications', GetApplications)
]
