# data/ubicaciones.py
"""
Datos geográficos hardcoded para los formularios.
Si necesitas más ciudades, simplemente agrégalas a la lista.
"""

PAISES = ["México", "Estados Unidos", "Canadá", "España", "Otro"]

# Estados/provincias por país
ESTADOS_POR_PAIS = {
    "México": [
        "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
        "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila", "Colima",
        "Durango", "Estado de México", "Guanajuato", "Guerrero", "Hidalgo",
        "Jalisco", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
        "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa",
        "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán",
        "Zacatecas"
    ],
    "Estados Unidos": [
        "Texas", "California", "Florida", "Arizona", "Nuevo México", "Otro"
    ],
    "Canadá": ["Ontario", "Quebec", "Columbia Británica", "Otro"],
    "España": ["Madrid", "Cataluña", "Andalucía", "Otro"],
    "Otro": ["Otro"],
}

# Ciudades principales por estado (puedes ampliar)
CIUDADES_POR_ESTADO = {
    # MÉXICO
    "Aguascalientes": ["Aguascalientes", "Jesús María", "Calvillo", "Otra"],
    "Baja California": ["Tijuana", "Mexicali", "Ensenada", "Tecate", "Rosarito", "Otra"],
    "Baja California Sur": ["La Paz", "Los Cabos", "Loreto", "Comondú", "Otra"],
    "Campeche": ["Campeche", "Ciudad del Carmen", "Champotón", "Otra"],
    "Chiapas": ["Tuxtla Gutiérrez", "Tapachula", "San Cristóbal de las Casas", "Comitán", "Otra"],
    "Chihuahua": ["Chihuahua", "Ciudad Juárez", "Delicias", "Cuauhtémoc", "Parral", "Otra"],
    "Ciudad de México": ["Álvaro Obregón", "Benito Juárez", "Coyoacán", "Cuauhtémoc",
                         "Iztapalapa", "Miguel Hidalgo", "Tlalpan", "Xochimilco", "Otra"],
    "Coahuila": ["Saltillo", "Torreón", "Monclova", "Piedras Negras", "Acuña", "Otra"],
    "Colima": ["Colima", "Manzanillo", "Tecomán", "Villa de Álvarez", "Otra"],
    "Durango": ["Durango", "Gómez Palacio", "Lerdo", "Otra"],
    "Estado de México": ["Toluca", "Ecatepec", "Naucalpan", "Tlalnepantla",
                         "Nezahualcóyotl", "Atizapán", "Otra"],
    "Guanajuato": ["León", "Irapuato", "Celaya", "Salamanca", "Guanajuato", "Otra"],
    "Guerrero": ["Acapulco", "Chilpancingo", "Iguala", "Zihuatanejo", "Otra"],
    "Hidalgo": ["Pachuca", "Tulancingo", "Tula", "Huejutla", "Otra"],
    "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "Puerto Vallarta", "Otra"],
    "Michoacán": ["Morelia", "Uruapan", "Zamora", "Lázaro Cárdenas", "Otra"],
    "Morelos": ["Cuernavaca", "Jiutepec", "Cuautla", "Temixco", "Otra"],
    "Nayarit": ["Tepic", "Bahía de Banderas", "Xalisco", "Otra"],
    "Nuevo León": ["Monterrey", "Guadalupe", "Apodaca", "San Nicolás", "Santa Catarina", "Otra"],
    "Oaxaca": ["Oaxaca", "Salina Cruz", "Tuxtepec", "Juchitán", "Otra"],
    "Puebla": ["Puebla", "Tehuacán", "Atlixco", "San Martín Texmelucan", "Otra"],
    "Querétaro": ["Querétaro", "San Juan del Río", "Corregidora", "El Marqués", "Otra"],
    "Quintana Roo": ["Cancún", "Playa del Carmen", "Chetumal", "Cozumel", "Tulum", "Otra"],
    "San Luis Potosí": ["San Luis Potosí", "Soledad", "Ciudad Valles", "Matehuala", "Otra"],
    "Sinaloa": ["Culiacán", "Mazatlán", "Los Mochis", "Guasave", "Otra"],
    "Sonora": ["Hermosillo", "Ciudad Obregón", "Nogales", "Navojoa", "Otra"],
    "Tabasco": ["Villahermosa", "Cárdenas", "Comalcalco", "Otra"],
    "Tamaulipas": ["Tampico", "Ciudad Victoria", "Reynosa", "Matamoros", "Nuevo Laredo",
                   "Ciudad Madero", "Altamira", "Mante", "Otra"],
    "Tlaxcala": ["Tlaxcala", "Apizaco", "Huamantla", "Otra"],
    "Veracruz": ["Veracruz", "Xalapa", "Coatzacoalcos", "Poza Rica", "Córdoba", "Orizaba", "Otra"],
    "Yucatán": ["Mérida", "Valladolid", "Tizimín", "Progreso", "Otra"],
    "Zacatecas": ["Zacatecas", "Fresnillo", "Guadalupe", "Otra"],

    # OTROS (lista mínima, completa según necesites)
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "McAllen", "Laredo", "Otra"],
    "California": ["Los Angeles", "San Diego", "San Francisco", "Otra"],
    "Florida": ["Miami", "Orlando", "Tampa", "Otra"],
    "Arizona": ["Phoenix", "Tucson", "Otra"],
    "Nuevo México": ["Albuquerque", "Santa Fe", "Otra"],
    "Ontario": ["Toronto", "Ottawa", "Otra"],
    "Quebec": ["Montreal", "Quebec", "Otra"],
    "Columbia Británica": ["Vancouver", "Victoria", "Otra"],
    "Madrid": ["Madrid", "Alcalá de Henares", "Otra"],
    "Cataluña": ["Barcelona", "Tarragona", "Otra"],
    "Andalucía": ["Sevilla", "Málaga", "Otra"],
    "Otro": ["Otra"],
}


def obtener_estados(pais: str) -> list:
    """Devuelve la lista de estados/provincias para un país."""
    return ESTADOS_POR_PAIS.get(pais, ["Otro"])


def obtener_ciudades(estado: str) -> list:
    """Devuelve la lista de ciudades para un estado."""
    return CIUDADES_POR_ESTADO.get(estado, ["Otra"])