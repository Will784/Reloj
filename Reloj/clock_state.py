import datetime
import logging
import time as _time
import sys

try:
    import tzdata  
except ImportError:
    pass

from zoneinfo import ZoneInfo
from typing import Optional

logger = logging.getLogger(__name__)

COUNTRY_TIMEZONES: dict[str, dict[str, str]] = {
    "Afganistán": {"Kabul": "Asia/Kabul"},
    "Albania": {"Tirana": "Europe/Tirane"},
    "Argelia": {"Argel": "Africa/Algiers"},
    "Andorra": {"Andorra": "Europe/Andorra"},
    "Angola": {"Luanda": "Africa/Luanda"},
    "Antigua y Barbuda": {"Antigua": "America/Antigua"},
    "Argentina": {
        "Buenos Aires": "America/Argentina/Buenos_Aires",
        "Córdoba": "America/Argentina/Cordoba",
        "Mendoza": "America/Argentina/Mendoza",
        "Salta": "America/Argentina/Salta",
        "San Juan": "America/Argentina/San_Juan",
        "Tucumán": "America/Argentina/Tucuman",
        "Ushuaia": "America/Argentina/Ushuaia",
    },
    "Armenia": {"Ereván": "Asia/Yerevan"},
    "Australia": {
        "Adelaida": "Australia/Adelaide",
        "Brisbane": "Australia/Brisbane",
        "Darwin": "Australia/Darwin",
        "Hobart": "Australia/Hobart",
        "Isla Lord Howe": "Australia/Lord_Howe",
        "Melbourne": "Australia/Melbourne",
        "Perth": "Australia/Perth",
        "Sídney": "Australia/Sydney",
    },
    "Austria": {"Viena": "Europe/Vienna"},
    "Azerbaiyán": {"Bakú": "Asia/Baku"},
    "Bahamas": {"Nassau": "America/Nassau"},
    "Baréin": {"Baréin": "Asia/Bahrain"},
    "Bangladés": {"Daca": "Asia/Dhaka"},
    "Barbados": {"Barbados": "America/Barbados"},
    "Bielorrusia": {"Minsk": "Europe/Minsk"},
    "Bélgica": {"Bruselas": "Europe/Brussels"},
    "Belice": {"Belice": "America/Belize"},
    "Benín": {"Porto-Novo": "Africa/Porto-Novo"},
    "Bután": {"Timbu": "Asia/Thimphu"},
    "Bolivia": {"La Paz": "America/La_Paz"},
    "Bosnia y Herzegovina": {"Sarajevo": "Europe/Sarajevo"},
    "Botsuana": {"Gaborone": "Africa/Gaborone"},
    "Brasil": {
        "Belém": "America/Belem",
        "Boa Vista": "America/Boa_Vista",
        "Campo Grande": "America/Campo_Grande",
        "Cuiabá": "America/Cuiaba",
        "Fortaleza": "America/Fortaleza",
        "Manaos": "America/Manaus",
        "Noronha": "America/Noronha",
        "Porto Velho": "America/Porto_Velho",
        "Recife": "America/Recife",
        "Rio Branco": "America/Rio_Branco",
        "Santarém": "America/Santarem",
        "São Paulo": "America/Sao_Paulo",
    },
    "Brunéi": {"Bandar Seri Begawan": "Asia/Brunei"},
    "Bulgaria": {"Sofía": "Europe/Sofia"},
    "Burkina Faso": {"Uagadugú": "Africa/Ouagadougou"},
    "Burundi": {"Buyumbura": "Africa/Bujumbura"},
    "Camboya": {"Nom Pen": "Asia/Phnom_Penh"},
    "Camerún": {"Duala": "Africa/Douala"},
    "Canadá": {
        "Atikokan": "America/Atikokan",
        "Blanc-Sablon": "America/Blanc-Sablon",
        "Cambridge Bay": "America/Cambridge_Bay",
        "Creston": "America/Creston",
        "Dawson": "America/Dawson",
        "Dawson Creek": "America/Dawson_Creek",
        "Edmonton": "America/Edmonton",
        "Fort Nelson": "America/Fort_Nelson",
        "Glace Bay": "America/Glace_Bay",
        "Goose Bay": "America/Goose_Bay",
        "Halifax": "America/Halifax",
        "Inuvik": "America/Inuvik",
        "Iqaluit": "America/Iqaluit",
        "Moncton": "America/Moncton",
        "Montreal": "America/Toronto",
        "Nipigon": "America/Nipigon",
        "Pangnirtung": "America/Pangnirtung",
        "Rainy River": "America/Rainy_River",
        "Rankin Inlet": "America/Rankin_Inlet",
        "Regina": "America/Regina",
        "Resolute": "America/Resolute",
        "St. Johns": "America/St_Johns",
        "Swift Current": "America/Swift_Current",
        "Thunder Bay": "America/Thunder_Bay",
        "Toronto": "America/Toronto",
        "Vancouver": "America/Vancouver",
        "Whitehorse": "America/Whitehorse",
        "Winnipeg": "America/Winnipeg",
        "Yellowknife": "America/Yellowknife",
    },
    "Cabo Verde": {"Praia": "Atlantic/Cape_Verde"},
    "República Centroafricana": {"Bangui": "Africa/Bangui"},
    "Chad": {"Yamena": "Africa/Ndjamena"},
    "Chile": {
        "Isla de Pascua": "Pacific/Easter",
        "Santiago": "America/Santiago",
    },
    "China": {"Shanghái": "Asia/Shanghai", "Ürümchi": "Asia/Urumqi"},
    "Colombia": {"Bogotá": "America/Bogota"},
    "Comoras": {"Moroni": "Indian/Comoro"},
    "Congo": {"Brazzaville": "Africa/Brazzaville"},
    "Costa Rica": {"San José": "America/Costa_Rica"},
    "Croacia": {"Zagreb": "Europe/Zagreb"},
    "Cuba": {"La Habana": "America/Havana"},
    "Chipre": {"Nicosia": "Asia/Nicosia"},
    "República Checa": {"Praga": "Europe/Prague"},
    "República Democrática del Congo": {
        "Kinshasa": "Africa/Kinshasa",
        "Lubumbashi": "Africa/Lubumbashi",
    },
    "Dinamarca": {"Copenhague": "Europe/Copenhagen"},
    "Yibuti": {"Yibuti": "Africa/Djibouti"},
    "República Dominicana": {"Santo Domingo": "America/Santo_Domingo"},
    "Ecuador": {"Galápagos": "Pacific/Galapagos", "Guayaquil": "America/Guayaquil"},
    "Egipto": {"El Cairo": "Africa/Cairo"},
    "El Salvador": {"San Salvador": "America/El_Salvador"},
    "Guinea Ecuatorial": {"Malabo": "Africa/Malabo"},
    "Eritrea": {"Asmara": "Africa/Asmara"},
    "Estonia": {"Talinn": "Europe/Tallinn"},
    "Esuatini": {"Mbabane": "Africa/Mbabane"},
    "Etiopía": {"Adís Abeba": "Africa/Addis_Ababa"},
    "Fiyi": {"Suva": "Pacific/Fiji"},
    "Finlandia": {"Helsinki": "Europe/Helsinki"},
    "Francia": {
        "Guadalupe": "America/Guadeloupe",
        "Martinica": "America/Martinique",
        "París": "Europe/Paris",
        "Reunión": "Indian/Reunion",
        "Tahití": "Pacific/Tahiti",
    },
    "Gabón": {"Libreville": "Africa/Libreville"},
    "Gambia": {"Banjul": "Africa/Banjul"},
    "Georgia": {"Tbilisi": "Asia/Tbilisi"},
    "Alemania": {"Berlín": "Europe/Berlin"},
    "Ghana": {"Accra": "Africa/Accra"},
    "Grecia": {"Atenas": "Europe/Athens"},
    "Guatemala": {"Ciudad de Guatemala": "America/Guatemala"},
    "Guinea": {"Conacrí": "Africa/Conakry"},
    "Guinea-Bisáu": {"Bisáu": "Africa/Bissau"},
    "Guyana": {"Georgetown": "America/Guyana"},
    "Haití": {"Puerto Príncipe": "America/Port-au-Prince"},
    "Honduras": {"Tegucigalpa": "America/Tegucigalpa"},
    "Hungría": {"Budapest": "Europe/Budapest"},
    "Islandia": {"Reikiavik": "Atlantic/Reykjavik"},
    "India": {"Calcuta": "Asia/Kolkata"},
    "Indonesia": {
        "Yakarta": "Asia/Jakarta",
        "Jayapura": "Asia/Jayapura",
        "Makassar": "Asia/Makassar",
        "Pontianak": "Asia/Pontianak",
    },
    "Irán": {"Teherán": "Asia/Tehran"},
    "Irak": {"Bagdad": "Asia/Baghdad"},
    "Irlanda": {"Dublín": "Europe/Dublin"},
    "Israel": {"Jerusalén": "Asia/Jerusalem"},
    "Italia": {"Roma": "Europe/Rome"},
    "Costa de Marfil": {"Abiyán": "Africa/Abidjan"},
    "Jamaica": {"Kingston": "America/Jamaica"},
    "Japón": {"Tokio": "Asia/Tokyo"},
    "Jordania": {"Amán": "Asia/Amman"},
    "Kazajstán": {
        "Almaty": "Asia/Almaty",
        "Aqtau": "Asia/Aqtau",
        "Aqtobe": "Asia/Aqtobe",
        "Atirau": "Asia/Atyrau",
        "Oral": "Asia/Oral",
        "Qostanay": "Asia/Qostanay",
        "Qyzylorda": "Asia/Qyzylorda",
    },
    "Kenia": {"Nairobi": "Africa/Nairobi"},
    "Kosovo": {"Pristina": "Europe/Belgrade"},
    "Kuwait": {"Kuwait": "Asia/Kuwait"},
    "Kirguistán": {"Bishkek": "Asia/Bishkek"},
    "Laos": {"Vientián": "Asia/Vientiane"},
    "Letonia": {"Riga": "Europe/Riga"},
    "Líbano": {"Beirut": "Asia/Beirut"},
    "Lesoto": {"Maseru": "Africa/Maseru"},
    "Liberia": {"Monrovia": "Africa/Monrovia"},
    "Libia": {"Trípoli": "Africa/Tripoli"},
    "Liechtenstein": {"Vaduz": "Europe/Vaduz"},
    "Lituania": {"Vilna": "Europe/Vilnius"},
    "Luxemburgo": {"Luxemburgo": "Europe/Luxembourg"},
    "Madagascar": {"Antananarivo": "Indian/Antananarivo"},
    "Malaui": {"Lilongüe": "Africa/Blantyre"},
    "Malasia": {"Kuala Lumpur": "Asia/Kuala_Lumpur", "Kuching": "Asia/Kuching"},
    "Maldivas": {"Malé": "Indian/Maldives"},
    "Malí": {"Bamako": "Africa/Bamako"},
    "Malta": {"La Valeta": "Europe/Malta"},
    "Mauritania": {"Nuakchot": "Africa/Nouakchott"},
    "Mauricio": {"Port Louis": "Indian/Mauritius"},
    "México": {
        "Bahía Banderas": "America/Bahia_Banderas",
        "Cancún": "America/Cancun",
        "Chihuahua": "America/Chihuahua",
        "Ciudad Juárez": "America/Ciudad_Juarez",
        "Ensenada": "America/Ensenada",
        "Hermosillo": "America/Hermosillo",
        "Matamoros": "America/Matamoros",
        "Mazatlán": "America/Mazatlan",
        "Mérida": "America/Merida",
        "Ciudad de México": "America/Mexico_City",
        "Monterrey": "America/Monterrey",
        "Ojinaga": "America/Ojinaga",
        "Tijuana": "America/Tijuana",
    },
    "Moldavia": {"Chisináu": "Europe/Chisinau"},
    "Mónaco": {"Mónaco": "Europe/Monaco"},
    "Mongolia": {
        "Choibalsan": "Asia/Choibalsan",
        "Hovd": "Asia/Hovd",
        "Ulán Bator": "Asia/Ulaanbaatar",
    },
    "Montenegro": {"Podgorica": "Europe/Podgorica"},
    "Marruecos": {"Casablanca": "Africa/Casablanca"},
    "Mozambique": {"Maputo": "Africa/Maputo"},
    "Birmania": {"Rangún": "Asia/Rangoon"},
    "Namibia": {"Windhoek": "Africa/Windhoek"},
    "Nepal": {"Katmandú": "Asia/Kathmandu"},
    "Países Bajos": {"Ámsterdam": "Europe/Amsterdam"},
    "Nueva Zelanda": {"Auckland": "Pacific/Auckland", "Chatham": "Pacific/Chatham"},
    "Nicaragua": {"Managua": "America/Managua"},
    "Níger": {"Niamey": "Africa/Niamey"},
    "Nigeria": {"Lagos": "Africa/Lagos"},
    "Corea del Norte": {"Pionyang": "Asia/Pyongyang"},
    "Macedonia del Norte": {"Skopie": "Europe/Skopje"},
    "Noruega": {"Oslo": "Europe/Oslo"},
    "Omán": {"Mascate": "Asia/Muscat"},
    "Pakistán": {"Karachi": "Asia/Karachi"},
    "Panamá": {"Panamá": "America/Panama"},
    "Papúa Nueva Guinea": {"Port Moresby": "Pacific/Port_Moresby"},
    "Paraguay": {"Asunción": "America/Asuncion"},
    "Perú": {"Lima": "America/Lima"},
    "Filipinas": {"Manila": "Asia/Manila"},
    "Polonia": {"Varsovia": "Europe/Warsaw"},
    "Portugal": {"Azores": "Atlantic/Azores", "Lisboa": "Europe/Lisbon", "Madeira": "Atlantic/Madeira"},
    "Catar": {"Doha": "Asia/Qatar"},
    "Rumania": {"Bucarest": "Europe/Bucharest"},
    "Rusia": {
        "Anadyr": "Asia/Anadyr",
        "Barnaúl": "Asia/Barnaul",
        "Chita": "Asia/Chita",
        "Irkutsk": "Asia/Irkutsk",
        "Kamchatka": "Asia/Kamchatka",
        "Khandyga": "Asia/Khandyga",
        "Krasnoyarsk": "Asia/Krasnoyarsk",
        "Magadán": "Asia/Magadan",
        "Moscú": "Europe/Moscow",
        "Novosibirsk": "Asia/Novosibirsk",
        "Novokuznetsk": "Asia/Novokuznetsk",
        "Omsk": "Asia/Omsk",
        "Sajálin": "Asia/Sakhalin",
        "Srednekolymsk": "Asia/Srednekolymsk",
        "Tomsk": "Asia/Tomsk",
        "Ust-Nera": "Asia/Ust-Nera",
        "Vladivostok": "Asia/Vladivostok",
        "Yakutsk": "Asia/Yakutsk",
        "Ekaterimburgo": "Asia/Yekaterinburg",
    },
    "Ruanda": {"Kigali": "Africa/Kigali"},
    "Arabia Saudita": {"Riad": "Asia/Riyadh"},
    "Senegal": {"Dakar": "Africa/Dakar"},
    "Serbia": {"Belgrado": "Europe/Belgrade"},
    "Sierra Leona": {"Freetown": "Africa/Freetown"},
    "Singapur": {"Singapur": "Asia/Singapore"},
    "Eslovaquia": {"Bratislava": "Europe/Bratislava"},
    "Eslovenia": {"Liubliana": "Europe/Ljubljana"},
    "Somalia": {"Mogadiscio": "Africa/Mogadishu"},
    "Sudáfrica": {"Johannesburgo": "Africa/Johannesburg"},
    "Corea del Sur": {"Seúl": "Asia/Seoul"},
    "Sudán del Sur": {"Juba": "Africa/Juba"},
    "España": {
        "Islas Canarias": "Atlantic/Canary",
        "Ceuta": "Africa/Ceuta",
        "Madrid": "Europe/Madrid",
    },
    "Sri Lanka": {"Colombo": "Asia/Colombo"},
    "Sudán": {"Jartún": "Africa/Khartoum"},
    "Surinam": {"Paramaribo": "America/Paramaribo"},
    "Suecia": {"Estocolmo": "Europe/Stockholm"},
    "Suiza": {"Zúrich": "Europe/Zurich"},
    "Siria": {"Damasco": "Asia/Damascus"},
    "Taiwán": {"Taipei": "Asia/Taipei"},
    "Tayikistán": {"Dushambé": "Asia/Dushanbe"},
    "Tanzania": {"Dar es Salaam": "Africa/Dar_es_Salaam"},
    "Tailandia": {"Bangkok": "Asia/Bangkok"},
    "Togo": {"Lomé": "Africa/Lome"},
    "Trinidad y Tobago": {"Port of Spain": "America/Port_of_Spain"},
    "Túnez": {"Túnez": "Africa/Tunis"},
    "Turquía": {"Estambul": "Europe/Istanbul"},
    "Turkmenistán": {"Asjabad": "Asia/Ashgabat"},
    "Uganda": {"Kampala": "Africa/Kampala"},
    "Ucrania": {
        "Kiev": "Europe/Kiev",
        "Simferópol": "Europe/Simferopol",
        "Uzhhorod": "Europe/Uzhgorod",
        "Zaporizhia": "Europe/Zaporozhye",
    },
    "Emiratos Árabes Unidos": {"Dubái": "Asia/Dubai"},
    "Reino Unido": {"Londres": "Europe/London"},
    "Estados Unidos": {
        "Adak": "America/Adak",
        "Anchorage": "America/Anchorage",
        "Boise": "America/Boise",
        "Chicago": "America/Chicago",
        "Denver": "America/Denver",
        "Detroit": "America/Detroit",
        "Honolulu": "Pacific/Honolulu",
        "Indianapolis": "America/Indiana/Indianapolis",
        "Juneau": "America/Juneau",
        "Los Ángeles": "America/Los_Angeles",
        "Louisville": "America/Kentucky/Louisville",
        "Menominee": "America/Menominee",
        "Metlakatla": "America/Metlakatla",
        "Nueva York": "America/New_York",
        "Nome": "America/Nome",
        "Phoenix": "America/Phoenix",
        "Sitka": "America/Sitka",
        "Yakutat": "America/Yakutat",
    },
    "Uruguay": {"Montevideo": "America/Montevideo"},
    "Uzbekistán": {"Samarcanda": "Asia/Samarkand", "Tashkent": "Asia/Tashkent"},
    "Venezuela": {"Caracas": "America/Caracas"},
    "Vietnam": {"Ho Chi Minh": "Asia/Ho_Chi_Minh"},
    "Yemen": {"Adén": "Asia/Aden"},
    "Zambia": {"Lusaka": "Africa/Lusaka"},
    "Zimbabue": {"Harare": "Africa/Harare"},
    "UTC": {"UTC": "UTC"},
}

