import json
from flask import Flask, render_template_string, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
RUTA_DB = '/home/juan/sistema_aves/detecciones.db'

ESPECIES = {
    # ── 7 ENTRENADAS ─────────────────────────────────────────
    'Amazilia de vientre blanco':  {'cientifico':'Chrysuronia versicolor','descripcion':'Colibrí de tamaño mediano con plumaje verde iridiscente y vientre blanco característico. Frecuente en bordes de bosque y jardines floridos. Se alimenta del néctar de flores tubulares y es un importante polinizador de los Llanos.','habitat':'Bordes de bosque, jardines, sabanas arboladas','familia':'Trochilidae','entrenada':True,'audio':None},
    'Golondrina de muslos blancos': {'cientifico':'Atticora tibialis','descripcion':'Golondrina esbelta de color negro azulado con muslos blancos muy distintivos. Vuela con gran agilidad sobre ríos y cuerpos de agua capturando insectos al vuelo. Construye sus nidos en barrancos y orillas de ríos.','habitat':'Ríos, quebradas, cuerpos de agua','familia':'Hirundinidae','entrenada':True,'audio':None},
    'Gorrion Pectoral':            {'cientifico':'Arremon taciturnus','descripcion':'Ave terrestre de hábitos discretos con pecho negro y dorso oliváceo muy característicos. Habita en el sotobosque denso y bordes de selva. Su canto suave y melodioso es típico del amanecer en los Llanos.','habitat':'Sotobosque, bordes de selva','familia':'Passerellidae','entrenada':True,'audio':None},
    'Mango gorjinegro':            {'cientifico':'Anthracothorax nigricollis','descripcion':'Colibrí robusto y llamativo con garganta negra iridiscente y dorso verde brillante. Uno de los colibríes más comunes de los Llanos. Defiende activamente sus territorios de alimentación frente a otras aves.','habitat':'Áreas abiertas, jardines, bordes de bosque','familia':'Trochilidae','entrenada':True,'audio':None},
    'Mosquerito ojiblanco':        {'cientifico':'Atalotriccus pilaris','descripcion':'Pequeño atrapamoscas con anillo ocular blanco muy característico y plumaje grisáceo. Habita en zonas áridas y matorrales secos de los Llanos. Captura insectos en cortos vuelos desde perchas expuestas.','habitat':'Matorrales secos, zonas áridas','familia':'Tyrannidae','entrenada':True,'audio':None},
    'Tecolote llanero':            {'cientifico':'Athene cunicularia','descripcion':'Búho pequeño de hábitos diurnos que anida en madrigueras en el suelo. Muy característico de las sabanas abiertas colombianas. Se observa parado en postes, termiteros y montículos de tierra al atardecer.','habitat':'Sabanas abiertas, pastizales, campos de cultivo','familia':'Strigidae','entrenada':True,'audio':None},
    'Urraca violacea':             {'cientifico':'Cyanocorax violaceus','descripcion':'Córvido de colores llamativos con plumaje azul violáceo y negro. Ave muy social y ruidosa que se mueve en grupos familiares bulliciosos. Muy inteligente y omnívora, común en bordes de bosque de los Llanos.','habitat':'Bordes de bosque, áreas arboladas, sabanas','familia':'Corvidae','entrenada':True,'audio':None},
    # ── 43 CATÁLOGO META / LLANOS ORIENTALES ─────────────────
    'Bichofue':                    {'cientifico':'Pitangus sulphuratus','descripcion':'Tiránido grande y ruidoso de pecho amarillo brillante y corona roja oculta. Muy común y territorial. Su canto "bichofué" le da el nombre popular. Omnívoro y oportunista.','habitat':'Áreas abiertas, jardines, orillas de ríos, potreros','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Siriri comun':                {'cientifico':'Tyrannus melancholicus','descripcion':'Tiránido esbelto con corona naranja oculta. Se posa en lo alto de árboles y postes desde donde caza insectos en vuelo. Muy común en los Llanos durante todo el año.','habitat':'Áreas abiertas, bordes de bosque, potreros','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Tijereta':                    {'cientifico':'Tyrannus savana','descripcion':'Ave inconfundible por su cola extremadamente larga en forma de tijera en el macho. Abundante en sabanas abiertas de los Llanos. Migratoria austral, presente en verano.','habitat':'Sabanas abiertas, potreros, áreas agrícolas','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Garza del ganado':            {'cientifico':'Bubulcus ibis','descripcion':'Garza blanca de talla mediana frecuentemente asociada al ganado bovino. Forrajea insectos y pequeños animales ahuyentados por los bovinos al caminar. Muy común en todo el Meta.','habitat':'Potreros, pastizales, áreas agrícolas','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garza blanca':                {'cientifico':'Ardea alba','descripcion':'La garza blanca más grande. Plumaje completamente blanco con pico amarillo largo. Habita en humedales, ríos y lagunas. En época de cría desarrolla plumas nupciales muy vistosas.','habitat':'Humedales, ríos, lagunas, arrozales','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garzon azul':                 {'cientifico':'Ardea cocoi','descripcion':'La garza más grande de Suramérica con plumaje gris azulado y corona negra. Solitaria y de hábitos acuáticos, caza peces con paciencia en orillas de ríos y lagunas.','habitat':'Ríos, lagunas, humedales, playas','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garza tigre':                 {'cientifico':'Tigrisoma lineatum','descripcion':'Garza robusta con marcado patrón bandeado en el cuello. De hábitos sigilosos y crepusculares, se camufla perfectamente entre la vegetación ribereña densa.','habitat':'Ríos, caños, bosques de galería','familia':'Ardeidae','entrenada':False,'audio':None},
    'Corocoro colorado':           {'cientifico':'Eudocimus ruber','descripcion':'Ibis de plumaje rojo carmesí brillante, uno de los más emblemáticos del Meta. Se congrega en grandes colonias en los morichales. Su color viene de los carotenoides de su dieta.','habitat':'Humedales, morichales, sabanas inundables','familia':'Threskiornithidae','entrenada':False,'audio':None},
    'Espatula rosada':             {'cientifico':'Platalea ajaja','descripcion':'Ave de plumaje rosado intenso con pico en forma de espátula única. Filtra el agua en movimientos laterales buscando peces y crustáceos. Muy vistosa en vuelo.','habitat':'Humedales, lagunas someras, playas de río','familia':'Threskiornithidae','entrenada':False,'audio':None},
    'Gaban llanero':               {'cientifico':'Jabiru mycteria','descripcion':'La cigüeña más grande de América con cuello rojo y negro y cuerpo blanco. Símbolo icónico de los Llanos colombianos y venezolanos. Anida en la cima de los árboles más altos.','habitat':'Sabanas inundables, lagunas, morichales','familia':'Ciconiidae','entrenada':False,'audio':None},
    'Cigueña americana':           {'cientifico':'Mycteria americana','descripcion':'Cigüeña con cabeza y cuello desnudos de color oscuro. Forrajea táctilmente en aguas someras con el pico abierto para capturar peces. Anida en colonias mixtas.','habitat':'Humedales, lagunas, ríos, esteros','familia':'Ciconiidae','entrenada':False,'audio':None},
    'Pato real':                   {'cientifico':'Cairina moschata','descripcion':'El pato más grande de Suramérica. El macho negro con manchas blancas posee carúncula roja sobre el pico. Anida en huecos de árboles grandes cerca de cuerpos de agua.','habitat':'Ríos, lagunas, bosques ribereños','familia':'Anatidae','entrenada':False,'audio':None},
    'Jacana americana':            {'cientifico':'Jacana jacana','descripcion':'Ave con dedos extraordinariamente largos que le permiten caminar sobre plantas flotantes. Plumaje castaño oscuro con alas amarillas llamativas en vuelo. El macho cuida los polluelos.','habitat':'Lagunas con vegetación flotante, humedales','familia':'Jacanidae','entrenada':False,'audio':None},
    'Gavilan caminero':            {'cientifico':'Rupornis magnirostris','descripcion':'El gavilán más común de los Llanos. De tamaño mediano con partes inferiores barradas. Caza lagartijas, insectos grandes y pequeños vertebrados en bordes de caminos.','habitat':'Bordes de caminos, potreros, bordes de bosque','familia':'Accipitridae','entrenada':False,'audio':None},
    'Halcon reidor':               {'cientifico':'Herpetotheres cachinnans','descripcion':'Falcón especializado en cazar serpientes. Su canto es un aullar que recuerda una risa estridente. Inconfundible por su máscara negra y corona blanca bandeada.','habitat':'Bordes de bosque, sabanas arboladas','familia':'Falconidae','entrenada':False,'audio':None},
    'Caracara crestado':           {'cientifico':'Caracara plancus','descripcion':'Falcónido oportunista que se alimenta de carroña, insectos y pequeños vertebrados. Muy visible en potreros y sabanas. Camina por el suelo con confianza.','habitat':'Sabanas, potreros, áreas abiertas','familia':'Falconidae','entrenada':False,'audio':None},
    'Condor de los Andes':         {'cientifico':'Vultur gryphus','descripcion':'El ave voladora más grande del mundo por envergadura. Buitre andino en peligro de extinción. Símbolo nacional de Colombia. Puede planear cientos de kilómetros sin batir las alas.','habitat':'Cordillera de los Andes, páramos, zonas montañosas','familia':'Cathartidae','entrenada':False,'audio':None},
    'Pava hedionda':               {'cientifico':'Opisthocomus hoazin','descripcion':'Ave prehistórica con penacho erecto y olor característico a estiércol. Los polluelos poseen garras en las alas para trepar. Una de las aves más antiguas del mundo.','habitat':'Bosques ribereños, caños, morichales','familia':'Opisthocomidae','entrenada':False,'audio':None},
    'Guacamaya azul y amarilla':   {'cientifico':'Ara ararauna','descripcion':'Una de las guacamayas más grandes y vistosas. Dorso azul brillante y pecho amarillo dorado. Se desplaza en ruidosas bandadas sobre los morichales de los Llanos.','habitat':'Morichales, bordes de bosque, sabanas arboladas','familia':'Psittacidae','entrenada':False,'audio':None},
    'Loro real':                   {'cientifico':'Amazona amazonica','descripcion':'Loro verde de tamaño mediano con manchas amarillas y rojas en las alas. Muy vocal al amanecer y atardecer. Vive en grupos ruidosos que recorren los morichales.','habitat':'Morichales, bordes de bosque, palmas','familia':'Psittacidae','entrenada':False,'audio':None},
    'Carpintero real':             {'cientifico':'Melanerpes rubricapillus','descripcion':'Carpintero de corona roja con dorso barrado blanco y negro. El más común de los Llanos. Muy activo y vocaliza frecuentemente desde postes y ramas secas.','habitat':'Bordes de bosque, árboles aislados, jardines','familia':'Picidae','entrenada':False,'audio':None},
    'Tucan pechiblanco':           {'cientifico':'Ramphastos tucanus','descripcion':'Tucán grande con pico naranja-rojo llamativo y pecho blanco. Su canto repetitivo y sonoro es muy característico de los bosques húmedos del Meta amazónico.','habitat':'Bosques húmedos, bordes de selva','familia':'Ramphastidae','entrenada':False,'audio':None},
    'Martin pescador':             {'cientifico':'Megaceryle torquata','descripcion':'El martín pescador más grande de América con corona gris jaspeada. Caza peces zambulléndose desde una percha sobre el agua. Vuelo rápido y directo a lo largo de ríos.','habitat':'Ríos, caños, lagunas','familia':'Alcedinidae','entrenada':False,'audio':None},
    'Martin pescador amazonico':   {'cientifico':'Chloroceryle amazona','descripcion':'Martín pescador de tamaño mediano con dorso verde metálico y pecho rufo. Frecuente en ríos y caños de la Amazonia y los Llanos del Meta.','habitat':'Ríos, caños, quebradas','familia':'Alcedinidae','entrenada':False,'audio':None},
    'Tangara azuleja':             {'cientifico':'Thraupis episcopus','descripcion':'Tangara de coloración azul-grisácea muy común y conspicua en los Llanos. Frecuenta jardines, bordes de bosque y árboles frutales. Se adapta bien a ambientes urbanos.','habitat':'Jardines, bordes de bosque, árboles frutales','familia':'Thraupidae','entrenada':False,'audio':None},
    'Tangara palma':               {'cientifico':'Thraupis palmarum','descripcion':'Tangara verde oliva fuertemente asociada a las palmas moriche. Muy común en los morichales de los Llanos. Se alimenta de frutos de palma y néctar.','habitat':'Palmas, morichales, áreas arboladas','familia':'Thraupidae','entrenada':False,'audio':None},
    'Canario de los llanos':       {'cientifico':'Sicalis flaveola','descripcion':'Pequeño pinzón amarillo brillante muy común en los Llanos. El macho luce un colorido amarillo intenso. Forma grandes bandadas en pastizales y sabanas.','habitat':'Pastizales, sabanas, áreas agrícolas, jardines','familia':'Thraupidae','entrenada':False,'audio':None},
    'Pico de plata':               {'cientifico':'Ramphocelus carbo','descripcion':'Tangara negra con mandíbula inferior plateada brillante en el macho. Ave común en bordes de bosque y matorrales cerca del agua. Muy sociable y activa.','habitat':'Bordes de bosque, matorrales, riberas','familia':'Thraupidae','entrenada':False,'audio':None},
    'Turpial':                     {'cientifico':'Icterus icterus','descripcion':'Ave representativa de los Llanos colombo-venezolanos. Plumaje naranja brillante con alas y cola negras. Su canto melodioso es uno de los más bellos de los Llanos.','habitat':'Sabanas, bordes de bosque, jardines, morichales','familia':'Icteridae','entrenada':False,'audio':None},
    'Chamon parasito':             {'cientifico':'Molothrus bonariensis','descripcion':'Pájaro parásito de nido que deposita sus huevos en nidos de otras especies. El macho es negro iridiscente y la hembra café opaco. Muy común en potreros.','habitat':'Potreros, jardines, áreas abiertas','familia':'Icteridae','entrenada':False,'audio':None},
    'Garrapatero':                 {'cientifico':'Crotophaga ani','descripcion':'Cucú completamente negro con pico comprimido y alto muy distinctive. Se mueve en grupos familiares y se alimenta de insectos, garrapatas y pequeños reptiles.','habitat':'Potreros, pastizales, bordes de caminos','familia':'Cuculidae','entrenada':False,'audio':None},
    'Cuco ardilla':                {'cientifico':'Piaya cayana','descripcion':'Cucú grande con larga cola rufa y pico verde-amarillo. Solitario y sigiloso, se mueve lentamente entre el follaje buscando orugas, insectos y pequeños lagartos.','habitat':'Bordes de bosque, matorrales, jardines','familia':'Cuculidae','entrenada':False,'audio':None},
    'Chotacabras comun':           {'cientifico':'Nyctidromus albicollis','descripcion':'Ave nocturna críptica de plumaje moteado que descansa en el suelo durante el día. Caza insectos en vuelo al anochecer. Sus ojos brillan rojo en la luz artificial.','habitat':'Bordes de bosque, potreros, claros','familia':'Caprimulgidae','entrenada':False,'audio':None},
    'Golondrina comun':            {'cientifico':'Hirundo rustica','descripcion':'Golondrina pequeña con dorso azul iridiscente y vientre blanco inmaculado. Muy ágil en vuelo. Una de las golondrinas más comunes sobre áreas abiertas de los Llanos.','habitat':'Áreas abiertas, sabanas, ríos, cuerpos de agua','familia':'Hirundinidae','entrenada':False,'audio':None},
    'Golondrina de rio':           {'cientifico':'Stelgidopteryx ruficollis','descripcion':'Golondrina de garganta rufa y dorso pardo oscuro. Anida en taludes de tierra arcillosa junto a ríos. Muy común sobre ríos y caños de los Llanos.','habitat':'Ríos, lagunas, taludes, barrancos','familia':'Hirundinidae','entrenada':False,'audio':None},
    'Hormiguero':                  {'cientifico':'Thamnophilus doliatus','descripcion':'Thamnofílido con marcado dimorfismo sexual. El macho está barrado en blanco y negro; la hembra es parda con rayas. Habita en matorrales densos y espinosos.','habitat':'Matorrales, bordes de bosque, jardines','familia':'Thamnophilidae','entrenada':False,'audio':None},
    'Saltarin cola de alambre':    {'cientifico':'Pipra filicauda','descripcion':'Pequeña ave del sotobosque amazónico. El macho negro y rojo posee dos filamentos en la cola. Realiza despliegues de cortejo elaborados en asambleas de machos.','habitat':'Sotobosque de bosques húmedos','familia':'Pipridae','entrenada':False,'audio':None},
    'Gallito de cienaga':          {'cientifico':'Porphyrio martinica','descripcion':'Ralo de coloración azul violáceo con escudo frontal rojo y dedos muy largos. Camina sobre vegetación flotante con gran habilidad. Muy colorido y conspicuo.','habitat':'Humedales, lagunas con vegetación flotante','familia':'Rallidae','entrenada':False,'audio':None},
    'Trepatroncos':                {'cientifico':'Xiphorhynchus susurrans','descripcion':'Furnárido trepador que recorre los troncos en espiral hacia arriba buscando artrópodos en la corteza. Plumaje pardo con manchas pálidas en cabeza y pecho.','habitat':'Bosques, bordes de bosque, plantaciones','familia':'Furnariidae','entrenada':False,'audio':None},
    'Cucarachero':                 {'cientifico':'Troglodytes aedon','descripcion':'Pequeño troglodítido de cola corta que lleva alzada. Voz muy potente para su tamaño. Muy activo y curioso, frecuenta jardines y matorrales cerca de viviendas.','habitat':'Jardines, matorrales, bordes de bosque, viviendas','familia':'Troglodytidae','entrenada':False,'audio':None},
    'Sinsonte':                    {'cientifico':'Mimus gilvus','descripcion':'Mimido de canto variado que imita a otras aves con maestría. Plumaje gris parduzco con partes inferiores blancas. Canta desde perchas altas al amanecer y al atardecer.','habitat':'Jardines, potreros, sabanas arboladas','familia':'Mimidae','entrenada':False,'audio':None},
    'Aguila pescadora':            {'cientifico':'Pandion haliaetus','descripcion':'Rapaz migratoria especializada en la pesca. Captura peces con sus garras zambulléndose de gran altura. Visitante de temporada en ríos y lagunas del Meta.','habitat':'Ríos, lagunas, embalses','familia':'Pandionidae','entrenada':False,'audio':None},
    'Pato cuervo':                 {'cientifico':'Nannopterum brasilianus','descripcion':'Cormorán completamente negro que seca sus alas extendidas sobre rocas o ramas después de nadar. Pesca sumergiéndose en ríos y lagunas de los Llanos.','habitat':'Ríos, lagunas, embalses, playas','familia':'Phalacrocoracidae','entrenada':False,'audio':None},
}

HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>CÓNDOR — Sistema IA Aves</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --gold:#7B5C0A;--gold2:#C9A84C;--gold3:#E8C870;
  --text:#1C1912;--muted:#6A6258;--muted2:#9A9288;
  --green:#1A6B5A;--orange:#B05020;
  --glass:rgba(255,255,255,.82);
  --glass-border:rgba(255,255,255,.65);
  --shadow:0 4px 24px rgba(0,0,0,.10),0 1px 4px rgba(0,0,0,.06);
  --shadow-lg:0 12px 48px rgba(0,0,0,.15),0 2px 8px rgba(0,0,0,.07);
}
html,body{height:100%;overflow:hidden;font-family:Georgia,serif}

/* ── FONDO FIJO SIEMPRE ───────────────────────────────────── */
body{
  background:linear-gradient(180deg,
    #8AB8D8 0%,#A8CDE8 18%,#C8E0F2 38%,
    #DDF0F8 55%,#EAF3F5 70%,#EDE8DF 100%);
}
#mtn-bg{
  position:fixed;bottom:0;left:0;width:100%;height:58%;
  z-index:0;pointer-events:none;
}
#mtn-bg svg{width:100%;height:100%}

/* ── PAGES ───────────────────────────────────────────────── */
.page{
  position:fixed;inset:0;z-index:1;
  display:none;opacity:0;transition:opacity .5s;
  flex-direction:column;background:transparent;
}
.page.active{display:flex;opacity:1}

/* ══ LANDING ════════════════════════════════════════════════ */
#landing{align-items:center;justify-content:center}

.l-content{
  position:relative;z-index:2;text-align:center;
  /* push content up so it floats above mountains */
  margin-bottom:28%;
}
.l-title{
  font-size:clamp(50px,9vw,84px);font-weight:700;
  letter-spacing:20px;color:#2A1E08;
  text-shadow:0 2px 30px rgba(123,92,10,.2),0 0 80px rgba(255,255,255,.4);
  margin-bottom:10px;
}
.l-sub{
  font-size:13px;letter-spacing:4px;color:#5A4A30;
  text-transform:uppercase;margin-bottom:5px;font-family:'Segoe UI',sans-serif;
}
.l-uni{
  font-size:11px;letter-spacing:2px;color:#8A7A60;
  margin-bottom:40px;font-family:'Segoe UI',sans-serif;
}
.btn-enter{
  background:linear-gradient(135deg,#7B5C0A,#4A3608);
  color:#F5DFA0;border:none;padding:15px 52px;
  font-size:12px;font-weight:700;letter-spacing:4px;
  text-transform:uppercase;font-family:'Segoe UI',sans-serif;
  cursor:pointer;transition:all .3s;
  clip-path:polygon(10px 0,100% 0,calc(100% - 10px) 100%,0 100%);
  box-shadow:0 6px 30px rgba(123,92,10,.4),0 2px 8px rgba(0,0,0,.2);
}
.btn-enter:hover{transform:translateY(-3px);box-shadow:0 10px 40px rgba(123,92,10,.55)}
.l-ver{
  position:absolute;bottom:12px;left:50%;transform:translateX(-50%);
  font-size:10px;color:rgba(100,88,68,.6);letter-spacing:2px;
  font-family:'Segoe UI',sans-serif;z-index:2;
}

/* ══ APP ════════════════════════════════════════════════════ */
#app{overflow:hidden}
.hdr{
  background:rgba(255,255,255,.88);
  backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);
  height:54px;display:flex;align-items:center;gap:14px;padding:0 20px;
  border-bottom:2px solid rgba(201,168,76,.5);
  box-shadow:0 2px 20px rgba(0,0,0,.08);
  flex-shrink:0;position:relative;z-index:10;
}
.btn-back{
  background:rgba(255,255,255,.6);border:1px solid rgba(201,168,76,.4);
  color:var(--muted);padding:6px 12px;border-radius:3px;cursor:pointer;
  font-size:11px;letter-spacing:1px;font-family:'Segoe UI',sans-serif;
  transition:all .2s;backdrop-filter:blur(4px);
}
.btn-back:hover{border-color:var(--gold);color:var(--gold)}
.h-logo{font-size:17px;font-weight:700;letter-spacing:7px;color:var(--gold)}
.h-tabs{margin-left:auto;display:flex;gap:2px}
.tab{
  background:none;border:none;color:var(--muted);
  padding:8px 16px;cursor:pointer;font-size:11px;
  font-family:'Segoe UI',sans-serif;letter-spacing:1px;
  border-bottom:2px solid transparent;transition:all .2s;
}
.tab:hover{color:var(--gold)}
.tab.active{color:var(--gold);border-bottom-color:var(--gold);font-weight:700}

/* ── SECTIONS ── */
.app-body{flex:1;overflow-y:auto;overflow-x:hidden;position:relative;z-index:2}
.sec{display:none;padding:20px;animation:fadeUp .3s ease}
.sec.active{display:block}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

.sec-titulo{
  font-size:10px;letter-spacing:3px;color:var(--muted);
  text-transform:uppercase;font-family:'Segoe UI',sans-serif;
  margin-bottom:18px;padding-bottom:10px;
  border-bottom:1px solid rgba(0,0,0,.08);
  display:flex;align-items:center;justify-content:space-between;
}
.sec-count{
  background:var(--gold);color:#fff;
  padding:2px 10px;border-radius:10px;font-size:10px;font-weight:700;
}

/* ── GRIDS ── */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.card{
  background:var(--glass);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid var(--glass-border);
  border-radius:10px;overflow:hidden;cursor:pointer;
  transition:all .3s;box-shadow:var(--shadow);
  position:relative;
}
.card:hover{
  transform:translateY(-5px);
  box-shadow:var(--shadow-lg);
  border-color:rgba(201,168,76,.5);
  background:rgba(255,255,255,.92);
}
.card:hover .c-arrow{color:var(--gold);transform:translateX(4px)}
.c-hero{
  height:140px;display:flex;align-items:center;
  justify-content:center;position:relative;overflow:hidden;
}
.c-emoji{font-size:52px;position:relative;z-index:1;filter:drop-shadow(0 4px 10px rgba(0,0,0,.2))}
.c-body{padding:14px}
.c-nom{font-size:14px;font-weight:700;color:var(--text);margin-bottom:3px}
.c-cient{font-size:11px;color:var(--muted);font-style:italic;margin-bottom:10px;font-family:'Segoe UI',sans-serif}
.c-foot{display:flex;align-items:center;justify-content:space-between}
.c-tag{
  display:inline-block;padding:3px 9px;border-radius:2px;
  font-size:10px;font-family:'Segoe UI',sans-serif;font-weight:600;
}
.c-arrow{font-size:14px;color:var(--muted2);transition:all .2s}
.c-det-count{
  position:absolute;top:10px;right:10px;
  background:rgba(123,92,10,.88);color:#F5DFA0;
  padding:3px 8px;border-radius:10px;
  font-size:10px;font-weight:700;font-family:'Segoe UI',sans-serif;
}
.badge-ent{
  position:absolute;top:10px;left:10px;
  background:rgba(26,107,90,.88);color:#B0F0E0;
  padding:2px 7px;border-radius:3px;
  font-size:9px;font-weight:700;font-family:'Segoe UI',sans-serif;letter-spacing:1px;
}

/* ── VACIO ── */
.vacio{text-align:center;padding:48px 20px;color:var(--muted);font-family:'Segoe UI',sans-serif;font-size:14px}
.vacio-icon{font-size:44px;margin-bottom:12px;opacity:.35}
.vacio-msg{margin-bottom:6px}
.vacio-sub{font-size:12px;color:var(--muted2)}

/* ── MODAL ── */
.overlay{
  position:fixed;inset:0;
  background:rgba(20,16,8,.65);
  z-index:200;display:none;align-items:center;justify-content:center;
  padding:16px;backdrop-filter:blur(10px);
}
.overlay.open{display:flex;animation:fadeUp .2s ease}
.modal{
  background:rgba(255,255,255,.96);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border:1px solid rgba(255,255,255,.8);
  border-radius:12px;width:100%;max-width:660px;max-height:92vh;
  overflow-y:auto;box-shadow:0 32px 100px rgba(0,0,0,.2);
  animation:modalIn .3s cubic-bezier(.34,1.4,.64,1);
}
@keyframes modalIn{from{opacity:0;transform:scale(.93) translateY(20px)}to{opacity:1;transform:scale(1) translateY(0)}}
.m-hero{height:180px;display:flex;align-items:center;justify-content:center;position:relative;border-radius:12px 12px 0 0;overflow:hidden}
.m-emoji{font-size:68px;filter:drop-shadow(0 4px 16px rgba(0,0,0,.2))}
.m-close{
  position:absolute;top:12px;right:12px;z-index:10;
  background:rgba(255,255,255,.85);border:1px solid rgba(0,0,0,.1);
  color:var(--text);width:32px;height:32px;border-radius:50%;
  cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;
  transition:all .2s;backdrop-filter:blur(4px);
}
.m-close:hover{background:#C02020;color:white;border-color:#C02020}
.m-body{padding:22px}
.m-nombre{font-size:24px;font-weight:700;color:var(--gold);margin-bottom:4px}
.m-cient{font-size:13px;color:var(--muted);font-style:italic;margin-bottom:18px;font-family:'Segoe UI',sans-serif}
.m-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.m-info{
  background:rgba(237,232,223,.7);border:1px solid rgba(0,0,0,.06);
  border-radius:6px;padding:12px;
}
.m-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;font-family:'Segoe UI',sans-serif}
.m-val{font-size:13px;color:var(--text);font-family:'Segoe UI',sans-serif;line-height:1.4}
.m-desc{font-size:14px;color:var(--muted);line-height:1.75;margin-bottom:18px;font-family:'Segoe UI',sans-serif}
.m-audio-box{
  background:rgba(237,232,223,.7);border:1px solid rgba(0,0,0,.06);
  border-radius:6px;padding:14px;margin-bottom:18px;
}
.m-audio-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;font-family:'Segoe UI',sans-serif}
audio{width:100%;height:32px}
.no-audio{font-size:12px;color:var(--muted2);text-align:center;font-family:'Segoe UI',sans-serif;padding:4px 0}
.m-dets-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;font-family:'Segoe UI',sans-serif}
.det-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid rgba(0,0,0,.06);font-family:'Segoe UI',sans-serif}
.det-hora{font-size:11px;color:var(--muted)}
.det-cnn{font-size:12px;color:var(--green);font-weight:600}
.det-rf{font-size:12px;color:var(--orange);font-weight:600}

/* ── DASHBOARD ── */
.dash-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.d-card{
  background:var(--glass);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid var(--glass-border);
  border-radius:10px;padding:18px;
  box-shadow:var(--shadow);
}
.d-h{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;font-family:'Segoe UI',sans-serif;display:flex;align-items:center;gap:7px}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s infinite;flex-shrink:0}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(26,107,90,.4)}50%{box-shadow:0 0 0 7px rgba(26,107,90,0)}}
.d-esp{font-size:20px;font-weight:700;color:var(--gold);margin-bottom:6px}
.d-hora{font-size:11px;color:var(--muted);margin-bottom:12px;font-family:'Segoe UI',sans-serif}
.m-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,.06)}
.m-inf{flex:1}
.m-lbl2{font-size:9px;color:var(--muted);font-family:'Segoe UI',sans-serif;margin-bottom:2px;letter-spacing:1px;text-transform:uppercase}
.m-nom{font-size:12px;font-weight:600;font-family:'Segoe UI',sans-serif;color:var(--text)}
.bw{width:100%;background:rgba(0,0,0,.07);border-radius:2px;height:3px;margin-top:5px}
.bf{height:3px;border-radius:2px;transition:width 1.2s ease}
.m-pct{font-size:14px;font-weight:700;margin-left:12px;font-family:'Segoe UI',sans-serif}
.badge2{display:inline-block;margin-top:11px;padding:4px 12px;border-radius:12px;font-size:10px;font-weight:700;letter-spacing:1px;font-family:'Segoe UI',sans-serif}
.b-si{background:rgba(26,107,90,.1);color:var(--green);border:1px solid rgba(26,107,90,.2)}
.b-no{background:rgba(176,80,32,.1);color:var(--orange);border:1px solid rgba(176,80,32,.2)}
.s-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.s-nom{font-size:11px;color:var(--text);width:150px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:'Segoe UI',sans-serif}
.s-bw{flex:1;background:rgba(0,0,0,.07);border-radius:2px;height:5px}
.s-bf{height:5px;border-radius:2px;background:linear-gradient(90deg,var(--gold),var(--gold3));transition:width 1.2s ease}
.s-n{font-size:11px;color:var(--gold);font-weight:700;width:22px;text-align:right;font-family:'Segoe UI',sans-serif}
.h-item{padding:11px 0;border-bottom:1px solid rgba(0,0,0,.06)}
.h-top{display:flex;justify-content:space-between;margin-bottom:4px}
.h-hora{font-size:10px;color:var(--muted);font-family:'Segoe UI',sans-serif}
.h-cnn{font-size:12px;color:var(--green);font-family:'Segoe UI',sans-serif;margin-bottom:2px}
.h-rf{font-size:12px;color:var(--orange);font-family:'Segoe UI',sans-serif}

