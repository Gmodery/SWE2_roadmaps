"""
URL configuration for roadmap_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from roadmaps import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("pages/dashboard", views.dashboard, name="dashboard"),
    path("pages/logout", views.logout_view, name="logout"),
    path("pages/dashboard/create-roadmap", views.create_roadmap_form, name="create_roadmap"),
    path("pages/dashboard/join-class", views.join_class_view, name="join_class"),
    path('pages/dashboard/class/<int:class_id>/', views.class_detail_view, name='class_detail'),
    path('pages/dashboard/remove-class/<int:class_id>/', views.class_delete_view, name='class_delete'),
    path('pages/dashboard/create-project/<int:class_id>/', views.create_project_view, name='project-create'),
    path('pages/dashboard/class/<int:class_id>/project/<int:project_id>/', views.project_details_view, name='project-details'),
    path('pages/dashboard/class/<int:class_id>/project/<int:project_id>/<int:roadmap_id>/', views.roadmap_details_view, name='project-details'),
    path('pages/dashboard/account', views.account_detail_view, name='account')
]

# Path syntax: path(URL route pattern (not necessarily path within templates, just url to follow in browser to get to view), 
# view function that should handle request (calls render() which loads .php), 
# unique identifier (optional))