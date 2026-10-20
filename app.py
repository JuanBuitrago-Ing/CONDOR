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
    'Gorrión Pectoral':            {'cientifico':'Arremon taciturnus','descripcion':'Ave terrestre de hábitos discretos con pecho negro y dorso oliváceo muy característicos. Habita en el sotobosque denso y bordes de selva. Su canto suave y melodioso es típico del amanecer en los Llanos.','habitat':'Sotobosque, bordes de selva','familia':'Passerellidae','entrenada':True,'audio':None},
    'Mango gorjinegro':            {'cientifico':'Anthracothorax nigricollis','descripcion':'Colibrí robusto y llamativo con garganta negra iridiscente y dorso verde brillante. Uno de los colibríes más comunes de los Llanos. Defiende activamente sus territorios de alimentación frente a otras aves.','habitat':'Áreas abiertas, jardines, bordes de bosque','familia':'Trochilidae','entrenada':True,'audio':None},
    'Mosquerito ojiblanco':        {'cientifico':'Atalotriccus pilaris','descripcion':'Pequeño atrapamoscas con anillo ocular blanco muy característico y plumaje grisáceo. Habita en zonas áridas y matorrales secos de los Llanos. Captura insectos en cortos vuelos desde perchas expuestas.','habitat':'Matorrales secos, zonas áridas','familia':'Tyrannidae','entrenada':True,'audio':None},
    'Tecolote llanero':            {'cientifico':'Athene cunicularia','descripcion':'Búho pequeño de hábitos diurnos que anida en madrigueras en el suelo. Muy característico de las sabanas abiertas colombianas. Se observa parado en postes, termiteros y montículos de tierra al atardecer.','habitat':'Sabanas abiertas, pastizales, campos de cultivo','familia':'Strigidae','entrenada':True,'audio':None},
    'Urraca violácea':             {'cientifico':'Cyanocorax violaceus','descripcion':'Córvido de colores llamativos con plumaje azul violáceo y negro. Ave muy social y ruidosa que se mueve en grupos familiares bulliciosos. Muy inteligente y omnívora, común en bordes de bosque de los Llanos.','habitat':'Bordes de bosque, áreas arboladas, sabanas','familia':'Corvidae','entrenada':True,'audio':None},
    # ── 43 CATÁLOGO META / LLANOS ORIENTALES ─────────────────
    'Bichofué':                    {'cientifico':'Pitangus sulphuratus','descripcion':'Tiránido grande y ruidoso de pecho amarillo brillante y corona roja oculta. Muy común y territorial. Su canto "bichofué" le da el nombre popular. Omnívoro y oportunista.','habitat':'Áreas abiertas, jardines, orillas de ríos, potreros','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Sirirí común':                {'cientifico':'Tyrannus melancholicus','descripcion':'Tiránido esbelto con corona naranja oculta. Se posa en lo alto de árboles y postes desde donde caza insectos en vuelo. Muy común en los Llanos durante todo el año.','habitat':'Áreas abiertas, bordes de bosque, potreros','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Tijereta':                    {'cientifico':'Tyrannus savana','descripcion':'Ave inconfundible por su cola extremadamente larga en forma de tijera en el macho. Abundante en sabanas abiertas de los Llanos. Migratoria austral, presente en verano.','habitat':'Sabanas abiertas, potreros, áreas agrícolas','familia':'Tyrannidae','entrenada':False,'audio':None},
    'Garza del ganado':            {'cientifico':'Bubulcus ibis','descripcion':'Garza blanca de talla mediana frecuentemente asociada al ganado bovino. Forrajea insectos y pequeños animales ahuyentados por los bovinos al caminar. Muy común en todo el Meta.','habitat':'Potreros, pastizales, áreas agrícolas','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garza blanca':                {'cientifico':'Ardea alba','descripcion':'La garza blanca más grande. Plumaje completamente blanco con pico amarillo largo. Habita en humedales, ríos y lagunas. En época de cría desarrolla plumas nupciales muy vistosas.','habitat':'Humedales, ríos, lagunas, arrozales','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garzón azul':                 {'cientifico':'Ardea cocoi','descripcion':'La garza más grande de Suramérica con plumaje gris azulado y corona negra. Solitaria y de hábitos acuáticos, caza peces con paciencia en orillas de ríos y lagunas.','habitat':'Ríos, lagunas, humedales, playas','familia':'Ardeidae','entrenada':False,'audio':None},
    'Garza tigre':                 {'cientifico':'Tigrisoma lineatum','descripcion':'Garza robusta con marcado patrón bandeado en el cuello. De hábitos sigilosos y crepusculares, se camufla perfectamente entre la vegetación ribereña densa.','habitat':'Ríos, caños, bosques de galería','familia':'Ardeidae','entrenada':False,'audio':None},
    'Corocoro colorado':           {'cientifico':'Eudocimus ruber','descripcion':'Ibis de plumaje rojo carmesí brillante, uno de los más emblemáticos del Meta. Se congrega en grandes colonias en los morichales. Su color viene de los carotenoides de su dieta.','habitat':'Humedales, morichales, sabanas inundables','familia':'Threskiornithidae','entrenada':False,'audio':None},
    'Espátula rosada':             {'cientifico':'Platalea ajaja','descripcion':'Ave de plumaje rosado intenso con pico en forma de espátula única. Filtra el agua en movimientos laterales buscando peces y crustáceos. Muy vistosa en vuelo.','habitat':'Humedales, lagunas someras, playas de río','familia':'Threskiornithidae','entrenada':False,'audio':None},
    'Gabán llanero':               {'cientifico':'Jabiru mycteria','descripcion':'La cigüeña más grande de América con cuello rojo y negro y cuerpo blanco. Símbolo icónico de los Llanos colombianos y venezolanos. Anida en la cima de los árboles más altos.','habitat':'Sabanas inundables, lagunas, morichales','familia':'Ciconiidae','entrenada':False,'audio':None},
    'Cigüeña americana':           {'cientifico':'Mycteria americana','descripcion':'Cigüeña con cabeza y cuello desnudos de color oscuro. Forrajea táctilmente en aguas someras con el pico abierto para capturar peces. Anida en colonias mixtas.','habitat':'Humedales, lagunas, ríos, esteros','familia':'Ciconiidae','entrenada':False,'audio':None},
    'Pato real':                   {'cientifico':'Cairina moschata','descripcion':'El pato más grande de Suramérica. El macho negro con manchas blancas posee carúncula roja sobre el pico. Anida en huecos de árboles grandes cerca de cuerpos de agua.','habitat':'Ríos, lagunas, bosques ribereños','familia':'Anatidae','entrenada':False,'audio':None},
    'Jacana americana':            {'cientifico':'Jacana jacana','descripcion':'Ave con dedos extraordinariamente largos que le permiten caminar sobre plantas flotantes. Plumaje castaño oscuro con alas amarillas llamativas en vuelo. El macho cuida los polluelos.','habitat':'Lagunas con vegetación flotante, humedales','familia':'Jacanidae','entrenada':False,'audio':None},
    'Gavilán caminero':            {'cientifico':'Rupornis magnirostris','descripcion':'El gavilán más común de los Llanos. De tamaño mediano con partes inferiores barradas. Caza lagartijas, insectos grandes y pequeños vertebrados en bordes de caminos.','habitat':'Bordes de caminos, potreros, bordes de bosque','familia':'Accipitridae','entrenada':False,'audio':None},

    'Halcón reidor':               {'cientifico':'Herpetotheres cachinnans','descripcion':'Falcón especializado en cazar serpientes. Su canto es un aullar que recuerda una risa estridente. Inconfundible por su máscara negra y corona blanca bandeada.','habitat':'Bordes de bosque, sabanas arboladas','familia':'Falconidae','entrenada':False,'audio':None},
    'Caracara crestado':           {'cientifico':'Caracara plancus','descripcion':'Falcónido oportunista que se alimenta de carroña, insectos y pequeños vertebrados. Muy visible en potreros y sabanas. Camina por el suelo con confianza.','habitat':'Sabanas, potreros, áreas abiertas','familia':'Falconidae','entrenada':False,'audio':None},
    'Cóndor de los Andes':         {'cientifico':'Vultur gryphus','descripcion':'El ave voladora más grande del mundo por envergadura. Buitre andino en peligro de extinción. Símbolo nacional de Colombia. Puede planear cientos de kilómetros sin batir las alas.','habitat':'Cordillera de los Andes, páramos, zonas montañosas','familia':'Cathartidae','entrenada':False,'audio':None},
    'Pava hedionda':               {'cientifico':'Opisthocomus hoazin','descripcion':'Ave prehistórica con penacho erecto y olor característico a estiércol. Los polluelos poseen garras en las alas para trepar. Una de las aves más antiguas del mundo.','habitat':'Bosques ribereños, caños, morichales','familia':'Opisthocomidae','entrenada':False,'audio':None},
    'Guacamaya azul y amarilla':   {'cientifico':'Ara ararauna','descripcion':'Una de las guacamayas más grandes y vistosas. Dorso azul brillante y pecho amarillo dorado. Se desplaza en ruidosas bandadas sobre los morichales de los Llanos.','habitat':'Morichales, bordes de bosque, sabanas arboladas','familia':'Psittacidae','entrenada':False,'audio':None},
    'Loro real':                   {'cientifico':'Amazona amazonica','descripcion':'Loro verde de tamaño mediano con manchas amarillas y rojas en las alas. Muy vocal al amanecer y atardecer. Vive en grupos ruidosos que recorren los morichales.','habitat':'Morichales, bordes de bosque, palmas','familia':'Psittacidae','entrenada':False,'audio':None},
    'Carpintero real':             {'cientifico':'Melanerpes rubricapillus','descripcion':'Carpintero de corona roja con dorso barrado blanco y negro. El más común de los Llanos. Muy activo y vocaliza frecuentemente desde postes y ramas secas.','habitat':'Bordes de bosque, árboles aislados, jardines','familia':'Picidae','entrenada':False,'audio':None},
    'Tucán pechiblanco':           {'cientifico':'Ramphastos tucanus','descripcion':'Tucán grande con pico naranja-rojo llamativo y pecho blanco. Su canto repetitivo y sonoro es muy característico de los bosques húmedos del Meta amazónico.','habitat':'Bosques húmedos, bordes de selva','familia':'Ramphastidae','entrenada':False,'audio':None},
    'Martín pescador':             {'cientifico':'Megaceryle torquata','descripcion':'El martín pescador más grande de América con corona gris jaspeada. Caza peces zambulléndose desde una percha sobre el agua. Vuelo rápido y directo a lo largo de ríos.','habitat':'Ríos, caños, lagunas','familia':'Alcedinidae','entrenada':False,'audio':None},
    'Martín pescador amazónico':   {'cientifico':'Chloroceryle amazona','descripcion':'Martín pescador de tamaño mediano con dorso verde metálico y pecho rufo. Frecuente en ríos y caños de la Amazonia y los Llanos del Meta.','habitat':'Ríos, caños, quebradas','familia':'Alcedinidae','entrenada':False,'audio':None},
    'Tangara azuleja':             {'cientifico':'Thraupis episcopus','descripcion':'Tangara de coloración azul-grisácea muy común y conspicua en los Llanos. Frecuenta jardines, bordes de bosque y árboles frutales. Se adapta bien a ambientes urbanos.','habitat':'Jardines, bordes de bosque, árboles frutales','familia':'Thraupidae','entrenada':False,'audio':None},
    'Tangara palma':               {'cientifico':'Thraupis palmarum','descripcion':'Tangara verde oliva fuertemente asociada a las palmas moriche. Muy común en los morichales de los Llanos. Se alimenta de frutos de palma y néctar.','habitat':'Palmas, morichales, áreas arboladas','familia':'Thraupidae','entrenada':False,'audio':None},
    'Canario de los llanos':       {'cientifico':'Sicalis flaveola','descripcion':'Pequeño pinzón amarillo brillante muy común en los Llanos. El macho luce un colorido amarillo intenso. Forma grandes bandadas en pastizales y sabanas.','habitat':'Pastizales, sabanas, áreas agrícolas, jardines','familia':'Thraupidae','entrenada':False,'audio':None},
    'Pico de plata':               {'cientifico':'Ramphocelus carbo','descripcion':'Tangara negra con mandíbula inferior plateada brillante en el macho. Ave común en bordes de bosque y matorrales cerca del agua. Muy sociable y activa.','habitat':'Bordes de bosque, matorrales, riberas','familia':'Thraupidae','entrenada':False,'audio':None},
    'Turpial':                     {'cientifico':'Icterus icterus','descripcion':'Ave representativa de los Llanos colombo-venezolanos. Plumaje naranja brillante con alas y cola negras. Su canto melodioso es uno de los más bellos de los Llanos.','habitat':'Sabanas, bordes de bosque, jardines, morichales','familia':'Icteridae','entrenada':False,'audio':None},
    'Chamón parásito':             {'cientifico':'Molothrus bonariensis','descripcion':'Pájaro parásito de nido que deposita sus huevos en nidos de otras especies. El macho es negro iridiscente y la hembra café opaco. Muy común en potreros.','habitat':'Potreros, jardines, áreas abiertas','familia':'Icteridae','entrenada':False,'audio':None},
    'Garrapatero':                 {'cientifico':'Crotophaga ani','descripcion':'Cucú completamente negro con pico comprimido y alto muy distinctive. Se mueve en grupos familiares y se alimenta de insectos, garrapatas y pequeños reptiles.','habitat':'Potreros, pastizales, bordes de caminos','familia':'Cuculidae','entrenada':False,'audio':None},
    'Cuco ardilla':                {'cientifico':'Piaya cayana','descripcion':'Cucú grande con larga cola rufa y pico verde-amarillo. Solitario y sigiloso, se mueve lentamente entre el follaje buscando orugas, insectos y pequeños lagartos.','habitat':'Bordes de bosque, matorrales, jardines','familia':'Cuculidae','entrenada':False,'audio':None},
    'Chotacabras común':           {'cientifico':'Nyctidromus albicollis','descripcion':'Ave nocturna críptica de plumaje moteado que descansa en el suelo durante el día. Caza insectos en vuelo al anochecer. Sus ojos brillan rojo en la luz artificial.','habitat':'Bordes de bosque, potreros, claros','familia':'Caprimulgidae','entrenada':False,'audio':None},
    'Golondrina azul y blanca':    {'cientifico':'Pygochelidon cyanoleuca','descripcion':'Golondrina pequeña con dorso azul iridiscente y vientre blanco inmaculado. Muy ágil en vuelo. Una de las golondrinas más comunes sobre áreas abiertas de los Llanos.','habitat':'Áreas abiertas, sabanas, ríos, cuerpos de agua','familia':'Hirundinidae','entrenada':False,'audio':None},
    'Golondrina de río':           {'cientifico':'Stelgidopteryx ruficollis','descripcion':'Golondrina de garganta rufa y dorso pardo oscuro. Anida en taludes de tierra arcillosa junto a ríos. Muy común sobre ríos y caños de los Llanos.','habitat':'Ríos, lagunas, taludes, barrancos','familia':'Hirundinidae','entrenada':False,'audio':None},
    'Hormiguero':                  {'cientifico':'Thamnophilus doliatus','descripcion':'Thamnofílido con marcado dimorfismo sexual. El macho está barrado en blanco y negro; la hembra es parda con rayas. Habita en matorrales densos y espinosos.','habitat':'Matorrales, bordes de bosque, jardines','familia':'Thamnophilidae','entrenada':False,'audio':None},
    'Saltarín cola de alambre':    {'cientifico':'Pipra filicauda','descripcion':'Pequeña ave del sotobosque amazónico. El macho negro y rojo posee dos filamentos en la cola. Realiza despliegues de cortejo elaborados en asambleas de machos.','habitat':'Sotobosque de bosques húmedos','familia':'Pipridae','entrenada':False,'audio':None},
    'Gallito de ciénaga':          {'cientifico':'Porphyrio martinica','descripcion':'Ralo de coloración azul violáceo con escudo frontal rojo y dedos muy largos. Camina sobre vegetación flotante con gran habilidad. Muy colorido y conspicuo.','habitat':'Humedales, lagunas con vegetación flotante','familia':'Rallidae','entrenada':False,'audio':None},
    'Trepatroncos':                {'cientifico':'Xiphorhynchus susurrans','descripcion':'Furnárido trepador que recorre los troncos en espiral hacia arriba buscando artrópodos en la corteza. Plumaje pardo con manchas pálidas en cabeza y pecho.','habitat':'Bosques, bordes de bosque, plantaciones','familia':'Furnariidae','entrenada':False,'audio':None},
    'Cucarachero':                 {'cientifico':'Troglodytes aedon','descripcion':'Pequeño troglodítido de cola corta que lleva alzada. Voz muy potente para su tamaño. Muy activo y curioso, frecuenta jardines y matorrales cerca de viviendas.','habitat':'Jardines, matorrales, bordes de bosque, viviendas','familia':'Troglodytidae','entrenada':False,'audio':None},
    'Sinsonte':                    {'cientifico':'Mimus gilvus','descripcion':'Mimido de canto variado que imita a otras aves con maestría. Plumaje gris parduzco con partes inferiores blancas. Canta desde perchas altas al amanecer y al atardecer.','habitat':'Jardines, potreros, sabanas arboladas','familia':'Mimidae','entrenada':False,'audio':None},
    'Águila pescadora':            {'cientifico':'Pandion haliaetus','descripcion':'Rapaz migratoria especializada en la pesca. Captura peces con sus garras zambulléndose de gran altura. Visitante de temporada en ríos y lagunas del Meta.','habitat':'Ríos, lagunas, embalses','familia':'Pandionidae','entrenada':False,'audio':None},
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
  --bg:#EDE8DF;--bg2:#FFFFFF;--bg3:#E4DED4;
  --border:#D0C8BC;--border2:#C0B8AC;
  --text:#1C1912;--muted:#7A7268;--muted2:#A09890;
  --gold:#7B5C0A;--gold2:#C9A84C;--gold3:#E8C870;
  --green:#1A6B5A;--orange:#B05020;
  --shadow:0 2px 16px rgba(0,0,0,.08),0 1px 4px rgba(0,0,0,.05);
  --shadow-lg:0 8px 40px rgba(0,0,0,.12),0 2px 8px rgba(0,0,0,.06);
}
html,body{height:100%;overflow-x:hidden;font-family:Georgia,serif}
body{background:var(--bg);color:var(--text)}

/* ── PAGES ── */
.page{position:fixed;inset:0;display:none;opacity:0;transition:opacity .5s;overflow:hidden}
.page.active{display:flex;flex-direction:column;opacity:1}

/* ══ LANDING ══════════════════════════════════════════════════ */
#landing{
  background:linear-gradient(180deg,#B8D4EE 0%,#D8EAF8 25%,#EAF2F8 55%,#EDE8DF 100%);
  align-items:center;justify-content:center;position:relative;
}
.mountain-wrap{position:absolute;bottom:0;left:0;width:100%;height:52%;pointer-events:none}
.mountain-wrap svg{width:100%;height:100%}
.l-content{position:relative;z-index:10;text-align:center;margin-bottom:10%}
.condor-anim{

  animation:soar 8s ease-in-out infinite;
  filter:drop-shadow(0 8px 30px rgba(0,0,0,.2));
  margin-bottom:28px;
}
@keyframes soar{
  0%,100%{transform:translateY(0) rotate(-1.5deg)}
  35%{transform:translateY(-32px) rotate(1.8deg)}
  65%{transform:translateY(-14px) rotate(-.6deg)}
}
.w-l{transform-origin:98% 52%;animation:wl 5s ease-in-out infinite}
.w-r{transform-origin:2% 52%;animation:wr 5s ease-in-out infinite}
@keyframes wl{0%,100%{transform:rotate(0)}50%{transform:rotate(5deg)}}
@keyframes wr{0%,100%{transform:rotate(0)}50%{transform:rotate(-5deg)}}
.l-title{
  font-size:clamp(48px,9vw,80px);font-weight:700;
  letter-spacing:18px;color:#3A2A08;
  text-shadow:0 2px 20px rgba(123,92,10,.25);
  margin-bottom:10px;
}
.l-sub{font-size:13px;letter-spacing:4px;color:#7A6A50;text-transform:uppercase;margin-bottom:6px;font-family:'Segoe UI',sans-serif}
.l-uni{font-size:11px;letter-spacing:2px;color:#A89878;margin-bottom:44px;font-family:'Segoe UI',sans-serif}
.btn-enter{
  background:linear-gradient(135deg,#7B5C0A,#4A3608);
  color:#F5DFA0;border:none;padding:15px 50px;
  font-size:12px;font-weight:700;letter-spacing:4px;
  text-transform:uppercase;font-family:'Segoe UI',sans-serif;
  cursor:pointer;transition:all .3s;
  clip-path:polygon(10px 0,100% 0,calc(100% - 10px) 100%,0 100%);
  box-shadow:0 6px 30px rgba(123,92,10,.35);
}
.btn-enter:hover{transform:translateY(-3px);box-shadow:0 10px 40px rgba(123,92,10,.5)}
.l-ver{position:absolute;bottom:16px;font-size:10px;color:#B8A888;letter-spacing:2px;font-family:'Segoe UI',sans-serif}


/* ══ APP ═══════════════════════════════════════════════════════ */
#app{overflow:hidden}
.hdr{
  background:var(--bg2);height:54px;
  display:flex;align-items:center;gap:14px;padding:0 20px;
  border-bottom:2px solid var(--gold2);
  box-shadow:0 2px 12px rgba(0,0,0,.08);flex-shrink:0;
  position:relative;z-index:100;
}
.btn-back{
  background:none;border:1px solid var(--border);color:var(--muted);
  padding:6px 12px;border-radius:3px;cursor:pointer;
  font-size:11px;letter-spacing:1px;font-family:'Segoe UI',sans-serif;transition:all .2s;
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
.app-body{flex:1;overflow-y:auto;overflow-x:hidden}
.sec{display:none;padding:20px;animation:fadeUp .3s ease}
.sec.active{display:block}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

.sec-titulo{
  font-size:10px;letter-spacing:3px;color:var(--muted);
  text-transform:uppercase;font-family:'Segoe UI',sans-serif;
  margin-bottom:18px;padding-bottom:10px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.sec-count{
  background:var(--gold);color:#fff;
  padding:2px 10px;border-radius:10px;font-size:10px;font-weight:700;
}

/* ── GRIDS ── */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.card{
  background:var(--bg2);border-radius:8px;overflow:hidden;
  cursor:pointer;transition:all .3s;
  box-shadow:var(--shadow);border:1px solid var(--border);
  position:relative;
}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg);border-color:var(--gold2)}
.card:hover .c-arrow{color:var(--gold);transform:translateX(3px)}
.c-hero{height:110px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.c-emoji{font-size:50px;position:relative;z-index:1;filter:drop-shadow(0 3px 8px rgba(0,0,0,.2))}
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
  background:rgba(123,92,10,.9);color:#F5DFA0;
  padding:3px 8px;border-radius:10px;
  font-size:10px;font-weight:700;font-family:'Segoe UI',sans-serif;
}
.badge-entrenada{
  position:absolute;top:10px;left:10px;
  background:rgba(26,107,90,.9);color:#B0F0E0;
  padding:2px 7px;border-radius:3px;
  font-size:9px;font-weight:700;font-family:'Segoe UI',sans-serif;letter-spacing:1px;
}

/* ── SIN DATOS ── */
.vacio{
  text-align:center;padding:50px 20px;color:var(--muted);
  font-family:'Segoe UI',sans-serif;font-size:14px;
}
.vacio-icon{font-size:48px;margin-bottom:12px;opacity:.4}
.vacio-msg{margin-bottom:8px}
.vacio-sub{font-size:12px;color:var(--muted2)}

/* ── MODAL ── */
.overlay{
  position:fixed;inset:0;background:rgba(20,16,8,.75);
  z-index:200;display:none;align-items:center;justify-content:center;
  padding:16px;backdrop-filter:blur(8px);
}
.overlay.open{display:flex;animation:fadeUp .2s ease}
.modal{
  background:var(--bg2);border-radius:10px;
  width:100%;max-width:660px;max-height:92vh;overflow-y:auto;

  box-shadow:0 24px 80px rgba(0,0,0,.25);
  animation:modalIn .3s cubic-bezier(.34,1.4,.64,1);
}
@keyframes modalIn{from{opacity:0;transform:scale(.93) translateY(20px)}to{opacity:1;transform:scale(1) translateY(0)}}
.m-hero{height:180px;display:flex;align-items:center;justify-content:center;position:relative;border-radius:10px 10px 0 0;overflow:hidden}
.m-emoji{font-size:68px;filter:drop-shadow(0 4px 16px rgba(0,0,0,.3))}
.m-close{
  position:absolute;top:12px;right:12px;z-index:10;
  background:rgba(255,255,255,.8);border:1px solid var(--border);
  color:var(--text);width:32px;height:32px;border-radius:50%;
  cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;
  transition:all .2s;backdrop-filter:blur(4px);
}
.m-close:hover{background:#C02020;color:white;border-color:#C02020}
.m-body{padding:22px}
.m-nombre{font-size:24px;font-weight:700;color:var(--gold);margin-bottom:4px}
.m-cient{font-size:13px;color:var(--muted);font-style:italic;margin-bottom:18px;font-family:'Segoe UI',sans-serif}
.m-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.m-info{background:var(--bg3);border:1px solid var(--border);border-radius:5px;padding:12px}
.m-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;font-family:'Segoe UI',sans-serif}
.m-val{font-size:13px;color:var(--text);font-family:'Segoe UI',sans-serif;line-height:1.4}
.m-desc{font-size:14px;color:var(--muted);line-height:1.75;margin-bottom:18px;font-family:'Segoe UI',sans-serif}
.m-audio-box{background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:14px;margin-bottom:18px}
.m-audio-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;font-family:'Segoe UI',sans-serif}
audio{width:100%;height:32px}
.no-audio{font-size:12px;color:var(--muted2);text-align:center;font-family:'Segoe UI',sans-serif;padding:4px 0}
.m-dets-lbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;font-family:'Segoe UI',sans-serif}
.det-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);font-family:'Segoe UI',sans-serif}
.det-hora{font-size:11px;color:var(--muted)}
.det-cnn{font-size:12px;color:var(--green);font-weight:600}
.det-rf{font-size:12px;color:var(--orange);font-weight:600}


/* ── DASHBOARD ── */
.dash-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.d-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:18px;box-shadow:var(--shadow)}
.d-h{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;font-family:'Segoe UI',sans-serif;display:flex;align-items:center;gap:7px}
.live-dot{width:7px;height:7px;border-radius:50%;background:#1A9;animation:pulse 2s infinite;flex-shrink:0}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(17,170,136,.4)}50%{box-shadow:0 0 0 7px rgba(17,170,136,0)}}
.d-esp{font-size:20px;font-weight:700;color:var(--gold);margin-bottom:6px}
.d-hora{font-size:11px;color:var(--muted);margin-bottom:12px;font-family:'Segoe UI',sans-serif}
.m-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--bg3)}
.m-inf{flex:1}
.m-lbl2{font-size:9px;color:var(--muted);font-family:'Segoe UI',sans-serif;margin-bottom:2px;letter-spacing:1px;text-transform:uppercase}
.m-nom{font-size:12px;font-weight:600;font-family:'Segoe UI',sans-serif;color:var(--text)}
.bw{width:100%;background:var(--bg3);border-radius:2px;height:3px;margin-top:5px}
.bf{height:3px;border-radius:2px;transition:width 1.2s ease}
.m-pct{font-size:14px;font-weight:700;margin-left:12px;font-family:'Segoe UI',sans-serif}
.badge2{display:inline-block;margin-top:11px;padding:4px 12px;border-radius:12px;font-size:10px;font-weight:700;letter-spacing:1px;font-family:'Segoe UI',sans-serif}
.b-si{background:rgba(26,107,90,.1);color:var(--green);border:1px solid rgba(26,107,90,.2)}
.b-no{background:rgba(176,80,32,.1);color:var(--orange);border:1px solid rgba(176,80,32,.2)}
.s-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.s-nom{font-size:11px;color:var(--text);width:150px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:'Segoe UI',sans-serif}
.s-bw{flex:1;background:var(--bg3);border-radius:2px;height:5px}
.s-bf{height:5px;border-radius:2px;background:linear-gradient(90deg,var(--gold),var(--gold3));transition:width 1.2s ease}
.s-n{font-size:11px;color:var(--gold);font-weight:700;width:22px;text-align:right;font-family:'Segoe UI',sans-serif}
.h-item{padding:11px 0;border-bottom:1px solid var(--border)}
.h-top{display:flex;justify-content:space-between;margin-bottom:4px}
.h-hora{font-size:10px;color:var(--muted);font-family:'Segoe UI',sans-serif}
.h-cnn{font-size:12px;color:var(--green);font-family:'Segoe UI',sans-serif;margin-bottom:2px}
.h-rf{font-size:12px;color:var(--orange);font-family:'Segoe UI',sans-serif}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg3)}

