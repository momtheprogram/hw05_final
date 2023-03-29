from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta): # тут не обязательно прописывать `(UserCreationForm.Meta)` для `Meta`
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
