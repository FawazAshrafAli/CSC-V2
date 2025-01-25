from django.urls import path
from .views import (
    AdminHomeView, MyProfileView, ChangePasswordView,
    UpdateProfileView,

    CreateFaqView, ListFaqView, FaqDetailView,
    UpdateFaqView, DeleteFaqView,

    EnquiryListView, DeleteEnquiryView, CscCenterEnquiriesListView,
    
    ListServiceView, DetailServiceView, UpdateServiceView, 
    CreateServiceView, DeleteServiceView, RemoveServiceImageView,

    ServiceEnquiryListView, DeleteServiceEnquiryView,

    BlogListView, BlogDetailView, CreateBlogView,
    UpdateBlogView, DeleteBlogView, RemoveBlogImageView,

    AddBlogCategoryView, BlogCategoryListView, DeleteBlogCategoryView,
    UpdateBlogCategoryView,

    CreateProductView, ProductListView, ProductDetailView,
    UpdateProductView, DeleteProductView, 

    ProductEnquiryListView, DeleteProductEnquiryView,
    
    get_product_categories, 
    AddProductCategoryView, UpdateProductCategoryView, DeleteProductCategoryView,
    ProductCategoryListView, 

    AddCscCenterView, GetDistrictView, GetBlockView,
    ListCscCenterView, DetailCscCenterView, UpdateCscCenterView,
    DeleteCscCenterView,
    RemoveSocialMediaLinkView, CscOwnersListView,
    
    ListCscCenterRequestView, CscCenterRequestDetailView, DeleteCscCenterRequestView,

    RejectCscCenterRequestView, ListRejectedCscCenterRequestView, 
    RejectedCscCenterRequestDetailView, CancelCscCenterRejectionView,
    
    ReturnCscCenterRequestView, ListReturnedCscCenterRequestView, 
    ReturnedCscCenterRequestDetailView, CancelCscCenterReturnView,

    ApproveCscCenterRequestView, ListApprovedCscCenterRequestView, 
    ApprovedCscCenterRequestDetailView, CancelCscCenterApprovalView,

    PosterListView, CreatePosterView, PosterDetailView,
    DeletePosterView, UpdatePosterView,

    get_all_states, get_all_districts, get_all_blocks,
    get_csc_keywords, get_name_types,
    GetDistrictDetailsView, GetBlockDetailsView, CreateStateView, 
    CreateDistrictView, CreateBlockView, EditStateView, 
    EditDistrictView, EditBlockView, DeleteStateView, 
    DeleteDistrictView, DeleteBlockView, CreateKeywordView, 
    EditKeywordView, DeleteKeywordView, CreateCscNameTypeView, 
    EditCscNameTypeView, DeleteCscNameTypeView,

    PaymentHistoryListView, PaymentHistoryDetailView,

    AddPriceView, GetPopUpDistrictView,

    AddHomePageBannersView, RemoveHomePageBannerView
    )

app_name = "csc_admin"

