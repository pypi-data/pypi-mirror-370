from enum import Enum
from typing import Optional


class Country(Enum):
    UNKNOWN = 0
    MEXICO = 1
    USA = 2
    CANADA = 3
    SPAIN = 4
    ARGENTINA = 5
    COLOMBIA = 6
    PERU = 7
    CHILE = 8
    BRAZIL = 9
    VENEZUELA = 10
    # Additional countries in alphabetical order
    AFGHANISTAN = 11
    ALBANIA = 12
    ALGERIA = 13
    ANDORRA = 14
    ANGOLA = 15
    ANTIGUA_AND_BARBUDA = 16
    ARMENIA = 17
    AUSTRALIA = 18
    AUSTRIA = 19
    AZERBAIJAN = 20
    BAHAMAS = 21
    BAHRAIN = 22
    BANGLADESH = 23
    BARBADOS = 24
    BELARUS = 25
    BELGIUM = 26
    BELIZE = 27
    BENIN = 28
    BHUTAN = 29
    BOLIVIA = 30
    BOSNIA_AND_HERZEGOVINA = 31
    BOTSWANA = 32
    BRUNEI = 33
    BULGARIA = 34
    BURKINA_FASO = 35
    BURUNDI = 36
    CABO_VERDE = 37
    CAMBODIA = 38
    CAMEROON = 39
    CENTRAL_AFRICAN_REPUBLIC = 40
    CHAD = 41
    CHINA = 42
    COMOROS = 43
    CONGO_DEMOCRATIC_REPUBLIC = 44
    CONGO_REPUBLIC = 45
    COSTA_RICA = 46
    COTE_DIVOIRE = 47
    CROATIA = 48
    CUBA = 49
    CYPRUS = 50
    CZECH_REPUBLIC = 51
    DENMARK = 52
    DJIBOUTI = 53
    DOMINICA = 54
    DOMINICAN_REPUBLIC = 55
    ECUADOR = 56
    EGYPT = 57
    EL_SALVADOR = 58
    EQUATORIAL_GUINEA = 59
    ERITREA = 60
    ESTONIA = 61
    ESWATINI = 62
    ETHIOPIA = 63
    FIJI = 64
    FINLAND = 65
    FRANCE = 66
    GABON = 67
    GAMBIA = 68
    GEORGIA = 69
    GERMANY = 70
    GHANA = 71
    GREECE = 72
    GRENADA = 73
    GUATEMALA = 74
    GUINEA = 75
    GUINEA_BISSAU = 76
    GUYANA = 77
    HAITI = 78
    HONDURAS = 79
    HUNGARY = 80
    ICELAND = 81
    INDIA = 82
    INDONESIA = 83
    IRAN = 84
    IRAQ = 85
    IRELAND = 86
    ISRAEL = 87
    ITALY = 88
    JAMAICA = 89
    JAPAN = 90
    JORDAN = 91
    KAZAKHSTAN = 92
    KENYA = 93
    KIRIBATI = 94
    KOREA_NORTH = 95
    KOREA_SOUTH = 96
    KOSOVO = 97
    KUWAIT = 98
    KYRGYZSTAN = 99
    LAOS = 100
    LATVIA = 101
    LEBANON = 102
    LESOTHO = 103
    LIBERIA = 104
    LIBYA = 105
    LIECHTENSTEIN = 106
    LITHUANIA = 107
    LUXEMBOURG = 108
    MADAGASCAR = 109
    MALAWI = 110
    MALAYSIA = 111
    MALDIVES = 112
    MALI = 113
    MALTA = 114
    MARSHALL_ISLANDS = 115
    MAURITANIA = 116
    MAURITIUS = 117
    MICRONESIA = 118
    MOLDOVA = 119
    MONACO = 120
    MONGOLIA = 121
    MONTENEGRO = 122
    MOROCCO = 123
    MOZAMBIQUE = 124
    MYANMAR = 125
    NAMIBIA = 126
    NAURU = 127
    NEPAL = 128
    NETHERLANDS = 129
    NEW_ZEALAND = 130
    NICARAGUA = 131
    NIGER = 132
    NIGERIA = 133
    NORTH_MACEDONIA = 134
    NORWAY = 135
    OMAN = 136
    PAKISTAN = 137
    PALAU = 138
    PALESTINE = 139
    PANAMA = 140
    PAPUA_NEW_GUINEA = 141
    PARAGUAY = 142
    PHILIPPINES = 143
    POLAND = 144
    PORTUGAL = 145
    QATAR = 146
    ROMANIA = 147
    RUSSIA = 148
    RWANDA = 149
    SAINT_KITTS_AND_NEVIS = 150
    SAINT_LUCIA = 151
    SAINT_VINCENT_AND_THE_GRENADINES = 152
    SAMOA = 153
    SAN_MARINO = 154
    SAO_TOME_AND_PRINCIPE = 155
    SAUDI_ARABIA = 156
    SENEGAL = 157
    SERBIA = 158
    SEYCHELLES = 159
    SIERRA_LEONE = 160
    SINGAPORE = 161
    SLOVAKIA = 162
    SLOVENIA = 163
    SOLOMON_ISLANDS = 164
    SOMALIA = 165
    SOUTH_AFRICA = 166
    SOUTH_SUDAN = 167
    SRI_LANKA = 168
    SUDAN = 169
    SURINAME = 170
    SWEDEN = 171
    SWITZERLAND = 172
    SYRIA = 173
    TAIWAN = 174
    TAJIKISTAN = 175
    TANZANIA = 176
    THAILAND = 177
    TIMOR_LESTE = 178
    TOGO = 179
    TONGA = 180
    TRINIDAD_AND_TOBAGO = 181
    TUNISIA = 182
    TURKEY = 183
    TURKMENISTAN = 184
    TUVALU = 185
    UGANDA = 186
    UKRAINE = 187
    UNITED_ARAB_EMIRATES = 188
    UNITED_KINGDOM = 189
    URUGUAY = 190
    UZBEKISTAN = 191
    VANUATU = 192
    VATICAN_CITY = 193
    VIETNAM = 194
    YEMEN = 195
    ZAMBIA = 196
    ZIMBABWE = 197