# Capital o ciudad principal de cada país (debe coincidir con clave en COUNTRY_TIMEZONES)
COUNTRY_CAPITALS: dict[str, str] = {
    "Afganistán": "Kabul",
    "Albania": "Tirana",
    "Argelia": "Argel",
    "Andorra": "Andorra",
    "Angola": "Luanda",
    "Antigua y Barbuda": "Antigua",
    "Argentina": "Buenos Aires",
    "Armenia": "Ereván",
    "Australia": "Sídney",
    "Austria": "Viena",
    "Azerbaiyán": "Bakú",
    "Bahamas": "Nassau",
    "Baréin": "Baréin",
    "Bangladés": "Daca",
    "Barbados": "Barbados",
    "Bielorrusia": "Minsk",
    "Bélgica": "Bruselas",
    "Belice": "Belice",
    "Benín": "Porto-Novo",
    "Bután": "Timbu",
    "Bolivia": "La Paz",
    "Bosnia y Herzegovina": "Sarajevo",
    "Botsuana": "Gaborone",
    "Brasil": "São Paulo",
    "Brunéi": "Bandar Seri Begawan",
    "Bulgaria": "Sofía",
    "Burkina Faso": "Uagadugú",
    "Burundi": "Buyumbura",
    "Camboya": "Nom Pen",
    "Camerún": "Duala",
    "Canadá": "Toronto",
    "Cabo Verde": "Praia",
    "República Centroafricana": "Bangui",
    "Chad": "Yamena",
    "Chile": "Santiago",
    "China": "Shanghái",
    "Colombia": "Bogotá",
    "Comoras": "Moroni",
    "Congo": "Brazzaville",
    "Costa Rica": "San José",
    "Croacia": "Zagreb",
    "Cuba": "La Habana",
    "Chipre": "Nicosia",
    "República Checa": "Praga",
    "República Democrática del Congo": "Kinshasa",
    "Dinamarca": "Copenhague",
    "Yibuti": "Yibuti",
    "República Dominicana": "Santo Domingo",
    "Ecuador": "Guayaquil",
    "Egipto": "El Cairo",
    "El Salvador": "San Salvador",
    "Guinea Ecuatorial": "Malabo",
    "Eritrea": "Asmara",
    "Estonia": "Talinn",
    "Esuatini": "Mbabane",
    "Etiopía": "Adís Abeba",
    "Fiyi": "Suva",
    "Finlandia": "Helsinki",
    "Francia": "París",
    "Gabón": "Libreville",
    "Gambia": "Banjul",
    "Georgia": "Tbilisi",
    "Alemania": "Berlín",
    "Ghana": "Accra",
    "Grecia": "Atenas",
    "Guatemala": "Ciudad de Guatemala",
    "Guinea": "Conacrí",
    "Guinea-Bisáu": "Bisáu",
    "Guyana": "Georgetown",
    "Haití": "Puerto Príncipe",
    "Honduras": "Tegucigalpa",
    "Hungría": "Budapest",
    "Islandia": "Reikiavik",
    "India": "Calcuta",
    "Indonesia": "Yakarta",
    "Irán": "Teherán",
    "Irak": "Bagdad",
    "Irlanda": "Dublín",
    "Israel": "Jerusalén",
    "Italia": "Roma",
    "Costa de Marfil": "Abiyán",
    "Jamaica": "Kingston",
    "Japón": "Tokio",
    "Jordania": "Amán",
    "Kazajstán": "Almaty",
    "Kenia": "Nairobi",
    "Kosovo": "Pristina",
    "Kuwait": "Kuwait",
    "Kirguistán": "Bishkek",
    "Laos": "Vientián",
    "Letonia": "Riga",
    "Líbano": "Beirut",
    "Lesoto": "Maseru",
    "Liberia": "Monrovia",
    "Libia": "Trípoli",
    "Liechtenstein": "Vaduz",
    "Lituania": "Vilna",
    "Luxemburgo": "Luxemburgo",
    "Madagascar": "Antananarivo",
    "Malaui": "Lilongüe",
    "Malasia": "Kuala Lumpur",
    "Maldivas": "Malé",
    "Malí": "Bamako",
    "Malta": "La Valeta",
    "Mauritania": "Nuakchot",
    "Mauricio": "Port Louis",
    "México": "Ciudad de México",
    "Moldavia": "Chisináu",
    "Mónaco": "Mónaco",
    "Mongolia": "Ulán Bator",
    "Montenegro": "Podgorica",
    "Marruecos": "Casablanca",
    "Mozambique": "Maputo",
    "Birmania": "Rangún",
    "Namibia": "Windhoek",
    "Nepal": "Katmandú",
    "Países Bajos": "Ámsterdam",
    "Nueva Zelanda": "Auckland",
    "Nicaragua": "Managua",
    "Níger": "Niamey",
    "Nigeria": "Lagos",
    "Corea del Norte": "Pionyang",
    "Macedonia del Norte": "Skopie",
    "Noruega": "Oslo",
    "Omán": "Mascate",
    "Pakistán": "Karachi",
    "Panamá": "Panamá",
    "Papúa Nueva Guinea": "Port Moresby",
    "Paraguay": "Asunción",
    "Perú": "Lima",
    "Filipinas": "Manila",
    "Polonia": "Varsovia",
    "Portugal": "Lisboa",
    "Catar": "Doha",
    "Rumania": "Bucarest",
    "Rusia": "Moscú",
    "Ruanda": "Kigali",
    "Arabia Saudita": "Riad",
    "Senegal": "Dakar",
    "Serbia": "Belgrado",
    "Sierra Leona": "Freetown",
    "Singapur": "Singapur",
    "Eslovaquia": "Bratislava",
    "Eslovenia": "Liubliana",
    "Somalia": "Mogadiscio",
    "Sudáfrica": "Johannesburgo",
    "Corea del Sur": "Seúl",
    "Sudán del Sur": "Juba",
    "España": "Madrid",
    "Sri Lanka": "Colombo",
    "Sudán": "Jartún",
    "Surinam": "Paramaribo",
    "Suecia": "Estocolmo",
    "Suiza": "Zúrich",
    "Siria": "Damasco",
    "Taiwán": "Taipei",
    "Tayikistán": "Dushambé",
    "Tanzania": "Dar es Salaam",
    "Tailandia": "Bangkok",
    "Togo": "Lomé",
    "Trinidad y Tobago": "Port of Spain",
    "Túnez": "Túnez",
    "Turquía": "Estambul",
    "Turkmenistán": "Asjabad",
    "Uganda": "Kampala",
    "Ucrania": "Kiev",
    "Emiratos Árabes Unidos": "Dubái",
    "Reino Unido": "Londres",
    "Estados Unidos": "Nueva York",
    "Uruguay": "Montevideo",
    "Uzbekistán": "Tashkent",
    "Venezuela": "Caracas",
    "Vietnam": "Ho Chi Minh",
    "Yemen": "Adén",
    "Zambia": "Lusaka",
    "Zimbabue": "Harare",
    "UTC": "UTC",
}

