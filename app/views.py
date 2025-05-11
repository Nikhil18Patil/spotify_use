
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
from .utils import spotify_get, spotify_post
import requests
from urllib.parse import urlencode
import time

class SpotifyAuthorize(APIView):
    def get(self, request):
        print("CLIENT_ID repr:", repr(settings.SPOTIFY_CLIENT_ID))
        print("redirect repr:", repr(settings.SPOTIFY_REDIRECT_URI))
        
        scopes = "user-top-read user-read-currently-playing user-modify-playback-state user-follow-read"
        params = {
            "client_id":     settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri":  settings.SPOTIFY_REDIRECT_URI,
            "scope":         scopes,
        }
        url = "https://accounts.spotify.com/authorize?" + urlencode(params)
        return redirect(url)

class SpotifyCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "client_secret": settings.SPOTIFY_CLIENT_SECRET,
            }
        ).json()
        # persist resp["access_token"], resp["refresh_token"], resp["expires_in"]
        from .utils import _write_token
        print(resp)
        token_data = {
            "access_token": resp["access_token"],
            "refresh_token": resp["refresh_token"],
            "expires_at": int(time.time()) + resp["expires_in"]
        }
        _write_token(token_data)
        return Response({"status": "saved tokens"})

class SpotifyData(APIView):
    def get(self, request):
        top = spotify_get("me/top/tracks", limit=10)
        now = spotify_get("me/player/currently-playing")
        artists = spotify_get("me/following", type="artist", limit=50)

        top_tracks = [track["name"] for track in top.get("items", [])] if top else []
        now_playing_track = now.get("item") if now else None
        now_playing_name = now_playing_track.get("name") if now_playing_track else None
        now_playing_id = now_playing_track.get("id") if now_playing_track else None

        followed_artists = [a["name"] for a in artists.get("artists", {}).get("items", [])] if artists else []

        return Response({
            "top_tracks": top_tracks,
            "now_playing": now_playing_name,
            "now_playing_id": now_playing_id,
            "followed_artists": followed_artists,
            "controls": {
                "play_track_endpoint": f"/spotify/play?track_id={now_playing_id}" if now_playing_id else "/spotify/play?track_id=...",
                "stop_playback_endpoint": "/spotify/stop"
            }
        })


class SpotifyPlay(APIView):
    def post(self, request):
        track_id = request.data.get("track_id") or request.query_params.get("track_id")
        if not track_id:
            return Response({"error": "track_id required"}, status=400)
        spotify_post("me/player/play", json={"uris": [f"spotify:track:{track_id}"]})
        return Response({"success": True, "track_id": track_id})


class SpotifyStop(APIView):
    def post(self, request):
        spotify_post("me/player/pause")
        return Response({"success": True})