::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:rgba(0,0,0,.04)}
::-webkit-scrollbar-thumb{background:rgba(201,168,76,.4);border-radius:2px}
@media(max-width:600px){
  .dash-grid,.m-grid{grid-template-columns:1fr}
  .h-tabs .tab{padding:8px 10px;font-size:10px}
  .l-title{letter-spacing:10px}
}
</style>
</head>
<body>

<!-- ══ FONDO MONTAÑAS FIJO (siempre visible) ════════════════ -->
<div id="mtn-bg">
  <svg viewBox="0 0 1440 400" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax slice">
    <!-- Rango lejano -->
    <path d="M-10,320 L80,215 L160,255 L255,178 L340,222 L430,158 L520,204 L610,140 L710,188 L800,130 L890,176 L975,150 L1065,196 L1150,160 L1245,202 L1335,165 L1450,208 L1450,400 L-10,400Z" fill="#C0D4E4" opacity=".75"/>
    <!-- Nieves lejanas -->
    <path d="M430,158 L454,186 L406,186Z M610,140 L638,170 L582,170Z M800,130 L830,162 L770,162Z M975,150 L998,176 L952,176Z M1150,160 L1174,186 L1126,186Z" fill="white" opacity=".92"/>
    <!-- Neblina -->
    <rect x="-10" y="292" width="1460" height="40" fill="white" opacity=".12"/>
    <!-- Rango medio -->
    <path d="M-10,368 L105,280 L205,318 L315,246 L415,290 L520,230 L620,274 L720,218 L820,262 L920,230 L1020,272 L1120,242 L1220,282 L1320,254 L1450,288 L1450,400 L-10,400Z" fill="#8AAABF"/>
    <!-- Nieves medias -->
    <path d="M520,230 L547,258 L493,258Z M720,218 L750,248 L690,248Z M920,230 L945,255 L895,255Z" fill="white" opacity=".85"/>
    <!-- Rango cercano -->
    <path d="M-10,390 L125,324 L225,358 L345,290 L445,332 L555,274 L660,316 L760,282 L870,320 L975,290 L1078,326 L1180,297 L1285,332 L1385,305 L1450,324 L1450,400 L-10,400Z" fill="#5A8098"/>
    <!-- Bosque / treeline -->
    <path d="M-10,399 C80,385 175,396 270,390 C365,384 460,396 555,390 C650,384 745,395 840,389 C935,383 1030,395 1125,389 C1220,383 1320,394 1440,388 L1440,400 L-10,400Z" fill="#2A5A32"/>
    <!-- Siluetas de árboles -->
    <g fill="#1E4826" opacity=".85">
      <path d="M38,400 L44,382 L50,400Z M76,400 L83,378 L90,400Z M128,400 L134,384 L140,400Z M175,400 L182,376 L189,400Z"/>
      <path d="M275,400 L282,380 L289,400Z M325,400 L332,376 L339,400Z M385,400 L392,382 L399,400Z"/>
      <path d="M575,400 L582,378 L589,400Z M628,400 L634,384 L640,400Z M688,400 L695,376 L702,400Z"/>
      <path d="M875,400 L882,380 L889,400Z M938,400 L945,376 L952,400Z M1005,400 L1012,382 L1019,400Z"/>
      <path d="M1195,400 L1202,380 L1209,400Z M1258,400 L1265,384 L1272,400Z M1325,400 L1332,378 L1339,400Z"/>
    </g>
  </svg>
