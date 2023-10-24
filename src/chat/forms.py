from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from chat.models import ChatRoom


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ("room_name",)
        labels = {"room_name": _("Room name")}

    def __init__(self, *args, **kwargs):
        """
        Grants access to the request object.
        """
        self.request = kwargs.pop("request")
        super(ChatRoomForm, self).__init__(*args, **kwargs)
        self.fields["room_name"].widget.attrs["placeholder"] = _("Optional")

    def save(self, commit=True):
        instance = super(ChatRoomForm, self).save(commit=False)

        if commit:
            instance.admin = self.request.user
            instance.save()

            instance.members.add(self.request.user)

        return instance


class ChatRoomMembersForm(forms.Form):
    members_to_add = forms.CharField(
        label=_("Usernames"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Enter usernames separated by comma")}
        ),
        required=False,
    )

    def update_members(self, chat_room_instance):
        if usernames := self.cleaned_data.get("members_to_add"):
            username_list = [
                username.strip() for username in usernames.split(",")
            ]

            users_to_add = get_user_model().objects.filter(
                username__in=username_list
            )
            for user in users_to_add:
                chat_room_instance.members.add(user)
