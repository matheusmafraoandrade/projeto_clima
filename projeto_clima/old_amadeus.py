#cities_api_key = "6kJtGwr4zOzUffuJRSXZwhEhVG0j"
#weather_api_key = "aabc6ce5b9f965907122e09b02b1ac95"

@st.experimental_fragment()
def get_token():
    cities_api_key = "9fxIgrGxNnIChovLLn1yDll05cRT08ug"
    cities_secret = "HyQlPubKbHkUAtpm"
    
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    token_headers = { "Content-Type": "application/x-www-form-urlencoded" }
    token_data = {
        "grant_type": "client_credentials",
        "client_id": cities_api_key,
        "client_secret": cities_secret
    }
    response = requests.post(token_url, headers=token_headers, data=token_data)
    token = response.json()['access_token']
    return token

@st.experimental_fragment()
def get_cities(search_string):
    token = get_token()
    url = 'https://test.api.amadeus.com/v1/reference-data/locations/cities'
    headers = { 'accept': 'application/vnd.amadeus+json', 'Authorization': f'Bearer {token}' }
    params = { 'keyword': search_string, 'max': 5 }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@st.experimental_fragment()
def list_cities(search_string):
    cidades = []
    coordenadas = []
    
    data = get_cities(search_string)['data']
    for loc in range(len(data)):
        nome = data[loc]['name']
        if 'ZZZ' in data[loc]['address']['stateCode']:
            regiao = data[loc]['address']['countryCode']
        else:
            regiao = data[loc]['address']['stateCode']
        
        cidade = f"{nome}, {regiao}"
        lat = data[loc]['geoCode']['latitude']
        lon = data[loc]['geoCode']['longitude']
        
        cidades.append(cidade)
        coordenadas.append((lat, lon))
    
    result = list(zip(cidades, coordenadas))
    return result