</div>

<!-- ══ LANDING ════════════════════════════════════════════════ -->
<div id="landing" class="page active" style="display:flex">
  <div class="l-content">
    <div class="l-title">CÓNDOR</div>
    <div class="l-sub">Sistema de Identificación de Aves por IA</div>
    <div class="l-uni">Universidad de los Llanos · Ingeniería Electrónica · 2025</div>
    <button class="btn-enter" onclick="irApp()">Explorar Especies</button>
  </div>
  <div class="l-ver">v1.0 · Prototipo</div>
</div>

<!-- ══ APP ════════════════════════════════════════════════════ -->
<div id="app" class="page">
  <div class="hdr">
    <button class="btn-back" onclick="irLanding()">← Inicio</button>
    <div class="h-logo">CÓNDOR</div>
    <div class="h-tabs">
      <button class="tab active" onclick="sec('especies',this)">Especies</button>
      <button class="tab" onclick="sec('datos',this)">Datos</button>
      <button class="tab" onclick="sec('live',this)">En Vivo</button>
      <button class="tab" onclick="sec('historial',this)">Historial</button>
    </div>
  </div>
  <div class="app-body">

    <div id="s-especies" class="sec active">
      <div class="sec-titulo">
        <span>Especies Detectadas</span>
        <span class="sec-count" id="cnt-esp">0</span>
      </div>
      <div class="grid" id="g-esp"></div>
    </div>

    <div id="s-datos" class="sec">
      <div class="sec-titulo">
        <span>Catálogo — Meta / Llanos Orientales</span>
        <span class="sec-count">50</span>
      </div>
      <div class="grid" id="g-datos"></div>
    </div>

    <div id="s-live" class="sec">
      <div class="dash-grid">
        <div class="d-card">
          <div class="d-h"><span class="live-dot"></span>Última Detección</div>
          <div id="d-ult"><div class="vacio"><div class="vacio-icon">🎙️</div><div class="vacio-msg">Sin detecciones aún</div><div class="vacio-sub">Activa inferencia.py para escuchar</div></div></div>
        </div>
        <div class="d-card">
          <div class="d-h">Detecciones de Hoy</div>
          <div id="d-stats"><div class="vacio"><div class="vacio-icon">📊</div><div class="vacio-msg">Sin datos</div></div></div>
        </div>
      </div>
    </div>

    <div id="s-historial" class="sec">
      <div class="d-card">
        <div class="d-h">Registro Completo</div>
        <div id="d-hist"><div class="vacio"><div class="vacio-icon">📋</div><div class="vacio-msg">Sin detecciones</div></div></div>
      </div>
    </div>

  </div>
