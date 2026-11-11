from rest_framework.routers import DefaultRouter # router automático do DRF
from .views import StationViewSet # ViewSet que fornece endpoints para Station

router = DefaultRouter(trailing_slash=False)
router.register(r'stations', StationViewSet) # registra rotas: /station/ e /station/{id}/

urlpatterns = router.urls # expõe as rotas geradas pelo router