import os
import io
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# Zakresy autoryzacji
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Funkcja do autoryzacji
def authenticate():
    creds = None
    # Jeśli już mamy zapisane poświadczenia, załaduj je
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Jeśli nie mamy poświadczeń, poproś użytkownika o autoryzację
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Zapisz poświadczenia do pliku token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# Funkcja do pobrania pliku z Dysku Google
def download_file(file_id, output_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Pobierz plik
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f'Download {int(status.progress() * 100)}%.')
    print(f'Plik zapisany jako {output_path}')

# ID pliku na Dysku Google
file_id = '1MN72qVprG-a8nw1Goi-WaqrwxjyDu9nK'  # Zastąp 'YOUR_FILE_ID' prawdziwym ID pliku

# Ścieżka do zapisania pliku na lokalnym dysku
output_file = 'Projekty specjalne - planowanie.xlsx'

# Pobierz plik
download_file(file_id, output_file)

# Wczytaj plik Excel do Pandas
df = pd.read_excel(output_file)

# Wyświetl dane
print(df.head())