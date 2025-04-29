import pandas as pd
import networkx as nx
import random
from faker import Faker
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopy # Import geopy exceptions
import time
import folium # For visualization
import warnings

# Ignore specific warnings from geopy or others if necessary
warnings.filterwarnings("ignore", category=UserWarning, module='geopy')

# --- 1. Konstanten und feste Standorte definieren ---
RETAILER_LOCATION = "Gelsenkirchen"
WHOLESALER_LOCATION = "Düsseldorf"
# Repräsentative Orte für die Weinregionen
WINERY_MOSEL_LOCATION = "Bernkastel-Kues" # Typischer Ort an der Mosel
WINERY_RHEINGAU_LOCATION = "Rüdesheim am Rhein" # Typischer Ort im Rheingau
N_CUSTOMERS = 20 # Anzahl der zu generierenden Kunden

# --- 2. Geocoding vorbereiten ---
# Wichtig: Ein eindeutiger User-Agent ist für Nominatim erforderlich
# Timeout erhöht, um Fehler bei langsamer Antwort des Servers zu vermeiden
geolocator = Nominatim(user_agent="my_supply_chain_app_v1_longer_timeout", timeout=15) # z.B. 15 Sekunden Timeout

# RateLimiter verhindert, dass wir zu schnell Anfragen senden (gut für APIs)
# error_wait_seconds fügt eine Pause nach einem Fehler hinzu
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=5.0, max_retries=2, swallow_exceptions=False)

def get_coordinates(city_name):
    """ Versucht, Koordinaten für einen Stadtnamen zu bekommen. """
    try:
        # Timeout wird jetzt vom Nominatim-Objekt gehandhabt
        location = geocode(city_name + ", Deutschland")
        if location:
            # print(f"Koordinaten für {city_name} gefunden: ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude)
        else:
            print(f"Warnung: Keine Koordinaten für {city_name} gefunden.")
            return None
    # Fangen spezifischer Geopy-Fehler und anderer potenzieller Probleme
    except (geopy.exc.GeocoderServiceError, geopy.exc.GeocoderTimedOut, geopy.exc.GeocoderUnavailable) as e:
        print(f"Geocoding Fehler für {city_name} (Service/Timeout): {e}")
        return None
    except Exception as e:
        print(f"Allgemeiner Fehler beim Geocoding für {city_name}: {e}")
        return None

# --- 3. Feste Standorte geocoden ---
print("Geocodiere feste Standorte...")
locations = {
    "Retailer": (RETAILER_LOCATION, get_coordinates(RETAILER_LOCATION)),
    "Wholesaler": (WHOLESALER_LOCATION, get_coordinates(WHOLESALER_LOCATION)),
    "Winery_Mosel": (WINERY_MOSEL_LOCATION, get_coordinates(WINERY_MOSEL_LOCATION)),
    "Winery_Rheingau": (WINERY_RHEINGAU_LOCATION, get_coordinates(WINERY_RHEINGAU_LOCATION)),
}

# Überprüfen, ob alle festen Standorte gefunden wurden
critical_locations_ok = True
for name, (city, coords) in locations.items():
    if coords is None:
        print(f"FEHLER: Kritischer Standort {name} ({city}) konnte nicht geocodet werden.")
        critical_locations_ok = False

if not critical_locations_ok:
     print("Abbruch wegen fehlender kritischer Standorte.")
     exit()

print("Feste Standorte erfolgreich geocodet.")

# --- 4. Zufällige Kundendaten generieren ---
print(f"Generiere {N_CUSTOMERS} zufällige Kunden...")
fake = Faker('de_DE') # Deutsche Daten verwenden
customer_data = []

# Liste bekannter deutscher Städte
common_german_cities = [
    'Berlin', 'Hamburg', 'München', 'Köln', 'Frankfurt am Main', 'Stuttgart',
    'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig', 'Bremen', 'Dresden',
    'Hannover', 'Nürnberg', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld',
    'Bonn', 'Münster', 'Karlsruhe', 'Mannheim', 'Augsburg', 'Wiesbaden',
    'Gelsenkirchen', 'Mönchengladbach', 'Braunschweig', 'Chemnitz', 'Kiel',
    'Aachen', 'Halle (Saale)', 'Magdeburg', 'Freiburg im Breisgau', 'Krefeld',
    'Lübeck', 'Oberhausen', 'Erfurt', 'Mainz', 'Rostock', 'Kassel',
    'Hagen', 'Hamm', 'Saarbrücken', 'Mülheim an der Ruhr', 'Potsdam',
    'Ludwigshafen am Rhein', 'Oldenburg', 'Leverkusen', 'Osnabrück', 'Solingen',
    'Heidelberg', 'Herne', 'Neuss', 'Darmstadt', 'Paderborn', 'Regensburg',
    'Ingolstadt', 'Würzburg', 'Fürth', 'Wolfsburg', 'Ulm', 'Offenbach am Main',
    'Heilbronn', 'Pforzheim', 'Göttingen', 'Bottrop', 'Trier', 'Recklinghausen',
    'Reutlingen', 'Bremerhaven', 'Koblenz', 'Bergisch Gladbach', 'Jena',
    'Remscheid', 'Erlangen', 'Moers', 'Siegen', 'Hildesheim', 'Salzgitter'
]

# Sicherstellen, dass wir genügend eindeutige Städte haben
if N_CUSTOMERS <= len(common_german_cities):
    customer_cities = random.sample(common_german_cities, N_CUSTOMERS)
else:
    customer_cities = random.choices(common_german_cities, k=N_CUSTOMERS)
    print(f"Warnung: Mehr Kunden ({N_CUSTOMERS}) als eindeutige Städte ({len(common_german_cities)}) benötigt. Städte werden wiederholt.")