COMMON_TIMEZONES: list[str] = sorted([
    "America/Bogota", "America/New_York", "America/Chicago",
    "America/Denver", "America/Los_Angeles", "America/Mexico_City",
    "America/Lima", "America/Santiago", "America/Argentina/Buenos_Aires",
    "America/Sao_Paulo", "America/Caracas", "America/Havana",
    "Europe/Madrid", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Europe/Rome", "Europe/Moscow", "Asia/Dubai", "Asia/Kolkata",
    "Asia/Shanghai", "Asia/Tokyo", "Asia/Seoul", "Australia/Sydney",
    "Pacific/Auckland", "UTC",
])


class ClockState:
    def __init__(
        self,
        timezone_name: str = "America/Bogota",
        offset_seconds: int = 0,
        hour_format_24: bool = False,
    ) -> None:
        self._offset_seconds: int = offset_seconds
        self.adjusting: bool = False
        self.hour_format_24: bool = hour_format_24
        self._set_timezone(timezone_name)

        self._stopwatch_running: bool = False
        self._stopwatch_start: Optional[float] = None
        self._stopwatch_accumulated: float = 0.0

        self._timer_running: bool = False
        self._timer_end: Optional[float] = None
        self._timer_total_seconds: int = 0
        self._timer_original_seconds: int = 0
        self._timer_finished: bool = False

        logger.info("ClockState initialised | tz=%s offset=%ds", timezone_name, offset_seconds)

    def _set_timezone(self, name: str) -> None:
        try:
            self._tz = ZoneInfo(name)
            self._timezone_name = name
        except Exception as exc:
            logger.error("Invalid timezone '%s': %s — falling back to UTC", name, exc)
            self._tz = datetime.timezone.utc
            self._timezone_name = "UTC"

    @property
    def timezone_name(self) -> str:
        return self._timezone_name

    @timezone_name.setter
    def timezone_name(self, name: str) -> None:
        logger.info("Timezone changed: %s -> %s", self._timezone_name, name)
        self._set_timezone(name)

    def current_time(self) -> datetime.datetime:
        now = datetime.datetime.now(tz=self._tz)
        return now + datetime.timedelta(seconds=self._offset_seconds)

    def start_adjusting(self) -> None:
        self.adjusting = True

    def stop_adjusting(self) -> None:
        self.adjusting = False

    def adjust_minutes(self, delta: int) -> None:
        self._offset_seconds += delta * 60
        logger.debug("Time adjusted by %d min | total offset=%ds", delta, self._offset_seconds)

    def adjust_hours(self, delta: int) -> None:
        self._offset_seconds += delta * 3600
        logger.debug("Time adjusted by %d h | total offset=%ds", delta, self._offset_seconds)

    def reset_offset(self) -> None:
        logger.info("Time offset reset to 0.")
        self._offset_seconds = 0
        self.adjusting = False

    @property
    def offset_seconds(self) -> int:
        return self._offset_seconds

    @offset_seconds.setter
    def offset_seconds(self, value: int) -> None:
        self._offset_seconds = value

    def should_trigger_alarm(self, alarm: dict) -> bool:
        if not alarm.get("enabled"):
            return False
        now = self.current_time()
        return now.hour == alarm["hour"] and now.minute == alarm["minute"] and now.second == 0

    def stopwatch_start(self) -> None:
        if not self._stopwatch_running:
            self._stopwatch_start = _time.monotonic()
            self._stopwatch_running = True
            logger.debug("Stopwatch started.")

    def stopwatch_pause(self) -> None:
        if self._stopwatch_running and self._stopwatch_start is not None:
            self._stopwatch_accumulated += _time.monotonic() - self._stopwatch_start
            self._stopwatch_running = False
            logger.debug("Stopwatch paused at %.2fs", self._stopwatch_accumulated)

    def stopwatch_reset(self) -> None:
        self._stopwatch_running = False
        self._stopwatch_start = None
        self._stopwatch_accumulated = 0.0
        logger.debug("Stopwatch reset.")

    def stopwatch_elapsed(self) -> float:
        elapsed = self._stopwatch_accumulated
        if self._stopwatch_running and self._stopwatch_start is not None:
            elapsed += _time.monotonic() - self._stopwatch_start
        return elapsed

    @property
    def stopwatch_running(self) -> bool:
        return self._stopwatch_running

    def timer_set(self, total_seconds: int) -> None:
        self._timer_total_seconds = total_seconds
        self._timer_original_seconds = total_seconds
        self._timer_running = False
        self._timer_end = None
        self._timer_finished = False
        logger.debug("Timer set to %ds", total_seconds)

    def timer_start(self) -> None:
        if self._timer_total_seconds > 0 and not self._timer_running:
            remaining = self.timer_remaining()
            self._timer_end = _time.monotonic() + (remaining if remaining > 0 else self._timer_total_seconds)
            self._timer_running = True
            self._timer_finished = False
            logger.debug("Timer started, ends in %.1fs", self._timer_end - _time.monotonic())

    def timer_pause(self) -> None:
        if self._timer_running and self._timer_end is not None:
            remaining = self._timer_end - _time.monotonic()
            self._timer_total_seconds = max(0, int(remaining))
            self._timer_end = None
            self._timer_running = False
            logger.debug("Timer paused with %ds remaining.", self._timer_total_seconds)

    def timer_reset(self) -> None:
        self._timer_running = False
        self._timer_end = None
        self._timer_total_seconds = self._timer_original_seconds
        self._timer_finished = False

    def timer_remaining(self) -> float:
        if self._timer_end is None:
            return float(self._timer_total_seconds)
        remaining = self._timer_end - _time.monotonic()
        if remaining <= 0:
            self._timer_running = False
            self._timer_finished = True
            return 0.0
        return remaining

    @property
    def timer_running(self) -> bool:
        return self._timer_running

    @property
    def timer_finished(self) -> bool:
        return self._timer_finished