urlpatterns = [
    path("", AdminHomeView.as_view(), name="home"),
    path("my_profile", MyProfileView.as_view(), name="my_profile"),
    path("change_password", ChangePasswordView.as_view(), name="change_password"),
    path("update_profile", UpdateProfileView.as_view(), name="update_profile"),

    path("add_faq/", CreateFaqView.as_view(), name="add_faq"),
    path("faqs/", ListFaqView.as_view(), name="faqs"),
    path("faq/<str:slug>", FaqDetailView.as_view(), name="faq"),
    path("update_faq/<str:slug>", UpdateFaqView.as_view(), name="update_faq"),
    path("delete_faq/<str:slug>", DeleteFaqView.as_view(), name="delete_faq"),

    path('enquiries/', EnquiryListView.as_view(), name="enquiries"),
    path('delete_enquiry/<str:slug>', DeleteEnquiryView.as_view(), name="delete_enquiry"),
    path('centers_enquiries/', CscCenterEnquiriesListView.as_view(), name="centers_enquiries"),

    path("services/", ListServiceView.as_view(), name="services"),
    path("service/<str:slug>", DetailServiceView.as_view(), name="service"),
    path("create_service/", CreateServiceView.as_view(), name="create_service"),
    path("update_service/<str:slug>", UpdateServiceView.as_view(), name="update_service"),
    path("delete_service/<str:slug>", DeleteServiceView.as_view(), name="delete_service"),
    path("remove_service_image/<pk>", RemoveServiceImageView.as_view(), name="remove_service_image"),

    path("service_enquiries/", ServiceEnquiryListView.as_view(), name="service_enquiries"),
    path("delete_service_enquiry/<str:slug>", DeleteServiceEnquiryView.as_view(), name="delete_service_enquiry"),

    path('blogs/', BlogListView.as_view(), name="blogs"),
    path('blog/<str:slug>', BlogDetailView.as_view(), name="blog"),
    path('create_blog/', CreateBlogView.as_view(), name="create_blog"),
    path('update_blog/<str:slug>', UpdateBlogView.as_view(), name="update_blog"),
    path('delete_blog/<str:slug>', DeleteBlogView.as_view(), name="delete_blog"),
    path("remove_blog_image/<pk>", RemoveBlogImageView.as_view(), name="remove_blog_image"),    

    path('add_blog_category/', AddBlogCategoryView.as_view(), name="add_blog_category"),
    path('blog_categories/', BlogCategoryListView.as_view(), name="blog_categories"),
    path('update_blog_category/<str:slug>', UpdateBlogCategoryView.as_view(), name="update_blog_category"),
    path('delete_blog_category/<str:slug>', DeleteBlogCategoryView.as_view(), name="delete_blog_category"),

    path('create_product/', CreateProductView.as_view(), name = "create_product"),
    path('products/', ProductListView.as_view(), name = "products"),
    path('product/<str:slug>', ProductDetailView.as_view(), name = "product"),
    path('update_product/<str:slug>', UpdateProductView.as_view(), name = "update_product"),
    path('delete_product/<str:slug>', DeleteProductView.as_view(), name = "delete_product"),

    path('product_enquiries/', ProductEnquiryListView.as_view(), name = "product_enquiries"),
    path('delete_product_enquiry/<str:slug>', DeleteProductEnquiryView.as_view(), name = "delete_product_enquiry"),

    path('get_product_categories/', get_product_categories, name = "get_product_categories"),
    path('add_product_category/', AddProductCategoryView.as_view(), name = "add_product_category"),
    path('product_categories/', ProductCategoryListView.as_view(), name = "product_categories"),
    path('update_product_category/<str:slug>', UpdateProductCategoryView.as_view(), name = "update_product_category"),
    path('delete_product_category/<str:slug>', DeleteProductCategoryView.as_view(), name = "delete_product_category"),

    path('posters/', PosterListView.as_view(), name="posters"),
    path('poster/<str:slug>', PosterDetailView.as_view(), name="poster"),
    path('create_poster/', CreatePosterView.as_view(), name="create_poster"),
    path('update_poster/<str:slug>', UpdatePosterView.as_view(), name = "update_poster"),
    path('delete_poster/<str:slug>', DeletePosterView.as_view(), name = "delete_poster"),

    path('csc_center_requests/', ListCscCenterRequestView.as_view(), name = "csc_center_requests"),
    path('csc_center_request/<str:slug>', CscCenterRequestDetailView.as_view(), name = "csc_center_request"),
    path('delete_csc_center_request/<str:slug>', DeleteCscCenterRequestView.as_view(), name = "delete_csc_center_request"),

    path('reject_csc_center_request/<str:slug>', RejectCscCenterRequestView.as_view(), name = "reject_csc_center_request"),
    path('rejected_csc_centers/', ListRejectedCscCenterRequestView.as_view(), name = "rejected_csc_centers"),
    path('rejected_csc_center/<str:slug>', RejectedCscCenterRequestDetailView.as_view(), name = "rejected_csc_center"),
    path('cancel_csc_center_rejection/<str:slug>', CancelCscCenterRejectionView.as_view(), name = "cancel_csc_center_rejection"),

    path('return_csc_center_request/<str:slug>', ReturnCscCenterRequestView.as_view(), name = "return_csc_center_request"),
    path('returned_csc_centers/', ListReturnedCscCenterRequestView.as_view(), name = "returned_csc_centers"),
    path('returned_csc_center/<str:slug>', ReturnedCscCenterRequestDetailView.as_view(), name = "returned_csc_center"),
    path('cancel_csc_center_return/<str:slug>', CancelCscCenterReturnView.as_view(), name = "cancel_csc_center_return"),

    path('approve_csc_center_request/<str:slug>', ApproveCscCenterRequestView.as_view(), name = "approve_csc_center_request"),
    path('approved_csc_centers/', ListApprovedCscCenterRequestView.as_view(), name = "approved_csc_centers"),
    path('approved_csc_center/<str:slug>', ApprovedCscCenterRequestDetailView.as_view(), name = "approved_csc_center"),
    path('cancel_csc_center_approval/<str:slug>', CancelCscCenterApprovalView.as_view(), name = "cancel_csc_center_approval"),

    path('csc_centers/', ListCscCenterView.as_view(), name = "csc_centers"),
    path('csc_centers/<int:state>/<int:district>/<int:block>/<str:payment>/', ListCscCenterView.as_view(), name = "csc_centers_with_params"),

    path('add_csc/', AddCscCenterView.as_view(), name = "add_csc"),
    path('csc_center/<str:slug>', DetailCscCenterView.as_view(), name = "csc_center"),
    path('update_csc/<str:slug>', UpdateCscCenterView.as_view(), name = "update_csc"),
    path('delete_csc/<str:slug>', DeleteCscCenterView.as_view(), name = "delete_csc"),    
    path('remove_social_media_link/<str:slug>', RemoveSocialMediaLinkView.as_view(), name="remove_social_media_link"),

    path('csc_owners/', CscOwnersListView.as_view(), name="csc_owners"),
    path('csc_owners/<int:state>/<int:district>/<int:block>/', CscOwnersListView.as_view(), name="csc_owners_with_params"),

    path('get_districts/', GetDistrictView.as_view(), name="get_districts"),
    path('get_blocks/', GetBlockView.as_view(), name="get_blocks"),

    path('get_pop_up_districts/', GetPopUpDistrictView.as_view(), name="get_pop_up_districts"),

    path('get_all_states/', get_all_states, name="get_all_states"),
    path('get_all_districts/', get_all_districts, name="get_all_districts"),
    path('get_all_blocks/', get_all_blocks, name="get_all_blocks"),
    path('get_csc_keywords/', get_csc_keywords, name="get_csc_keywords"),
    path('get_name_types/', get_name_types, name="get_name_types"),

    path('get_district_detail/<int:pk>', GetDistrictDetailsView.as_view(), name="get_district_detail"),
    path('get_block_detail/<int:pk>', GetBlockDetailsView.as_view(), name="get_block_detail"),

    # Pop up box urls start
    path('add_state/', CreateStateView.as_view(), name="add_state"),
    path('edit_state/<int:pk>', EditStateView.as_view(), name="edit_state"),
    path('delete_state/<int:pk>', DeleteStateView.as_view(), name="delete_state"),

    path('add_district/', CreateDistrictView.as_view(), name="add_district"),
    path('edit_district/<int:pk>', EditDistrictView.as_view(), name="edit_district"),
    path('delete_district/<int:pk>', DeleteDistrictView.as_view(), name="delete_district"),

    path('add_block/', CreateBlockView.as_view(), name="add_block"),
    path('edit_block/<int:pk>', EditBlockView.as_view(), name="edit_block"),
    path('delete_block/<int:pk>', DeleteBlockView.as_view(), name="delete_block"),

    path('add_keyword/', CreateKeywordView.as_view(), name="add_keyword"),
    path('edit_keyword/<str:slug>', EditKeywordView.as_view(), name="edit_keyword"),
    path('delete_keyword/<str:slug>', DeleteKeywordView.as_view(), name="delete_keyword"),

    path('add_name_type/', CreateCscNameTypeView.as_view(), name="add_name_type"),
    path('edit_name_type/<str:slug>', EditCscNameTypeView.as_view(), name="edit_name_type"),
    path('delete_name_type/<str:slug>', DeleteCscNameTypeView.as_view(), name="delete_name_type"),
    # Pop up box urls end    

    path('payment_histories/', PaymentHistoryListView.as_view(), name="payment_histories"),
    path('payment_history/<str:slug>', PaymentHistoryDetailView.as_view(), name="payment_history"),

    path("add_price/", AddPriceView.as_view(), name="add_price"),

    path('add_home_page_banner/', AddHomePageBannersView.as_view(), name="add_home_page_banner"),
    path('remove_home_page_banner/', RemoveHomePageBannerView.as_view(), name="remove_home_page_banner"),
    ]
