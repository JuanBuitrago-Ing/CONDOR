import os
import time
import requests

RUTA_FOTOS = '/home/juan/sistema_aves/static/fotos'
os.makedirs(RUTA_FOTOS, exist_ok=True)

ESPECIES = {
    'Amazilia de vientre blanco':   'Chrysuronia versicolor',
    'Golondrina de muslos blancos': 'Atticora tibialis',
    'Gorrion Pectoral':             'Arremon taciturnus',
    'Mango gorjinegro':             'Anthracothorax nigricollis',
    'Mosquerito ojiblanco':         'Atalotriccus pilaris',
    'Tecolote llanero':             'Athene cunicularia',
    'Urraca violacea':              'Cyanocorax violaceus',
    'Bichofue':                     'Pitangus sulphuratus',
    'Siriri comun':                 'Tyrannus melancholicus',
    'Tijereta':                     'Tyrannus savana',
    'Garza del ganado':             'Bubulcus ibis',
    'Garza blanca':                 'Ardea alba',
    'Garzon azul':                  'Ardea cocoi',
    'Garza tigre':                  'Tigrisoma lineatum',
    'Corocoro colorado':            'Eudocimus ruber',
    'Espatula rosada':              'Platalea ajaja',
    'Gaban llanero':                'Jabiru mycteria',
    'Ciguena americana':            'Mycteria americana',
    'Pato real':                    'Cairina moschata',
    'Jacana americana':             'Jacana jacana',
    'Gavilan caminero':             'Rupornis magnirostris',
    'Halcon reidor':                'Herpetotheres cachinnans',
    'Caracara crestado':            'Caracara plancus',
    'Condor de los Andes':          'Vultur gryphus',

    'Pava hedionda':                'Opisthocomus hoazin',
    'Guacamaya azul y amarilla':    'Ara ararauna',
    'Loro real':                    'Amazona amazonica',
    'Carpintero real':              'Melanerpes rubricapillus',
    'Tucan pechiblanco':            'Ramphastos tucanus',
    'Martin pescador':              'Megaceryle torquata',
    'Martin pescador amazonico':    'Chloroceryle amazona',
    'Tangara azuleja':              'Thraupis episcopus',
    'Tangara palma':                'Thraupis palmarum',
    'Canario de los llanos':        'Sicalis flaveola',
    'Pico de plata':                'Ramphocelus carbo',
    'Turpial':                      'Icterus icterus',
    'Chamon parasito':              'Molothrus bonariensis',
    'Garrapatero':                  'Crotophaga ani',
    'Cuco ardilla':                 'Piaya cayana',
    'Chotacabras comun':            'Nyctidromus albicollis',
    'Golondrina azul y blanca':     'Pygochelidon cyanoleuca',
    'Golondrina de rio':            'Stelgidopteryx ruficollis',
    'Hormiguero':                   'Thamnophilus doliatus',
    'Saltarin cola de alambre':     'Pipra filicauda',
    'Gallito de cienaga':           'Porphyrio martinica',
    'Trepatroncos':                 'Xiphorhynchus susurrans',
    'Cucarachero':                  'Troglodytes aedon',
    'Sinsonte':                     'Mimus gilvus',
    'Aguila pescadora':             'Pandion haliaetus',
    'Pato cuervo':                  'Nannopterum brasilianus',
    'Garza nocturna':               'Nycticorax nycticorax',
    'Garza cangrejera':             'Butorides striata',
    'Garza tricolor':               'Egretta tricolor',
    'Garza pechicastana':           'Agamia agami',
    'Cotorra carisucio':            'Eupsittula pertinax',
    'Periquito de anteojos':        'Forpus conspicillatus',

    'Perico aliamarillo':           'Brotogeris jugularis',
    'Loro amazonico':               'Amazona ochrocephala',
    'Guacamaya escarlata':          'Ara macao',
    'Guacamaya verde':              'Ara militaris',
    'Loro torcaza':                 'Pionus menstruus',
    'Cuclillo piquioscuro':         'Coccyzus melacoryphus',
    'Cuco hormiguero':              'Dromococcyx phasianellus',
    'Buho de anteojos':             'Pulsatrix perspicillata',
    'Lechuza comun':                'Tyto alba',
    'Lechucita ferruginosa':        'Glaucidium brasilianum',
    'Vencejo amazonico':            'Chaetura brachyura',
    'Ermitano rojizo':              'Phaethornis ruber',
    'Ermitano largo':               'Phaethornis longirostris',
    'Colibri coliblanco':           'Florisuga mellivora',
    'Colibri coliazul':             'Thalurania furcata',
    'Trogon violaceo':              'Trogon violaceus',
    'Trogon collarejo':             'Trogon collaris',
    'Momoto amazonico':             'Momotus momota',
    'Martin pescador enano':        'Chloroceryle aenea',
    'Carpintero ondulado':          'Celeus undatus',
    'Carpintero lineado':           'Dryocopus lineatus',
    'Trepador pico de cuna':        'Glyphorhynchus spirurus',
    'Colaespina rojiza':            'Synallaxis rutilans',
    'Atrapamoscas real':            'Onychorhynchus coronatus',
    'Atrapamoscas de agua':         'Fluvicola pica',
    'Tirano aguas':                 'Arundinicola leucocephala',
    'Mosquero pecho amarillo':      'Myiozetetes cayanensis',
    'Copeton crestiblanco':         'Elaenia albiceps',
    'Doradito olivaceo':            'Pseudocolopteryx acutipennis',
    'Hormiguero vientre blanco':    'Myrmeciza longipes',
    'Hormiguero dorsirrufo':        'Thamnophilus palliatus',
    'Saltarin cabecidorado':        'Ceratopipra erythrocephala',

    'Saltarin azulado':             'Lepidothrix coronata',
    'Pepitero verdoso':             'Saltator maximus',
    'Tangara turquesa':             'Tangara mexicana',
    'Tangara sietecolores':         'Tangara chilensis',
    'Dacnis azul':                  'Dacnis cayana',
    'Mielero patirrojo':            'Cyanerpes cyaneus',
    'Semillero pico grueso':        'Oryzoborus angolensis',
    'Tortolita colorada':           'Columbina talpacoti',
    'Paloma colorada':              'Patagioenas cayennensis',
    'Paloma morada':                'Patagioenas subvinacea',
    'Perdiz colorada':              'Colinus cristatus',
    'Aninga americana':             'Anhinga anhinga',
}