::-webkit-scrollbar-thumb{background:var(--gold2);border-radius:2px}

@media(max-width:600px){
  .dash-grid,.m-grid{grid-template-columns:1fr}
  .h-tabs .tab{padding:8px 10px;font-size:10px}
  .l-title{letter-spacing:10px}
}
</style>
</head>
<body>

<!-- ══ LANDING ══════════════════════════════════════════════ -->
<div id="landing" class="page active" style="display:flex">

  <!-- Condor + title -->
  <div class="l-content">
    <div class="condor-anim">
      <svg viewBox="0 0 520 230" width="440" height="194" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="260" cy="222" rx="85" ry="6" fill="rgba(60,40,10,.12)"/>
        <!-- Left wing -->
        <g class="w-l">
          <path d="M260,112 C238,95 196,73 150,59 C106,46 60,45 22,56 C8,61 0,71 4,82 C28,73 76,74 134,85 C176,93 218,103 260,112Z" fill="#2A2018"/>
          <path d="M260,112 C240,104 216,92 188,86 C207,93 233,103 260,112Z" fill="#B0A898" opacity=".5"/>
        </g>
        <!-- Right wing -->
        <g class="w-r">
          <path d="M260,112 C282,95 324,73 370,59 C414,46 460,45 498,56 C512,61 520,71 516,82 C492,73 444,74 386,85 C344,93 302,103 260,112Z" fill="#2A2018"/>
          <path d="M260,112 C280,104 304,92 332,86 C313,93 287,103 260,112Z" fill="#B0A898" opacity=".5"/>
        </g>
        <!-- Body -->
        <ellipse cx="260" cy="120" rx="40" ry="21" fill="#1A1410"/>
        <!-- Tail -->

        <path d="M242,136 C248,154 260,162 272,154 C266,140 254,136 242,136Z" fill="#2A2018"/>
        <!-- White collar -->
        <ellipse cx="274" cy="109" rx="18" ry="11" fill="#E8E4DC"/>
        <ellipse cx="272" cy="110" rx="13" ry="8" fill="#D0CCC4"/>
        <!-- Neck -->
        <ellipse cx="278" cy="100" rx="11" ry="16" fill="#6A1818"/>
        <!-- Head -->
        <circle cx="283" cy="89" r="15" fill="#8B2020"/>
        <circle cx="278" cy="85" r="7" fill="#A03030" opacity=".5"/>
        <!-- Eye -->
        <circle cx="289" cy="87" r="4.5" fill="#D89A00"/>
        <circle cx="290" cy="87" r="2.5" fill="#0A080A"/>
        <circle cx="289" cy="86" r="1" fill="white"/>
        <!-- Beak -->
        <path d="M296,89 L313,92 L296,97 C293,97 290,95 290,93 C290,91 293,89 296,89Z" fill="#C09040"/>
        <path d="M296,89 L313,92 L296,93Z" fill="#A07030"/>
        <!-- Caruncle -->
        <path d="M288,81 C295,77 299,82 296,86 C292,91 286,88 288,81Z" fill="#9B3030"/>
      </svg>
    </div>
    <div class="l-title">CÓNDOR</div>
    <div class="l-sub">Sistema de Identificación de Aves por IA</div>
    <div class="l-uni">Universidad de los Llanos · Ingeniería Electrónica · 2025</div>
    <button class="btn-enter" onclick="irApp()">Explorar Especies</button>
  </div>

  <!-- Mountain landscape -->
  <div class="mountain-wrap">
    <svg viewBox="0 0 1440 400" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax slice">
      <!-- Far range -->
      <path d="M-10,310 L80,210 L160,250 L255,175 L340,218 L430,155 L520,200 L610,138 L710,185 L800,128 L890,172 L975,148 L1065,192 L1150,158 L1245,198 L1335,162 L1450,205 L1450,400 L-10,400Z" fill="#C0D0E0" opacity=".7"/>
      <!-- Snow caps far -->

      <path d="M430,155 L452,180 L408,180Z M610,138 L636,167 L584,167Z M800,128 L828,160 L772,160Z M975,148 L997,173 L953,173Z M1150,158 L1172,183 L1128,183Z" fill="white" opacity=".9"/>
      <!-- Mist -->
      <rect x="-10" y="285" width="1460" height="35" fill="white" opacity=".15"/>
      <!-- Mid range -->
      <path d="M-10,365 L105,278 L205,315 L315,244 L415,288 L520,228 L620,272 L720,215 L820,260 L920,227 L1020,270 L1120,240 L1220,280 L1320,252 L1450,285 L1450,400 L-10,400Z" fill="#8AAABF"/>
      <!-- Snow caps mid -->
      <path d="M520,228 L545,256 L495,256Z M720,215 L748,245 L692,245Z M920,227 L943,252 L897,252Z" fill="white" opacity=".8"/>
      <!-- Near range -->
      <path d="M-10,390 L125,322 L225,355 L345,288 L445,330 L555,272 L660,314 L760,280 L870,318 L975,287 L1078,324 L1180,295 L1285,330 L1385,303 L1450,322 L1450,400 L-10,400Z" fill="#5A8098"/>
      <!-- Forest/treeline -->
      <path d="M-10,398 C80,383 175,394 270,388 C365,382 460,394 555,388 C650,382 745,393 840,387 C935,381 1030,393 1125,387 C1220,381 1320,392 1440,386 L1440,400 L-10,400Z" fill="#2A5A32"/>
      <!-- Tree silhouettes -->
      <g fill="#1E4826" opacity=".8">
        <path d="M40,398 L46,380 L52,398Z M80,398 L87,376 L94,398Z M130,398 L136,382 L142,398Z"/>
        <path d="M280,398 L287,374 L294,398Z M330,398 L337,380 L344,398Z"/>
        <path d="M580,398 L587,376 L594,398Z M630,398 L636,382 L642,398Z"/>
        <path d="M880,398 L887,378 L894,398Z M940,398 L947,374 L954,398Z"/>
        <path d="M1200,398 L1207,378 L1214,398Z M1260,398 L1267,382 L1274,398Z"/>
      </g>
    </svg>
  </div>
  <div class="l-ver">v1.0 · Prototipo</div>
