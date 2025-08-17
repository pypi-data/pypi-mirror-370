MOBILE_PHONE = r"(?P<mobile_phone>\d{3}\s?\d{3}\s?\d{3})"

_STREET = r"(?P<street>(?:ul\.|al\.|pl\.|os\.|ulica|aleja|plac)\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:[\s-][A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+)*)"

_ZIP_CODE = r"(?P<zip_code>\d{2}-\d{3})"

_BUILDING = r"(?P<building>\d+[A-Za-z]?)"

_APARTMENT = rf"(?<=\b{_BUILDING}[ /])(?P<apartment>\d+[A-Za-z]?)"

_WORD = r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:-[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+)*"
_CONNECT = r"(?:nad|pod|przy|w|we|koło)"
_TOKEN = rf"(?:{_WORD}|{_CONNECT})"

_CITY = rf"(?P<city>{_TOKEN}(?:[ -]{_TOKEN}){{0,4}})"

_CITY_0 = rf"(?<=\b{_ZIP_CODE}[\s,]+){_CITY}"

_CITY_1 = rf"{_CITY}(?=\s+{_BUILDING}\b)(?=.*?\b{_ZIP_CODE}\b)"

_ADDRESS_0 = (
    rf"(?s)^"
    rf"(?=.*?"
    rf"{_STREET}"
    rf"\s+{_BUILDING}"
    rf"(?:[ /]{_APARTMENT})?"
    rf"\s*,?\s*"
    rf"{_ZIP_CODE}"
    rf"[\s,]+{_CITY_0}"
    rf")"
)

_ADDRESS_1 = (
    rf"(?s)^"
    rf"(?=.*?"
    rf"{_CITY_1}"
    rf"\s+{_BUILDING}"
    rf"(?:[ /]{_APARTMENT})?"
    rf"\s*,?\s*"
    rf"{_ZIP_CODE}"
    rf")"
)

ADDRESS = rf"(?x)(?|{_ADDRESS_0}|{_ADDRESS_1})"
