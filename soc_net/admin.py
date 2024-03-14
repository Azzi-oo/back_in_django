from django.contrib import admin
from soc_net.models import (
    User,
    Post,
    Comment,
    Reaction,
)
from django.contrib.auth.models import Group
from rangefilter.filters import DateRangeFilter
from soc_net.filters import AuthorFilter, PostFilter
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    readonly_fields = (
        "date_joined",
    )

    search_fields = (
        "id",
        "username",
        "email",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("date_joined", DateRangeFilter),
    )


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "body",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    def get_body(self, obj):
        max_length = 64
        if len(obj.body) > max_length:
            return obj.body[:61] + "..."
        return obj.body

    get_body.short_description = "body"

    def get_comment_count(self, obj):
        return obj.comments.count()

    search_fields = (
        "id",
        "title",
        "author__username",
    )

    list_filter = (
        AuthorFilter,
        ("created_at", DateRangeFilter),
    )


@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "body",
        "created_at",
    )

    list_display_links = (
        "id",
        "body",
    )

    list_filter = (
        PostFilter,
        AuthorFilter,
    )

    # search_fields = (
    #     "author__username",
    #     "post__title",
    # )


@admin.register(Reaction)
class ReactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "value",
    )
    list_filter = (
        PostFilter,
        AuthorFilter,
        ("value", ChoiceDropdownFilter),
    )


admin.site.unregister(Group)
