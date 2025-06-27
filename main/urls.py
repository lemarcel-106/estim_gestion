
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.http import HttpResponse
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from django.shortcuts import redirect




api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")

admin.site.site_header = "Administration des Resultats"
admin.site.site_title = "Administration des Resultats"
admin.site.index_title = "Administration des Resultats"



urls_admin = [
]




urlpatterns = [
    path('', lambda request: redirect('admin/')),
    # path('', include('web_admin.urls')),
    path("robots.txt", robots_txt),
    path('admin/', admin.site.urls),
    path('api/', include('gestion_des_resultats.urls')),
    path('api/auth', api.urls),


    ##### Tools admin
]



# admin.site.site_header = "Administration des Resultats"
# admin.site.site_title = "Administration des Resultats"  
# admin.site.index_title = "Administration des Resultats"
# admin.site.site_header = "Administration des Resultats"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)