from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post
from django.shortcuts import redirect
from .util import update_or_create_user_tokens, is_spotify_authenticated
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


class AuthUrl(APIView):
    def get(self, request):
        scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        url = Request('GET', 'https://accounts.spotify.com/authorize/', params={
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': scope,
        }).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request):
    code = request.GET.get('code')
    response = post('https://accounts.spotify.com/api/token/', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }).json()
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')
    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_user_tokens(session_id=request.session.session_key, access_token=access_token,
                                 token_type=token_type, expires_in=expires_in, refresh_token=refresh_token)
    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
