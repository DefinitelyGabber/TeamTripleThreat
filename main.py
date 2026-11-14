import requests
import urllib.parse
import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)

load_dotenv()
route_url = "https://graphhopper.com/api/1/route?"
key = os.getenv("GRAPHHOPPER_API_KEY")

def quit_app():
    print(Fore.CYAN + "\n" + "=" * 65)
    print(Fore.CYAN + "   Thank you for using Graphhopper Route Planner. Goodbye!")
    print(Fore.CYAN + "=" * 65 + "\n")
    sys.exit()

if not key:
    print(Fore.RED + "\n[!] API Key missing. Please check your .env file.\n")
    sys.exit()

THICK_LINE = Fore.BLUE + "=" * 65 + Style.RESET_ALL
THIN_LINE = Fore.BLUE + "-" * 65 + Style.RESET_ALL

def geocoding(location, key):
    while location.strip() == "":
        print(Fore.RED + "      [!] Location cannot be empty.")
        location = input(Fore.CYAN + "      ➔ " + Style.RESET_ALL)
    
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    try:
        replydata = requests.get(url, timeout=10)
        replydata.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"      [!] Network/API Error: {e}")
        return "error", "null", "null", location

    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data.get("hits", [])) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0].get("osm_value", "Unknown")
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        parts = [p for p in [name, state, country] if p]
        new_loc = ", ".join(parts)

        print(Fore.GREEN + f"      [+] Found: {new_loc} ({value})\n")
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        print(Fore.RED + f"      [!] Could not find '{location}'.\n")

    return json_status, lat, lng, new_loc

print("\n" + Fore.CYAN + "=" * 65)
print(Fore.CYAN + "                 WELCOME TO GRAPHHOPPER ROUTE PLANNER ")
print(Fore.CYAN + "=" * 65)

while True:
    print("\n" + THICK_LINE)
    print(Fore.YELLOW + "                       NEW ROUTE SETUP                         ")
    print(THICK_LINE)
    
    while True:
        print(Fore.WHITE + "\n  [?] Choose your unit preference (m = miles, k = kilometers, q = quit)")
        unit_pref = input(Fore.CYAN + "   ➔ " + Style.RESET_ALL).lower().strip()
        if unit_pref in ['q', 'quit']: quit_app()
        
        if unit_pref in ['m', 'miles', 'mile']: 
            use_miles = True
            break
        elif unit_pref in ['k', 'km', 'kilometers', 'kilometer']:
            use_miles = False
            break
        print(Fore.RED + "      [!] Invalid input. Please enter 'm' or 'k'.")

    while True:
        print(Fore.WHITE + "\n  [?] Choose a vehicle profile (car, bike, foot, or q = quit)")
        v_input = input(Fore.CYAN + "   ➔ " + Style.RESET_ALL).lower().strip()
        if v_input in ['q', 'quit']: quit_app()
        
        if v_input in ['c', 'car']: 
            vehicle = 'car'
            break
        elif v_input in ['b', 'bike', 'bicycle']: 
            vehicle = 'bike'
            break
        elif v_input in ['f', 'foot', 'walk']: 
            vehicle = 'foot'
            break
        print(Fore.RED + "      [!] Invalid profile. Please choose: car, bike, or foot.")

    print("\n" + THIN_LINE)
    
    while True:
        print(Fore.WHITE + "\n  [?] Starting Location (e.g., Manila, or q = quit)")
        loc1 = input(Fore.CYAN + "   ➔ " + Style.RESET_ALL).strip()
        if loc1.lower() in ['quit', 'q']: quit_app()
        orig = geocoding(loc1, key)
        if orig[0] != "error" and orig[1] != "null":
            break

    while True:
        print(Fore.WHITE + "  [?] Destination (e.g., Baguio, or q = quit)")
        loc2 = input(Fore.CYAN + "   ➔ " + Style.RESET_ALL).strip()
        if loc2.lower() in ['quit', 'q']: quit_app()
        dest = geocoding(loc2, key)
        if dest[0] != "error" and dest[1] != "null":
            break

    op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
    dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
    paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
    
    try:
        paths_reply = requests.get(paths_url, timeout=10)
        paths_reply.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"\n[!] Routing failed: {e}")
        continue

    paths_status = paths_reply.status_code
    paths_data = paths_reply.json()

    print("\n" + THICK_LINE)
    print(Fore.CYAN + f" NAVIGATION: {orig[3]} ➔ {dest[3]}")
    print(THICK_LINE)

    if paths_status == 200:
        distance_m = paths_data["paths"][0]["distance"]
        time_ms = paths_data["paths"][0]["time"]
        
        miles = (distance_m / 1000) / 1.60934
        km = distance_m / 1000
        
        sec = int(time_ms / 1000 % 60)
        min = int(time_ms / 1000 / 60 % 60)
        hr = int(time_ms / 1000 / 60 / 60)

        if use_miles:
            print(Fore.YELLOW + f" VEHICLE: {vehicle.upper():<6} | DISTANCE: {miles:.1f} mi | TIME: {hr:02d}:{min:02d}:{sec:02d}")
        else:
            print(Fore.YELLOW + f" VEHICLE: {vehicle.upper():<6} | DISTANCE: {km:.1f} km | TIME: {hr:02d}:{min:02d}:{sec:02d}")
            
        print(THIN_LINE)
        
        for step in paths_data["paths"][0]["instructions"]:
            path = step["text"]
            step_distance_m = step["distance"]
            
            if use_miles:
                step_dist = step_distance_m / 1000 / 1.60934
                unit = "mi"
            else:
                if step_distance_m < 1000:
                    step_dist = step_distance_m
                    unit = "m"
                else:
                    step_dist = step_distance_m / 1000
                    unit = "km"
                
            print(Fore.WHITE + f"  • {path:<45} " + Fore.LIGHTBLACK_EX + f"({step_dist:.1f} {unit})")
            
        print(THICK_LINE)
    else:
        print(Fore.RED + " [!] Routing error: " + paths_data.get("message", "Unknown error"))