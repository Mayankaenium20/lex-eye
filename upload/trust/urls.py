from django.urls import path
from .views import TrustMasterListCreateView, TrustMasterDetailView, TrustValueListCreateView, TrustValueDetailView 
from .views import TrustDetailsListCreateView, TrustDetailsDetailView, TrusteeDetailsListCreateView, TrusteeDetailsDetailView
from .views import DocumentDetailsListCreateView, DocumentDetailsDetailView,  MailingTemplateDetailView, MailingTemplateListCreateView
from .views import ResolutionListCreateView, ResolutionDetailView, MasterListCreateView, MasterDetailView, MasterValueListCreateView, MasterValueDetailView
from .views import MeetingSchedulerListCreateView, MeetingSchedulerDetailView

from .views import search_trust, search_trustee, search_master_list, search_master_value

urlpatterns = [
    #trust_master model paths
    path('trust-master/', TrustMasterListCreateView.as_view(), name='trust-master-list-create'),
    path('trust-master/<int:pk>/', TrustMasterDetailView.as_view(), name='trust-master-detail'),
    
    #trust_value model paths
    path('trust-value/', TrustValueListCreateView.as_view(), name = 'trust-value-list-create'),
    path('trust-value/<int:pk>/', TrustValueDetailView.as_view(), name = 'trust-value-detail'),

    #trust_details model paths
    path('trust-details/', TrustDetailsListCreateView.as_view(), name = 'trust-detail-list-create'),
    path('trust-detail/<int:pk>/', TrustDetailsDetailView.as_view(), name = 'trust-details-detail'),

    #trustee_details model paths
    path('trustee-details/', TrusteeDetailsListCreateView.as_view(), name = 'trustee-detail-list-create'),
    path('trustee-detail/<int:pk>/', TrusteeDetailsDetailView.as_view(), name = 'trustee-details-detail'),

    # #document_detaisl model paths
    path('document-details/', DocumentDetailsListCreateView.as_view(), name='document-detail-list-create'),
    path('document-detail/<int:pk>/', DocumentDetailsDetailView.as_view(), name='document-detail-detail'),

    # #mailing_template model paths
    path('mailing-templates/', MailingTemplateListCreateView.as_view(), name='mailing-template-list-create'),
    path('mailing-templates/<int:pk>/', MailingTemplateDetailView.as_view(), name='mailing-template-detail'),
    
    # resolution model paths
    path('resolution/', ResolutionListCreateView.as_view(), name='resolution-list-create'),
    path('resolution/<int:pk>/', ResolutionDetailView.as_view(), name='resolution-detail'),

    # master model paths
    path('master/', MasterListCreateView.as_view(), name = 'master-list-create'),
    path('master/<int:pk>/', MasterDetailView.as_view(), name = 'master-detail'),

    # master value model paths
    path('master-value/', MasterValueListCreateView.as_view(), name = 'master-value-list-create'),
    path('master/<int:pk>/', MasterValueDetailView.as_view(), name = 'master-value-detail'),

    # meeting scheduler 
    path('meet-sch/', MeetingSchedulerListCreateView.as_view(), name = 'meet-sch-list-create'),
    path('meet/<int:pk>/', MeetingSchedulerDetailView.as_view(), name = 'meet-sch-detail'),


    ####SEARCH 
    path('search-trust/', search_trust, name='search_trust'),
    path('search-trustee/', search_trustee, name = 'search_trustee'),
    path('search-master-list/', search_master_list, name = 'search_master_list'),
    path('search-master-value/', search_master_value, name = 'search_master_value'),
]
