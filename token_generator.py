from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Define los permisos (Scopes)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# Esto imprimirá el JSON que debes poner en Render
print("--- COPIA ESTO EN TU VARIABLE DE ENTORNO 'GOOGLE_TOKEN' ---")
print(creds.to_json())