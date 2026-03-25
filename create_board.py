import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.authtoken.models import Token
from kanban_app.models import Board
from django.contrib.auth.models import User

token_key = '450510a169846b865a5eb8bff64af3526357bc93'

try:
    token = Token.objects.get(key=token_key)
    user = token.user
    board = Board.objects.create(
        title='Beispiel Board',
        description='Ein Board mit allen Informationen',
        owner=user
    )
    print(f'Board erstellt: {board.title}, ID: {board.id}')
except Token.DoesNotExist:
    print('Token nicht gefunden')
except Exception as e:
    print(f'Fehler: {e}')