</div>

<!-- ══ MODAL ══════════════════════════════════════════════════ -->
<div class="overlay" id="modal" onclick="if(event.target===this)cerrar()">
  <div class="modal">
    <div class="m-hero" id="m-hero">
      <div class="m-emoji" id="m-emoji">🐦</div>
      <button class="m-close" onclick="cerrar()">✕</button>
    </div>
    <div class="m-body">
      <div class="m-nombre" id="m-nombre"></div>
      <div class="m-cient" id="m-cient"></div>
      <div class="m-grid">
        <div class="m-info"><div class="m-lbl">Hábitat</div><div class="m-val" id="m-hab"></div></div>
        <div class="m-info"><div class="m-lbl">Familia</div><div class="m-val" id="m-fam"></div></div>
        <div class="m-info"><div class="m-lbl">Detecciones hoy</div><div class="m-val" id="m-hoy"></div></div>
        <div class="m-info"><div class="m-lbl">Total detectada</div><div class="m-val" id="m-tot"></div></div>
      </div>
      <div class="m-desc" id="m-desc"></div>
      <div class="m-audio-box">
        <div class="m-audio-lbl">🔊 Canto base registrado</div>
        <div id="m-audio"></div>
      </div>
      <div class="m-dets-lbl">Detecciones recientes</div>
      <div id="m-dets"></div>
    </div>
  </div>
