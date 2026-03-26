"""
Script one-time para gerar o refresh_token do Google Ads via OAuth2.

Pré-requisitos:
  1. No GCP (projeto dashboard-491401), crie uma credencial OAuth2
     tipo "Desktop App" e baixe o JSON.
  2. Preencha CLIENT_ID e CLIENT_SECRET abaixo (ou via .env).
  3. Execute: python scripts/generate_google_refresh_token.py
  4. Copie o refresh_token gerado para o .env.

Documentação: https://developers.google.com/google-ads/api/docs/oauth/overview
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")

SCOPES = ["https://www.googleapis.com/auth/adwords"]

if not CLIENT_ID or not CLIENT_SECRET:
    print("Configure GOOGLE_ADS_CLIENT_ID e GOOGLE_ADS_CLIENT_SECRET no .env antes de rodar.")
    exit(1)

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
credentials = flow.run_local_server(port=0)

print("\n=== COPIE PARA O .env ===")
print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
