from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserOpportunityViewSet, OpportunityList, ApplyOpportunity, WithdrawApplication

router = DefaultRouter()
router.register('opportunities/me', UserOpportunityViewSet)
router.register('opportunities/all', OpportunityList)

urlpatterns = [
    path('', include(router.urls)),
    path('opportunities/<int:opp_id>/apply', ApplyOpportunity),
    path('opportunities/<int:app_id>/withdraw', WithdrawApplication)
]