</div>

<!-- ══ APP ═══════════════════════════════════════════════════ -->
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

    <!-- ESPECIES: solo detectadas -->
    <div id="s-especies" class="sec active">
      <div class="sec-titulo">
        <span>Especies Detectadas</span>
        <span class="sec-count" id="cnt-esp">0</span>
      </div>
      <div class="grid" id="g-esp"></div>
    </div>

    <!-- DATOS: catálogo completo -->
    <div id="s-datos" class="sec">
      <div class="sec-titulo">
        <span>Catálogo de Especies — Meta / Llanos Orientales</span>
        <span class="sec-count">50</span>
      </div>
      <div class="grid" id="g-datos"></div>
    </div>

    <!-- EN VIVO -->
    <div id="s-live" class="sec">
      <div class="dash-grid">
        <div class="d-card">
          <div class="d-h"><span class="live-dot"></span>Última Detección</div>
          <div id="d-ult"><div class="vacio"><div class="vacio-icon">🎙️</div><div class="vacio-msg">Sin detecciones aún</div><div class="vacio-sub">Activa el sistema de escucha</div></div></div>
        </div>
        <div class="d-card">

          <div class="d-h">Detecciones de Hoy</div>
          <div id="d-stats"><div class="vacio"><div class="vacio-icon">📊</div><div class="vacio-msg">Sin datos</div></div></div>
        </div>
      </div>
    </div>

    <!-- HISTORIAL -->
    <div id="s-historial" class="sec">
      <div class="d-card">
        <div class="d-h">Registro Completo</div>
        <div id="d-hist"><div class="vacio"><div class="vacio-icon">📋</div><div class="vacio-msg">Sin detecciones</div></div></div>
      </div>
    </div>

  </div>
