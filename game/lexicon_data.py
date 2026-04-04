"""
Diccionarios locales para validación semántica básica.

No reemplazan un diccionario completo del español, pero permiten una
validación mucho más útil que el chequeo puramente superficial.
"""

NAMES = {
    "aaron", "abel", "abigail", "adalberto", "adela", "adriana", "agustin",
    "aida", "alba", "alejandra", "alejandro", "alfonso", "alicia", "alma",
    "alonso", "amalia", "ana", "andrea", "andres", "angel", "angela",
    "anibal", "antonella", "antonio", "ariadna", "armando", "arturo",
    "aurelio", "axel", "belen", "benjamin", "bernardo", "bianca", "brenda", "bruno",
    "camila", "camilo", "candela", "carla", "carlos", "carolina", "catalina",
    "cecilia", "celeste", "cesar", "claudia", "cristian", "cristina",
    "daniel", "daniela", "dario", "david", "debora", "diego", "dolores",
    "eduardo", "elena", "elias", "elisa", "emanuel", "emilia", "emilio",
    "enzo", "erica", "esteban", "eugenia", "eva", "fabian", "fatima",
    "felipe", "fernanda", "fernando", "florencia", "franco", "gabriel",
    "gabriela", "gaston", "gema", "genaro", "gisela", "gloria", "gonzalo",
    "guadalupe", "guillermo", "hector", "helena", "hugo", "ian", "ines",
    "irene", "isabel", "isabella", "ivan", "jacinta", "jaime", "javier",
    "jazmin", "jesica", "jesus", "joaquin", "jose", "josefina", "juan",
    "juana", "julia", "julian", "karina", "katia", "kevin", "lara", "laura",
    "lautaro", "leandro", "leo", "leon", "leonardo", "leticia", "lucas",
    "lucia", "luciano", "luisa", "manuel", "marcela", "marcelo", "marcos", "maria",
    "mariana", "mariano", "marina", "marta", "martin", "mateo", "matias", "melina", "micaela",
    "milagros", "mirta", "monica", "mora", "nadia", "nahuel", "natalia",
    "nico", "nicolas", "noelia", "norberto", "olga", "olivia", "oscar",
    "pamela", "paola", "patricia", "paulina", "pedro", "rafael", "raquel",
    "ricardo", "roberto", "rocio", "rodolfo", "romina", "rosa", "samanta",
    "santiago", "sebastian", "selena", "sergio", "silvia", "sofia", "susana", "tamara",
    "teo", "teresa", "thiago", "tobias", "tomas", "ulises", "valentina", "valeria",
    "vanesa", "veronica", "victor", "victoria", "vincenzo", "violeta",
    "viviana", "walter", "ximena", "yanina", "yasmin", "zoe"
}

ANIMALS = {
    "abeja", "aguila", "alce", "alpaca", "anaconda", "antilope", "ardilla",
    "avestruz", "ballena", "basilisco", "bisonte", "boa", "buho", "burro", "bufalo",
    "caballo", "cabra", "camaleon", "camello", "canario", "caracol",
    "castor", "cebra", "cerdo", "chita", "ciervo", "cobra", "codorniz",
    "conejo", "condor", "coral", "cordero", "cotorra", "coyote", "cuervo",
    "delfin", "elefante", "escarabajo", "escarpin", "escorpion", "faisan",
    "flamenco", "foca", "gacela", "gallo", "ganso", "gato", "gavilan",
    "gepardo", "gerbo", "golondrina", "gorila", "grillo", "guanaco",
    "hamster", "halcon", "hiena", "hipopotamo", "hormiga", "huron", "iguana",
    "jaguar", "jirafa", "koala", "lagarto", "langosta", "lechuza", "leon",
    "leopardo", "liebre", "llama", "lobo", "loro", "lucioperca", "mantis",
    "mariposa", "medusa", "mono", "morsa", "mosca", "mula", "murcielago", "nutria",
    "oveja", "oso", "paloma", "panda", "pantera", "pato", "pavo", "pelicano",
    "perro", "pinguino", "pulpo", "puma", "quetzal", "rana", "raton",
    "rinoceronte", "salamandra", "salmon", "serpiente", "suricata", "tapir",
    "tigre", "tortuga", "vaca", "venado", "vibora", "vizcacha", "zorro"
}