</div>

<script>
const ESPECIES = {{ especies_json|safe }};
const FAM={
  Trochilidae:{e:'🌿',g:'linear-gradient(135deg,#0A2015,#1A4025)',c:'#4CAF80'},
  Hirundinidae:{e:'🌊',g:'linear-gradient(135deg,#0A1828,#1A3050)',c:'#5890C8'},
  Passerellidae:{e:'🌾',g:'linear-gradient(135deg,#251508,#50280A)',c:'#C88040'},
  Tyrannidae:{e:'🌤️',g:'linear-gradient(135deg,#1A1808,#383010)',c:'#C8B840'},
  Corvidae:{e:'💜',g:'linear-gradient(135deg,#150A28,#28104A)',c:'#9870C8'},
  Ardeidae:{e:'🦢',g:'linear-gradient(135deg,#081820,#103040)',c:'#5090B8'},
  Threskiornithidae:{e:'🔴',g:'linear-gradient(135deg,#280808,#501010)',c:'#C84040'},
  Ciconiidae:{e:'⬜',g:'linear-gradient(135deg,#181818,#303030)',c:'#909090'},
  Anatidae:{e:'🦆',g:'linear-gradient(135deg,#082010,#104020)',c:'#40A060'},
  Accipitridae:{e:'🦅',g:'linear-gradient(135deg,#1A0A08,#382018)',c:'#A06040'},
  Falconidae:{e:'🦅',g:'linear-gradient(135deg,#080818,#101830)',c:'#5070A8'},
  Cathartidae:{e:'🦅',g:'linear-gradient(135deg,#100808,#281410)',c:'#C9A84C'},
  Opisthocomidae:{e:'🦜',g:'linear-gradient(135deg,#181008,#302010)',c:'#A08050'},
  Psittacidae:{e:'🦜',g:'linear-gradient(135deg,#081808,#103010)',c:'#40B840'},
  Picidae:{e:'🐦',g:'linear-gradient(135deg,#200808,#401010)',c:'#C04040'},
  Ramphastidae:{e:'🌈',g:'linear-gradient(135deg,#081818,#102828)',c:'#40A8A8'},
  Alcedinidae:{e:'🐟',g:'linear-gradient(135deg,#081028,#102048)',c:'#4060C0'},
  Thraupidae:{e:'✨',g:'linear-gradient(135deg,#1A1808,#302808)',c:'#C8A830'},
  Cuculidae:{e:'🐦',g:'linear-gradient(135deg,#101808,#202808)',c:'#709040'},
  Caprimulgidae:{e:'🌙',g:'linear-gradient(135deg,#080810,#101018)',c:'#7870A0'},
  Thamnophilidae:{e:'🐦',g:'linear-gradient(135deg,#080808,#181818)',c:'#808080'},
  Pipridae:{e:'🔴',g:'linear-gradient(135deg,#200808,#380808)',c:'#D04040'},
  Rallidae:{e:'💙',g:'linear-gradient(135deg,#080820,#101040)',c:'#4848C0'},
  Furnariidae:{e:'🐦',g:'linear-gradient(135deg,#181008,#302010)',c:'#A08040'},
  Troglodytidae:{e:'🐦',g:'linear-gradient(135deg,#201008,#381808)',c:'#B07030'},
  Mimidae:{e:'🎵',g:'linear-gradient(135deg,#181818,#282828)',c:'#A0A0A0'},
  Pandionidae:{e:'🦅',g:'linear-gradient(135deg,#081018,#101828)',c:'#4878A8'},
  Phalacrocoracidae:{e:'🐦',g:'linear-gradient(135deg,#080808,#141414)',c:'#606060'},
  Icteridae:{e:'🟠',g:'linear-gradient(135deg,#281008,#481808)',c:'#C86020'},
  Jacanidae:{e:'🐦',g:'linear-gradient(135deg,#200A08,#381408)',c:'#C07040'},
  Strigidae:{e:'🦉',g:'linear-gradient(135deg,#1A1005,#3A2808)',c:'#D4A843'},
};
function getCfg(nom){
  const d=ESPECIES[nom];
  if(!d) return{e:'🐦',g:'linear-gradient(135deg,#181410,#282018)',c:'#C9A84C'};
  return FAM[d.familia]||{e:'🐦',g:'linear-gradient(135deg,#181410,#282018)',c:'#C9A84C'};
}