</div>

<!-- ══ MODAL ═════════════════════════════════════════════════ -->
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

// ── Config visual por familia ────────────────────────────────
const FAM = {
  Trochilidae:      {e:'🌿',g:'linear-gradient(135deg,#0A2015,#1A4025)',c:'#4CAF80'},
  Hirundinidae:     {e:'🌊',g:'linear-gradient(135deg,#0A1828,#1A3050)',c:'#5890C8'},
  Passerellidae:    {e:'🌾',g:'linear-gradient(135deg,#251508,#50280A)',c:'#C88040'},
  Tyrannidae:       {e:'🌤️',g:'linear-gradient(135deg,#1A1808,#383010)',c:'#C8B840'},
  Corvidae:         {e:'💜',g:'linear-gradient(135deg,#150A28,#28104A)',c:'#9870C8'},
  Ardeidae:         {e:'🦢',g:'linear-gradient(135deg,#081820,#103040)',c:'#5090B8'},
  Threskiornithidae:{e:'🔴',g:'linear-gradient(135deg,#280808,#501010)',c:'#C84040'},
  Ciconiidae:       {e:'⬜',g:'linear-gradient(135deg,#181818,#303030)',c:'#909090'},
  Anatidae:         {e:'🦆',g:'linear-gradient(135deg,#082010,#104020)',c:'#40A060'},
  Jacanidae:        {e:'🌿',g:'linear-gradient(135deg,#1A1008,#352008)',c:'#C07830'},
  Accipitridae:     {e:'🦅',g:'linear-gradient(135deg,#1A0A08,#382018)',c:'#A06040'},
  Falconidae:       {e:'🦅',g:'linear-gradient(135deg,#080818,#101830)',c:'#5070A8'},
  Cathartidae:      {e:'🦅',g:'linear-gradient(135deg,#100808,#281410)',c:'#C9A84C'},
  Opisthocomidae:   {e:'🦜',g:'linear-gradient(135deg,#181008,#302010)',c:'#A08050'},
  Psittacidae:      {e:'🦜',g:'linear-gradient(135deg,#081808,#103010)',c:'#40B840'},

  Picidae:          {e:'🐦',g:'linear-gradient(135deg,#200808,#401010)',c:'#C04040'},
  Ramphastidae:     {e:'🌈',g:'linear-gradient(135deg,#081818,#102828)',c:'#40A8A8'},
  Alcedinidae:      {e:'🐟',g:'linear-gradient(135deg,#081028,#102048)',c:'#4060C0'},
  Thraupidae:       {e:'✨',g:'linear-gradient(135deg,#1A1808,#302808)',c:'#C8A830'},
  Cuculidae:        {e:'🐦',g:'linear-gradient(135deg,#101808,#202808)',c:'#709040'},
  Caprimulgidae:    {e:'🌙',g:'linear-gradient(135deg,#080810,#101018)',c:'#7870A0'},
  Thamnophilidae:   {e:'🐦',g:'linear-gradient(135deg,#080808,#181818)',c:'#808080'},
  Pipridae:         {e:'🔴',g:'linear-gradient(135deg,#200808,#380808)',c:'#D04040'},
  Rallidae:         {e:'💙',g:'linear-gradient(135deg,#080820,#101040)',c:'#4848C0'},
  Furnariidae:      {e:'🐦',g:'linear-gradient(135deg,#181008,#302010)',c:'#A08040'},
  Troglodytidae:    {e:'🐦',g:'linear-gradient(135deg,#201008,#381808)',c:'#B07030'},
  Mimidae:          {e:'🎵',g:'linear-gradient(135deg,#181818,#282828)',c:'#A0A0A0'},
  Pandionidae:      {e:'🦅',g:'linear-gradient(135deg,#081018,#101828)',c:'#4878A8'},
  Phalacrocoracidae:{e:'🐦',g:'linear-gradient(135deg,#080808,#141414)',c:'#606060'},
  Icteridae:        {e:'🟠',g:'linear-gradient(135deg,#281008,#481808)',c:'#C86020'},
  Jacanidae:        {e:'🐦',g:'linear-gradient(135deg,#200A08,#381408)',c:'#C07040'},
};
function getCfg(nom){
  const d=ESPECIES[nom];
  if(!d) return {e:'🐦',g:'linear-gradient(135deg,#181410,#282018)',c:'#C9A84C'};
  return FAM[d.familia]||{e:'🐦',g:'linear-gradient(135deg,#181410,#282018)',c:'#C9A84C'};
}