FRUITS_VEGETABLES = {
    "acelga", "ajo", "alcaucil", "anana", "ananas", "apio", "arandano", "arveja",
    "avellana", "banana", "batata", "berenjena", "bergamota", "brocoli",
    "cacahuate", "calabaza", "calabacin", "castaña", "cebolla", "cereza",
    "champiñon", "chaucha", "choclo", "ciruela", "coco", "coliflor",
    "damasco", "durazno", "esparrago", "espinaca", "frambuesa", "frutilla",
    "granada", "guayaba", "haba", "higo", "jalapeño", "kiwi", "lechuga",
    "lima", "limon", "mandarina", "mango", "manzana", "melon", "membrillo",
    "mora", "nabo", "naranja", "nuez", "palta", "papaya", "papa", "pepino",
    "pera", "perejil", "pimiento", "pomelo", "poroto", "puerro", "rabano",
    "remolacha", "repollo", "sandia", "tomate", "toronja", "uva", "vainilla",
    "zanahoria", "zapallo"
}

COUNTRIES = {
    "alemania", "argelia", "argentina", "australia", "austria", "belgica",
    "bolivia", "brasil", "canada", "chile", "china", "colombia", "corea",
    "costa rica", "croacia", "cuba", "dinamarca", "ecuador", "egipto",
    "el salvador", "eslovaquia", "eslovenia", "españa", "estados unidos",
    "finlandia", "francia", "grecia", "guatemala", "haiti", "honduras",
    "hungria", "india", "indonesia", "irlanda", "islandia", "israel", "italia",
    "jamaica", "japon", "luxemburgo", "malasia", "marruecos", "mexico",
    "nicaragua", "noruega", "nueva zelanda", "panama", "paraguay", "peru",
    "polonia", "portugal", "reino unido", "republica dominicana", "rumania",
    "rusia", "serbia", "singapur", "suecia", "suiza", "tailandia", "turquia",
    "ucrania", "uruguay", "venezuela", "vietnam"
}

CITIES = {
    "amsterdam", "asuncion", "atenas", "barcelona", "berlin", "bogota",
    "brasilia", "buenos aires", "caracas", "cartagena", "cordoba", "dublin",
    "florencia", "guadalajara", "helsinki", "lima", "lisboa", "londres",
    "madrid", "malaga", "mendoza", "mexico", "miami", "montevideo", "moscu",
    "neuquen", "new york", "oslo", "paris", "porto alegre", "quito", "roma",
    "rosario", "salta", "san juan", "san luis", "san pablo", "san rafael",
    "santa cruz", "santiago", "santo domingo", "sevilla", "tokio", "toronto",
    "tucuman", "valencia", "vancouver", "venecia", "viena", "villa carlos paz",
    "villa maria", "viedma"
}

OBJECTS = {
    "abanico", "agenda", "aguja", "alarma", "alfiler", "almohada", "anillo",
    "antena", "armario", "balde", "banco", "bandera", "barco", "baston", "bateria",
    "bicicleta", "boligrafo", "botella", "brujula", "cable", "cadena",
    "calculadora", "campana", "candado", "carpeta", "celular", "cierre",
    "cinta", "clavo", "computadora", "cuaderno", "cuchara", "cuchillo",
    "destornillador", "escalera", "escoba", "espejo", "estufa", "foco",
    "frasco", "gafas", "grapadora", "hamaca", "heladera", "impresora",
    "jarra", "juguete", "lampara", "lapiz", "libro", "linterna", "llave",
    "manta", "martillo", "mesa", "mochila", "monitor", "papel", "paraguas",
    "peine", "pelota", "pincel", "plato", "puerta", "radio", "reloj",
    "sarten", "silla", "sofa", "taza", "teclado", "televisor", "tenedor",
    "tijera", "toalla", "trompeta", "vaso", "vela", "ventana", "xilofon", "xilofono"
}
