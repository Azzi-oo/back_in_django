from rest_framework.routers import SimpleRouter

from soc_net.api.views import ChatViewSet, PostViewSet, ReactionViewSet, UserViewSet, CommentViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'posts', PostViewSet, basename="posts")
router.register(r'comments', CommentViewSet, basename="comments")
router.register(r'reaction', ReactionViewSet, basename="reaction")
router.register(r'chats', ChatViewSet, basename="chats")


urlpatterns = router.urls