// ── Navegación ────────────────────────────────────────────────
function showPage(id){
  document.querySelectorAll('.page').forEach(p=>{p.style.display='none';p.classList.remove('active')});
  const p=document.getElementById(id);
  p.style.display='flex';setTimeout(()=>p.classList.add('active'),10);
}
function irApp(){showPage('app');cargarEspeciesDetectadas();buildDatos()}
function irLanding(){showPage('landing')}
function sec(id,btn){

  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('s-'+id).classList.add('active');btn.classList.add('active');
  if(id==='live'||id==='historial') fetchDash();
  if(id==='especies') cargarEspeciesDetectadas();
}

// ── Card builder ─────────────────────────────────────────────
function makeCard(nom,data,cfg,detCount,showEntrenada){
  const card=document.createElement('div');card.className='card';
  card.innerHTML=`
    <div class="c-hero" style="background:${cfg.g}">
      <div class="c-emoji">${cfg.e}</div>
      ${detCount>0?`<div class="c-det-count">${detCount} det.</div>`:''}
      ${showEntrenada&&data.entrenada?'<div class="badge-entrenada">ENTRENADA</div>':''}
    </div>
    <div class="c-body">
      <div class="c-nom">${nom}</div>
      <div class="c-cient">${data.cientifico}</div>
      <div class="c-foot">
        <span class="c-tag" style="background:${cfg.c}18;color:${cfg.c};border:1px solid ${cfg.c}28">${data.familia}</span>
        <span class="c-arrow">→</span>
      </div>
    </div>`;
  card.onclick=()=>abrirModal(nom,data,cfg);
  return card;
}

