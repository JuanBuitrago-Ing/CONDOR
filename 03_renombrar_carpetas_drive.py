from google.colab import drive
drive.mount('/content/drive')

from googleapiclient.discovery import build
from google.colab import auth
auth.authenticate_user()

service = build('drive', 'v3')

RUTA = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'

renombrar = {
    'Bienteveo Común - Pitangus Sulphuratus':   'Bichofué',
    'Canario de los llanos - Sicalis flaveola': 'Canario de los llanos',
    'Gallito de Cienaga - Jacana jacana':       'Gallito de ciénaga',
    'Garrapatero Aní - Crotophaga ani':         'Garrapatero',
    'Gavilan caminero - Rupornis magnirostris': 'Gavilán caminero',
    'Golondrina común - Hirundo rustica':       'Golondrina común',
    'Loro real - Amazona ochrocephala':         'Loro real',
    'Perico Aliamarillo - Brotogeris Juglaris': 'Perico aliamarillo',
    'Tangara Azuleja - Thraupis episcopus':     'Tangara azuleja',
    'Tangara Palmera - Thraupis palmarum':      'Tangara palma',
    'Tortolita Colorada - Columbina talpacoti': 'Tortolita colorada',
    'Trepatroncos - Lepidocolaptes affinis':    'Trepatroncos',
    'Turpial Venezolano - Icterus Icterus':     'Turpial',
}

print("Buscando carpetas...\n")

for nombre_viejo, nombre_nuevo in renombrar.items():
    # Buscar la carpeta por nombre
    results = service.files().list(

        q=f"name='{nombre_viejo}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()

    archivos = results.get('files', [])

    if archivos:
        file_id = archivos[0]['id']
        service.files().update(
            fileId=file_id,
            body={'name': nombre_nuevo}
        ).execute()
        print(f"  ✓ '{nombre_viejo}' → '{nombre_nuevo}'")
    else:
        print(f"  ✗ No encontrada: '{nombre_viejo}'")

print("\nListo.")