for i in range(N_CUSTOMERS):
    customer_id = f"Customer_{i+1}"
    city = customer_cities[i]
    demand = random.randint(1, 12) # Zufällige Nachfrage
    print(f"Versuche Geocoding für Kunde {i+1}/{N_CUSTOMERS} in {city}...")
    coords = get_coordinates(city)
    if coords: # Nur Kunden hinzufügen, deren Ort gefunden wurde
        customer_data.append({
            "id": customer_id,
            "city": city,
            "demand": demand,
            "latitude": coords[0],
            "longitude": coords[1]
        })
    else:
         print(f"Warnung: Kunde in {city} wird übersprungen (keine Koordinaten).")
    # Die Pause wird jetzt durch RateLimiter gehandhabt, time.sleep() hier nicht unbedingt nötig

customers_df = pd.DataFrame(customer_data)
print(f"{len(customers_df)} von {N_CUSTOMERS} Kunden erfolgreich generiert und geocodet.")

# --- 5. Netzwerk-Graph erstellen (NetworkX) ---
G = nx.DiGraph() # Gerichteter Graph

# Knoten hinzufügen (mit Attributen für spätere Verwendung/Visualisierung)
# Wichtig: pos als (longitude, latitude) speichern
G.add_node("Winery_Mosel", type="Winery", city=locations["Winery_Mosel"][0], pos=(locations["Winery_Mosel"][1][1], locations["Winery_Mosel"][1][0]))
G.add_node("Winery_Rheingau", type="Winery", city=locations["Winery_Rheingau"][0], pos=(locations["Winery_Rheingau"][1][1], locations["Winery_Rheingau"][1][0]))
G.add_node("Wholesaler", type="Wholesaler", city=locations["Wholesaler"][0], pos=(locations["Wholesaler"][1][1], locations["Wholesaler"][1][0]))
G.add_node("Retailer", type="Retailer", city=locations["Retailer"][0], pos=(locations["Retailer"][1][1], locations["Retailer"][1][0]))

# Kundenknoten hinzufügen
for index, customer in customers_df.iterrows():
    G.add_node(customer['id'], type="Customer", city=customer['city'], demand=customer['demand'], pos=(customer['longitude'], customer['latitude']))

# Kanten hinzufügen (Lieferwege)
G.add_edge("Winery_Mosel", "Wholesaler", percentage=0.20)
G.add_edge("Winery_Rheingau", "Wholesaler", percentage=0.80)
G.add_edge("Wholesaler", "Retailer")
for customer_id in customers_df['id']:
    G.add_edge("Retailer", customer_id)

print("\nNetzwerk Graph erstellt:")
print(f"Anzahl Knoten: {G.number_of_nodes()}")
print(f"Anzahl Kanten: {G.number_of_edges()}")

# --- 6. Netzwerk visualisieren (Folium auf Deutschlandkarte) ---
print("\nErstelle Visualisierung mit Folium...")

map_center = [51.1657, 10.4515] # Ungefähre Mitte Deutschlands
map_zoom = 6

m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB positron")

# Farben und Icons für verschiedene Knotentypen
node_colors = {
    "Winery": "darkred",
    "Wholesaler": "orange",
    "Retailer": "blue",
    "Customer": "green"
}
node_icons = {
    "Winery": "industry",
    "Wholesaler": "truck",
    "Retailer": "shopping-cart",
    "Customer": "user"
}


# Knoten zur Karte hinzufügen
for node, data in G.nodes(data=True):
    if 'pos' in data and data['pos'] is not None:
        lon, lat = data['pos']
        node_type = data.get('type', 'Unknown')
        color = node_colors.get(node_type, 'gray')
        icon = node_icons.get(node_type, 'circle')

        popup_text = f"<b>{node}</b> ({node_type})<br>City: {data.get('city', 'N/A')}"
        if node_type == 'Customer':
            popup_text += f"<br>Demand: {data.get('demand', 'N/A')} Flaschen"

        folium.Marker(
            location=[lat, lon], # Folium braucht [lat, lon]
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=node,
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    else:
        print(f"Warnung: Knoten {node} hat keine Positionsdaten und wird nicht gezeichnet.")


# Kanten zur Karte hinzufügen
for u, v, data in G.edges(data=True):
    pos_u = G.nodes[u].get('pos')
    pos_v = G.nodes[v].get('pos')

    if pos_u and pos_v:
        # NetworkX pos ist (lon, lat), Folium braucht [(lat, lon), (lat, lon)]
        points = [(pos_u[1], pos_u[0]), (pos_v[1], pos_v[0])]

        line_color = "gray"
        line_weight = 1.5
        line_opacity = 0.6

        # Kantenfarben basierend auf Startknoten-Typ
        start_node_type = G.nodes[u].get('type')
        if start_node_type == 'Winery':
             line_color = 'darkred'
             line_weight = 2
             line_opacity = 0.7
        elif start_node_type == 'Wholesaler':
             line_color = 'orange'
             line_weight = 2
             line_opacity = 0.7
        elif start_node_type == 'Retailer':
             line_color = 'blue'
             line_weight = 1
             line_opacity = 0.5

        edge_tooltip = f"{u} -> {v}" + (f" ({data['percentage']*100:.0f}%)" if 'percentage' in data else "")
        folium.PolyLine(
            locations=points,
            color=line_color,
            weight=line_weight,
            opacity=line_opacity,
            tooltip=edge_tooltip
        ).add_to(m)

# Karte speichern
map_filename = 'liefernetz_karte.html'
m.save(map_filename)
print(f"\nVisualisierung wurde als '{map_filename}' gespeichert. Öffnen Sie diese Datei in einem Webbrowser.")