// ── ESPECIES DETECTADAS ───────────────────────────────────────
function cargarEspeciesDetectadas(){
  fetch('/api/especies-detectadas').then(r=>r.json()).then(lista=>{
    const g=document.getElementById('g-esp');g.innerHTML='';

    document.getElementById('cnt-esp').textContent=lista.length;
    if(!lista.length){
      g.innerHTML=`<div class="vacio" style="grid-column:1/-1">
        <div class="vacio-icon">🎙️</div>
        <div class="vacio-msg">Ninguna especie detectada aún</div>
        <div class="vacio-sub">Ejecuta inferencia.py para comenzar a detectar aves</div>
      </div>`;return;
    }
    lista.forEach(item=>{
      const nom=item.especie;
      const data=ESPECIES[nom];
      if(!data) return;
      const cfg=getCfg(nom);
      g.appendChild(makeCard(nom,data,cfg,item.total,true));
    });
  });
}

// ── DATOS: catálogo completo ──────────────────────────────────
function buildDatos(){
  const g=document.getElementById('g-datos');
  if(g.children.length>0) return;
  Object.entries(ESPECIES).forEach(([nom,data])=>{
    const cfg=getCfg(nom);
    g.appendChild(makeCard(nom,data,cfg,0,true));
  });
}

// ── Modal ─────────────────────────────────────────────────────
function abrirModal(nom,data,cfg){
  document.getElementById('m-hero').style.background=cfg.g;
  document.getElementById('m-emoji').textContent=cfg.e;

  document.getElementById('m-nombre').textContent=nom;
  document.getElementById('m-cient').textContent=data.cientifico;
  document.getElementById('m-hab').textContent=data.habitat;
  document.getElementById('m-fam').textContent=data.familia+(data.entrenada?' · Modelo entrenado':'');
  document.getElementById('m-desc').textContent=data.descripcion;
  document.getElementById('m-hoy').textContent='Cargando...';
  document.getElementById('m-tot').textContent='Cargando...';
  document.getElementById('m-dets').innerHTML='';
  document.getElementById('m-audio').innerHTML=data.audio
    ?`<audio controls src="${data.audio}"></audio>`
    :`<div class="no-audio">Audio aún no disponible — agrega archivo en /static/audios/</div>`;
  fetch('/api/especie/'+encodeURIComponent(nom)).then(r=>r.json()).then(d=>{
    document.getElementById('m-hoy').textContent=d.hoy+(d.hoy===1?' detección':' detecciones');
    document.getElementById('m-tot').textContent=d.total+(d.total===1?' en total':' en total');
    document.getElementById('m-dets').innerHTML=!d.recientes.length
      ?'<div class="vacio" style="padding:20px 0"><div class="vacio-msg">Sin detecciones de esta especie</div></div>'
      :d.recientes.map(r=>`<div class="det-row"><span class="det-hora">${r.fecha} · ${r.hora}</span><span class="det-cnn">CNN ${parseFloat(r.confianza_cnn).toFixed(1)}%</span><span class="det-rf">RF ${parseFloat(r.confianza_rf).toFixed(1)}%</span></div>`).join('');
  });
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow='hidden';
}
function cerrar(){document.getElementById('modal').classList.remove('open');document.body.style.overflow=''}

