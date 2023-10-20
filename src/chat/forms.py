from django import forms

from chat.models import ChatRoom


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ("room_name",)

    def __init__(self, *args, **kwargs):
        """
        Grants access to the request object.
        """
        self.request = kwargs.pop("request")
        super(ChatRoomForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ChatRoomForm, self).save(commit=False)

        if commit:
            instance.admin = self.request.user
            instance.save()

            instance.members.add(self.request.user)
            self.save_m2m()

        return instance