function showPage(id){
  document.querySelectorAll('.page').forEach(p=>{p.style.display='none';p.classList.remove('active')});
  const p=document.getElementById(id);p.style.display='flex';
  setTimeout(()=>p.classList.add('active'),10);
}
function irApp(){showPage('app');cargarEsp();buildDatos()}
function irLanding(){showPage('landing')}
function sec(id,btn){
  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('s-'+id).classList.add('active');btn.classList.add('active');
  if(id==='live'||id==='historial') fetchDash();
  if(id==='especies') cargarEsp();
}

function nombreAArchivo(nom) {
    return nom.toLowerCase()
        .replace(/á/g,'a').replace(/é/g,'e').replace(/í/g,'i')
        .replace(/ó/g,'o').replace(/ú/g,'u').replace(/ñ/g,'n')
        .replace(/ /g,'_') + '.jpg';
}

function makeCard(nom, data, cfg, detCount, showEnt) {
    const c = document.createElement('div');
    c.className = 'card';
    const archivo = nombreAArchivo(nom);
    const fotoUrl = `/static/fotos/${archivo}`;

    c.innerHTML = `
        <div class="c-hero" style="background:${cfg.g}; position:relative; overflow:hidden;">
            <img src="${fotoUrl}"
     style="width:100%;height:100%;object-fit:contain;position:absolute;inset:0;opacity:0;transition:opacity .4s;padding:4px"
     onload="this.style.opacity=1"
     onerror="this.style.display='none'">
            <div class="c-emoji" style="position:relative;z-index:1;opacity:0">${cfg.e}</div>
            ${detCount > 0 ? `<div class="c-det-count">${detCount} det.</div>` : ''}
            ${showEnt && data.entrenada ? '<div class="badge-ent">IA</div>' : ''}
        </div>
        <div class="c-body">
            <div class="c-nom">${nom}</div>
            <div class="c-cient">${data.cientifico}</div>
            <div class="c-foot">
                <span class="c-tag" style="background:${cfg.c}18;color:${cfg.c};border:1px solid ${cfg.c}28">${data.familia}</span>
                <span class="c-arrow">→</span>
            </div>
        </div>`;
    c.onclick = () => abrirModal(nom, data, cfg);
    return c;
}