# ISO 3166-1 alpha-2 country codes mapping
_ISO_CODES = {
    Country.UNKNOWN: None,
    Country.MEXICO: "MX",
    Country.USA: "US",
    Country.CANADA: "CA",
    Country.SPAIN: "ES",
    Country.ARGENTINA: "AR",
    Country.COLOMBIA: "CO",
    Country.PERU: "PE",
    Country.CHILE: "CL",
    Country.BRAZIL: "BR",
    Country.VENEZUELA: "VE",
    Country.AFGHANISTAN: "AF",
    Country.ALBANIA: "AL",
    Country.ALGERIA: "DZ",
    Country.ANDORRA: "AD",
    Country.ANGOLA: "AO",
    Country.ANTIGUA_AND_BARBUDA: "AG",
    Country.ARMENIA: "AM",
    Country.AUSTRALIA: "AU",
    Country.AUSTRIA: "AT",
    Country.AZERBAIJAN: "AZ",
    Country.BAHAMAS: "BS",
    Country.BAHRAIN: "BH",
    Country.BANGLADESH: "BD",
    Country.BARBADOS: "BB",
    Country.BELARUS: "BY",
    Country.BELGIUM: "BE",
    Country.BELIZE: "BZ",
    Country.BENIN: "BJ",
    Country.BHUTAN: "BT",
    Country.BOLIVIA: "BO",
    Country.BOSNIA_AND_HERZEGOVINA: "BA",
    Country.BOTSWANA: "BW",
    Country.BRUNEI: "BN",
    Country.BULGARIA: "BG",
    Country.BURKINA_FASO: "BF",
    Country.BURUNDI: "BI",
    Country.CABO_VERDE: "CV",
    Country.CAMBODIA: "KH",
    Country.CAMEROON: "CM",
    Country.CENTRAL_AFRICAN_REPUBLIC: "CF",
    Country.CHAD: "TD",
    Country.CHINA: "CN",
    Country.COMOROS: "KM",
    Country.CONGO_DEMOCRATIC_REPUBLIC: "CD",
    Country.CONGO_REPUBLIC: "CG",
    Country.COSTA_RICA: "CR",
    Country.COTE_DIVOIRE: "CI",
    Country.CROATIA: "HR",
    Country.CUBA: "CU",
    Country.CYPRUS: "CY",
    Country.CZECH_REPUBLIC: "CZ",
    Country.DENMARK: "DK",
    Country.DJIBOUTI: "DJ",
    Country.DOMINICA: "DM",
    Country.DOMINICAN_REPUBLIC: "DO",
    Country.ECUADOR: "EC",
    Country.EGYPT: "EG",
    Country.EL_SALVADOR: "SV",
    Country.EQUATORIAL_GUINEA: "GQ",
    Country.ERITREA: "ER",
    Country.ESTONIA: "EE",
    Country.ESWATINI: "SZ",
    Country.ETHIOPIA: "ET",
    Country.FIJI: "FJ",
    Country.FINLAND: "FI",
    Country.FRANCE: "FR",
    Country.GABON: "GA",
    Country.GAMBIA: "GM",
    Country.GEORGIA: "GE",
    Country.GERMANY: "DE",
    Country.GHANA: "GH",
    Country.GREECE: "GR",
    Country.GRENADA: "GD",
    Country.GUATEMALA: "GT",
    Country.GUINEA: "GN",
    Country.GUINEA_BISSAU: "GW",
    Country.GUYANA: "GY",
    Country.HAITI: "HT",
    Country.HONDURAS: "HN",
    Country.HUNGARY: "HU",
    Country.ICELAND: "IS",
    Country.INDIA: "IN",
    Country.INDONESIA: "ID",
    Country.IRAN: "IR",
    Country.IRAQ: "IQ",
    Country.IRELAND: "IE",
    Country.ISRAEL: "IL",
    Country.ITALY: "IT",
    Country.JAMAICA: "JM",
    Country.JAPAN: "JP",
    Country.JORDAN: "JO",
    Country.KAZAKHSTAN: "KZ",
    Country.KENYA: "KE",
    Country.KIRIBATI: "KI",
    Country.KOREA_NORTH: "KP",
    Country.KOREA_SOUTH: "KR",
    Country.KOSOVO: "XK",
    Country.KUWAIT: "KW",
    Country.KYRGYZSTAN: "KG",
    Country.LAOS: "LA",
    Country.LATVIA: "LV",
    Country.LEBANON: "LB",
    Country.LESOTHO: "LS",
    Country.LIBERIA: "LR",
    Country.LIBYA: "LY",
    Country.LIECHTENSTEIN: "LI",
    Country.LITHUANIA: "LT",
    Country.LUXEMBOURG: "LU",
    Country.MADAGASCAR: "MG",
    Country.MALAWI: "MW",
    Country.MALAYSIA: "MY",
    Country.MALDIVES: "MV",
    Country.MALI: "ML",
    Country.MALTA: "MT",
    Country.MARSHALL_ISLANDS: "MH",
    Country.MAURITANIA: "MR",
    Country.MAURITIUS: "MU",
    Country.MICRONESIA: "FM",
    Country.MOLDOVA: "MD",
    Country.MONACO: "MC",
    Country.MONGOLIA: "MN",
    Country.MONTENEGRO: "ME",
    Country.MOROCCO: "MA",
    Country.MOZAMBIQUE: "MZ",
    Country.MYANMAR: "MM",
    Country.NAMIBIA: "NA",
    Country.NAURU: "NR",
    Country.NEPAL: "NP",
    Country.NETHERLANDS: "NL",
    Country.NEW_ZEALAND: "NZ",
    Country.NICARAGUA: "NI",
    Country.NIGER: "NE",
    Country.NIGERIA: "NG",
    Country.NORTH_MACEDONIA: "MK",
    Country.NORWAY: "NO",
    Country.OMAN: "OM",
    Country.PAKISTAN: "PK",
    Country.PALAU: "PW",
    Country.PALESTINE: "PS",
    Country.PANAMA: "PA",
    Country.PAPUA_NEW_GUINEA: "PG",
    Country.PARAGUAY: "PY",
    Country.PHILIPPINES: "PH",
    Country.POLAND: "PL",
    Country.PORTUGAL: "PT",
    Country.QATAR: "QA",
    Country.ROMANIA: "RO",
    Country.RUSSIA: "RU",
    Country.RWANDA: "RW",
    Country.SAINT_KITTS_AND_NEVIS: "KN",
    Country.SAINT_LUCIA: "LC",
    Country.SAINT_VINCENT_AND_THE_GRENADINES: "VC",
    Country.SAMOA: "WS",
    Country.SAN_MARINO: "SM",
    Country.SAO_TOME_AND_PRINCIPE: "ST",
    Country.SAUDI_ARABIA: "SA",
    Country.SENEGAL: "SN",
    Country.SERBIA: "RS",
    Country.SEYCHELLES: "SC",
    Country.SIERRA_LEONE: "SL",
    Country.SINGAPORE: "SG",
    Country.SLOVAKIA: "SK",
    Country.SLOVENIA: "SI",
    Country.SOLOMON_ISLANDS: "SB",
    Country.SOMALIA: "SO",
    Country.SOUTH_AFRICA: "ZA",
    Country.SOUTH_SUDAN: "SS",
    Country.SRI_LANKA: "LK",
    Country.SUDAN: "SD",
    Country.SURINAME: "SR",
    Country.SWEDEN: "SE",
    Country.SWITZERLAND: "CH",
    Country.SYRIA: "SY",
    Country.TAIWAN: "TW",
    Country.TAJIKISTAN: "TJ",
    Country.TANZANIA: "TZ",
    Country.THAILAND: "TH",
    Country.TIMOR_LESTE: "TL",
    Country.TOGO: "TG",
    Country.TONGA: "TO",
    Country.TRINIDAD_AND_TOBAGO: "TT",
    Country.TUNISIA: "TN",
    Country.TURKEY: "TR",
    Country.TURKMENISTAN: "TM",
    Country.TUVALU: "TV",
    Country.UGANDA: "UG",
    Country.UKRAINE: "UA",
    Country.UNITED_ARAB_EMIRATES: "AE",
    Country.UNITED_KINGDOM: "GB",
    Country.URUGUAY: "UY",
    Country.UZBEKISTAN: "UZ",
    Country.VANUATU: "VU",
    Country.VATICAN_CITY: "VA",
    Country.VIETNAM: "VN",
    Country.YEMEN: "YE",
    Country.ZAMBIA: "ZM",
    Country.ZIMBABWE: "ZW",
}


def get_iso_code(country: Country) -> Optional[str]:
    """Get the ISO 3166-1 alpha-2 country code for a Country enum member.
    Args:
        country: The Country enum member to get the ISO code for.
    Returns:
        The ISO 3166-1 alpha-2 country code (e.g., "US", "CA", "MX") or None if the
        country is UNKNOWN or not found in the mapping.
    Examples:
        >>> get_iso_code(Country.USA)
        'US'
        >>> get_iso_code(Country.MEXICO)
        'MX'
        >>> get_iso_code(Country.UNKNOWN)
        None
    """
    return _ISO_CODES.get(country)
