from django.urls import path,include
from . import views
from . import restaraunts
urlpatterns = [
#  path("home/", views.home,name="home"),
 path('signup',views.Register,name="register"),
 path('user_lst',views.Userreg_list,name="user-list"),
 path('login',views.UserLogin.as_view(),name='login'),
 path('dha-restaraunts',restaraunts.get_dharestaraunts,name='dha'),
 path('get_dharestaraunts_qry/<str:restaraunt>/',restaraunts.get_dharestaraunts_qry,name='get_dharestaraunts_qry'),
 path('restaraunt_x_datab/<str:restaraunt>/',restaraunts.restaraunt_x_database,name="restaraunt_x_datab"),
 path('user_preferences', views.user_preferences,name='user_preferences')
]