// ── Dashboard ─────────────────────────────────────────────────
function fetchDash(){
  fetch('/api/datos').then(r=>r.json()).then(d=>{rUlt(d.ultima);rStats(d.estadisticas);rHist(d.historial)});
}
function rUlt(d){
  const div=document.getElementById('d-ult');
  if(!d){div.innerHTML='<div class="vacio"><div class="vacio-icon">🎙️</div><div class="vacio-msg">Sin detecciones aún</div></div>';return}
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
  div.innerHTML=h.map(r=>{
    const co=r.coinciden===1;
    return`<div class="h-item"><div class="h-top"><span class="h-hora">${r.fecha} · ${r.hora}</span><span class="badge2 ${co?'b-si':'b-no'}" style="padding:2px 8px;font-size:9px">${co?'Coinciden':'Difieren'}</span></div><div class="h-cnn">CNN: ${r.especie_cnn.split(' - ')[0]} · ${parseFloat(r.confianza_cnn).toFixed(1)}%</div><div class="h-rf">RF: ${r.especie_rf.split(' - ')[0]} · ${parseFloat(r.confianza_rf).toFixed(1)}%</div></div>`;
  }).join('');
}
setInterval(()=>{
  if(['s-live','s-historial'].some(id=>document.getElementById(id).classList.contains('active'))) fetchDash();
},8000);

// Init
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

if __name__ == '__main__':
    print('CÓNDOR → http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)