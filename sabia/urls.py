from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from base.views import course_list, course_registration, cursos_xsendfile, material, my_course, payment_complete, \
    send_email, users_report, mercado_pago_webhook

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.search, name='search'),
    path('cursos', course_list, name='cursos'),
    path('cursos/<int:course_id>', course_registration, name='enroll'),
    path('cursos/finalizado', payment_complete, name='course_paid'),
    path('mercadopago_webhook/<str:token>', mercado_pago_webhook,
         name='mercado_pago_webhook'),
    path('cursos/meus-cursos', my_course, name='my_course'),
    path('cursos/inscritos/<int:course_id>', users_report, name='users-report'),
    re_path(r'^media/cursos', cursos_xsendfile, name='cursos_xsendfile'),
    path('material', material, name='material'),
    path('email', send_email, name='send_email'),
]

urlpatterns += i18n_patterns(
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('userauth.urls')),
)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