HEADERS = {'User-Agent': 'CONDOR-IA-Bot/1.0 (Universidad de los Llanos)'}

def nombre_a_archivo(nombre):
    n = nombre.lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),(' ','_')]:
        n = n.replace(a, b)
    return n + '.jpg'

def buscar_inat(cientifico):
    try:
        url = f"https://api.inaturalist.org/v1/taxa?q={cientifico.replace(' ','+')}&rank=species&per_page=1"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data['results']:
                taxon = data['results'][0]
                if taxon.get('default_photo') and taxon['default_photo'].get('medium_url'):
                    return taxon['default_photo']['medium_url']

        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def descargar(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
        return None
    except:
        return None

total = len(ESPECIES)
ok, fallidas = 0, []

print(f"Descargando {total} imagenes via iNaturalist...\n")

for i, (nombre, cientifico) in enumerate(ESPECIES.items(), 1):
    archivo = nombre_a_archivo(nombre)
    ruta    = os.path.join(RUTA_FOTOS, archivo)

    if os.path.exists(ruta) and os.path.getsize(ruta) > 5000:
        print(f"[{i:3}/{total}] Ya existe — {nombre}")
        ok += 1
        continue

    print(f"[{i:3}/{total}] {nombre}...")
    img_url = buscar_inat(cientifico)

    if img_url:

        datos = descargar(img_url)
        if datos:
            with open(ruta, 'wb') as f:
                f.write(datos)
            print(f"  OK ({len(datos)//1024} KB)")
            ok += 1
        else:
            print(f"  Error descargando")
            fallidas.append(nombre)
    else:
        print(f"  No encontrada")
        fallidas.append(nombre)

    time.sleep(1)

print(f"\n{'='*50}")
print(f"Descargadas: {ok}/{total}")
print(f"Fallidas:    {len(fallidas)}")
if fallidas:
    print("\nBuscar manualmente:")
    for f in fallidas:
        print(f"  - {f}")
print(f"Imagenes en: {RUTA_FOTOS}")