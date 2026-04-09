import json
import base64
import urllib.parse
import urllib.request

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def index(request):
    """Main page — renders the connect button."""
    context = {
        "spotify_client_id": settings.SPOTIFY_CLIENT_ID,
        "spotify_redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "spotify_scopes": "user-read-private user-read-email",
    }
    return render(request, "spotify_app/index.html", context)


def callback(request):
    """OAuth callback page — receives the auth code from Spotify and passes it to the opener."""
    context = {
        "code": request.GET.get("code", ""),
        "state": request.GET.get("state", ""),
        "error": request.GET.get("error", ""),
    }
    return render(request, "spotify_app/callback.html", context)


@csrf_exempt
@require_POST
def spotify_token(request):
    """Server-side token exchange — keeps CLIENT_SECRET off the client."""
    try:
        body = json.loads(request.body)
        code = body.get("code")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not code:
        return JsonResponse({"error": "Missing code"}, status=400)

    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    redirect_uri = settings.SPOTIFY_REDIRECT_URI

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }).encode()

    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read().decode())
        # Only return the access token — never expose refresh token to the client
        return JsonResponse({"access_token": token_data["access_token"]})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return JsonResponse({"error": "Token exchange failed", "detail": error_body}, status=e.code)
    except Exception as e:
        return JsonResponse({"error": "Internal server error", "detail": str(e)}, status=500)
