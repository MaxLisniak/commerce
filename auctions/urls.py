from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watch/<int:id>/", views.watch, name="watch"),
    path("unwatch/<int:id>/", views.unwatch, name="unwatch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("deactivate/<int:id>", views.deactivate, name="deactivate"),
    path("categories", views.categories, name="categories"),
    path("category/<str:name>", views.category, name="category"),
    path("notifications", views.notifications, name="notifications"),
    path("notification/<int:id>", views.notification, name="notification"),
]