function cargarEsp(){
  fetch('/api/especies-detectadas').then(r=>r.json()).then(lista=>{
    const g=document.getElementById('g-esp');g.innerHTML='';
    document.getElementById('cnt-esp').textContent=lista.length;
    if(!lista.length){
      g.innerHTML=`<div class="vacio" style="grid-column:1/-1"><div class="vacio-icon">🎙️</div><div class="vacio-msg">Ninguna especie detectada aún</div><div class="vacio-sub">Ejecuta inferencia.py para comenzar</div></div>`;
      return;
    }
    lista.forEach(item=>{
      const d=ESPECIES[item.especie];if(!d)return;
      g.appendChild(makeCard(item.especie,d,getCfg(item.especie),item.total,true));
    });
  });
}

function buildDatos(){
  const g=document.getElementById('g-datos');if(g.children.length>0)return;
  Object.entries(ESPECIES).forEach(([nom,d])=>g.appendChild(makeCard(nom,d,getCfg(nom),0,true)));
}

function abrirModal(nom,data,cfg){
  const mHero = document.getElementById('m-hero');
  mHero.style.background = cfg.g;
  const fotoExistente = mHero.querySelector('img.m-foto');
  if (fotoExistente) fotoExistente.remove();
  const mFoto = document.createElement('img');
  mFoto.className = 'm-foto';
  mFoto.src = `/static/fotos/${nombreAArchivo(nom)}`;
  mFoto.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .5s;z-index:0;padding:8px';
  mFoto.onload = () => mFoto.style.opacity = '1';
  mHero.insertBefore(mFoto, mHero.firstChild);
  document.getElementById('m-emoji').textContent=cfg.e;
  document.getElementById('m-nombre').textContent=nom;
  document.getElementById('m-cient').textContent=data.cientifico;
  document.getElementById('m-hab').textContent=data.habitat;
  document.getElementById('m-fam').textContent=data.familia+(data.entrenada?' · Modelo IA':'');
  document.getElementById('m-desc').textContent=data.descripcion;
  document.getElementById('m-hoy').textContent='Cargando...';
  document.getElementById('m-tot').textContent='Cargando...';
  document.getElementById('m-dets').innerHTML='';
  document.getElementById('m-audio').innerHTML=data.audio
    ?`<audio controls src="${data.audio}"></audio>`
    :`<div class="no-audio">Audio no disponible aún</div>`;
  fetch('/api/especie/'+encodeURIComponent(nom)).then(r=>r.json()).then(d=>{
    document.getElementById('m-hoy').textContent=d.hoy+(d.hoy===1?' detección':' detecciones');
    document.getElementById('m-tot').textContent=d.total+' en total';
    document.getElementById('m-dets').innerHTML=!d.recientes.length
      ?'<div class="vacio" style="padding:16px 0"><div class="vacio-msg">Sin detecciones de esta especie</div></div>'
      :d.recientes.map(r=>`<div class="det-row"><span class="det-hora">${r.fecha} · ${r.hora}</span><span class="det-cnn">CNN ${parseFloat(r.confianza_cnn).toFixed(1)}%</span><span class="det-rf">RF ${parseFloat(r.confianza_rf).toFixed(1)}%</span></div>`).join('');
  });
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow='hidden';
}
function cerrar(){document.getElementById('modal').classList.remove('open');document.body.style.overflow=''}

