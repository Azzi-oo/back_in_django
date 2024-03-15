from rest_framework import serializers
from soc_net.models import Chat, Comment, Message, Post, Reaction, User
from django.db.models import Q


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "is_friend")

    def get_is_friend(self, obj) -> bool:
        current_user = self.context["request"].user
        return current_user in obj.friends.all()


class NestedPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "created_at",
        )


class UserRetrieveSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()
    posts = NestedPostListSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "is_friend",
            "posts",
            "friend_count",
            "posts",
        )

    def get_friend_count(self, obj) -> int:
        return obj.friends.count()

    def get_is_friend(self, obj) -> bool:
        return obj in self.context["request"].user.friends.all()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class PostListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer()
    body = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
            "created_at",
        )

    def get_body(self, obj) -> str:
        if len(obj.body) > 128:
            return obj.body[:125] + "..."
        return obj.body


class PostRetrieveSerializer(serializers.ModelSerializer):
    author = UserShortSerializer()
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
            "my_reaction",
            "created_at",
        )

    def get_my_reaction(self, obj) -> str:
        reaction = self.context["request"].user.eractions.filter(post=obj).last()
        return reaction.value if reaction else ""


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].metod == "GET":
            fields["author"] = UserShortSerializer(read_only=True)
        return fields

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "post",
            "body",
            "created_at",
        )


class ReactionSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Reaction
        fields = (
            "id",
            "author",
            "post",
            "value",
        )

    def create(self, validated_data):
        reaction = Reaction.objects.filter(
            post=validated_data["post"],
            author=validated_data["author"],
        ).last()

        if not reaction:
            return Reaction.objects.create(**validated_data)

        if reaction.value == validated_data["value"]:
            reaction.value = None
        else:
            reaction.value = validated_data["value"]
        reaction.save()

        return reaction


class ChatSerializer(serializers.ModelSerializer):
    user_1 = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Chat
        fields = ("user_1", "user_2")

    def create(self, validated_data):
        request_user = validated_data["user_1"]
        second_user = validated_data["user_2"]

        chat = Chat.objects.filter(
            Q(user_1=request_user, user_2=second_user)
            | Q(user_1=second_user, user_2=request_user)
        ).first()
        if not chat:
            chat = Chat.objects.create(
                user_1=request_user,
                user_2=second_user,
            )

        return chat


class MessageListSerializer(serializers.ModelSerializer):
    message_author = serializers.CharField()

    class Meta:
        model = Message
        fields = ("id", "content", "message_author", "created_at")