function fetchDash(){
  fetch('/api/datos').then(r=>r.json()).then(d=>{rUlt(d.ultima);rStats(d.estadisticas);rHist(d.historial)});
}
function rUlt(d){
  const div=document.getElementById('d-ult');
  if(!d){div.innerHTML='<div class="vacio"><div class="vacio-icon">🎙️</div><div class="vacio-msg">Sin detecciones</div></div>';return}
  const co=d.coinciden===1;
  div.innerHTML=`<div class="d-esp">${d.especie_cnn.split(' - ')[0]}</div>
    <div class="d-hora">${d.fecha} · ${d.hora}</div>
    <div class="m-row"><div class="m-inf"><div class="m-lbl2">CNN · Transfer Learning</div><div class="m-nom">${d.especie_cnn.split(' - ')[0]}</div><div class="bw"><div class="bf" style="width:${parseFloat(d.confianza_cnn).toFixed(0)}%;background:var(--green)"></div></div></div><div class="m-pct" style="color:var(--green)">${parseFloat(d.confianza_cnn).toFixed(1)}%</div></div>
    <div class="m-row"><div class="m-inf"><div class="m-lbl2">Random Forest</div><div class="m-nom">${d.especie_rf.split(' - ')[0]}</div><div class="bw"><div class="bf" style="width:${parseFloat(d.confianza_rf).toFixed(0)}%;background:var(--orange)"></div></div></div><div class="m-pct" style="color:var(--orange)">${parseFloat(d.confianza_rf).toFixed(1)}%</div></div>
    <span class="badge2 ${co?'b-si':'b-no'}">${co?'✓ Coinciden':'⚡ Difieren'}</span>`;
}
function rStats(s){
  const div=document.getElementById('d-stats');
  if(!s||!s.length){div.innerHTML='<div class="vacio"><div class="vacio-icon">📊</div><div class="vacio-msg">Sin datos hoy</div></div>';return}
  const mx=s[0].total;
  div.innerHTML=s.map(r=>`<div class="s-row"><div class="s-nom">${r.especie.split(' - ')[0]}</div><div class="s-bw"><div class="s-bf" style="width:${(r.total/mx*100).toFixed(0)}%"></div></div><div class="s-n">${r.total}</div></div>`).join('');
}
function rHist(h){
  const div=document.getElementById('d-hist');
  if(!h||!h.length){div.innerHTML='<div class="vacio"><div class="vacio-icon">📋</div><div class="vacio-msg">Sin detecciones</div></div>';return}
  div.innerHTML=h.map(r=>{const co=r.coinciden===1;return`<div class="h-item"><div class="h-top"><span class="h-hora">${r.fecha} · ${r.hora}</span><span class="badge2 ${co?'b-si':'b-no'}" style="padding:2px 8px;font-size:9px">${co?'Coinciden':'Difieren'}</span></div><div class="h-cnn">CNN: ${r.especie_cnn.split(' - ')[0]} · ${parseFloat(r.confianza_cnn).toFixed(1)}%</div><div class="h-rf">RF: ${r.especie_rf.split(' - ')[0]} · ${parseFloat(r.confianza_rf).toFixed(1)}%</div></div>`;}).join('');
}
setInterval(()=>{if(['s-live','s-historial'].some(id=>document.getElementById(id).classList.contains('active')))fetchDash()},8000);

document.getElementById('landing').style.display='flex';
document.getElementById('app').style.display='none';
</script>
</body>
</html>'''

def get_db():
    conn = sqlite3.connect(RUTA_DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template_string(HTML, especies_json=json.dumps(ESPECIES, ensure_ascii=False))

@app.route('/api/datos')
def datos():
    conn = get_db()
    ultima = conn.execute('SELECT * FROM detecciones ORDER BY id DESC LIMIT 1').fetchone()
    hoy = datetime.now().strftime('%Y-%m-%d')
    stats = conn.execute('SELECT especie_cnn as especie,COUNT(*) as total FROM detecciones WHERE fecha=? GROUP BY especie_cnn ORDER BY total DESC',(hoy,)).fetchall()
    hist = conn.execute('SELECT * FROM detecciones ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify({'ultima':dict(ultima) if ultima else None,'estadisticas':[dict(r) for r in stats],'historial':[dict(r) for r in hist]})

@app.route('/api/especie/<nombre>')
def especie_api(nombre):
    conn = get_db()
    hoy = datetime.now().strftime('%Y-%m-%d')
    h = conn.execute('SELECT COUNT(*) as n FROM detecciones WHERE especie_cnn LIKE ? AND fecha=?',(f'%{nombre}%',hoy)).fetchone()['n']
    t = conn.execute('SELECT COUNT(*) as n FROM detecciones WHERE especie_cnn LIKE ?',(f'%{nombre}%',)).fetchone()['n']
    r = conn.execute('SELECT * FROM detecciones WHERE especie_cnn LIKE ? ORDER BY id DESC LIMIT 10',(f'%{nombre}%',)).fetchall()
    conn.close()
    return jsonify({'hoy':h,'total':t,'recientes':[dict(x) for x in r]})

@app.route('/api/especies-detectadas')
def especies_detectadas():
    conn = get_db()
    r = conn.execute('SELECT especie_cnn as especie,COUNT(*) as total FROM detecciones GROUP BY especie_cnn ORDER BY total DESC').fetchall()
    conn.close()
    return jsonify([dict(x) for x in r])

from flask import send_from_directory

@app.route('/static/fotos/<path:filename>')
def fotos(filename):
    return send_from_directory('/home/juan/sistema_aves/static/fotos', filename)

if __name__ == '__main__':
    print('CÓNDOR → http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)



