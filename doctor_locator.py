import requests
from bs4 import BeautifulSoup

doctor_speciality_map = {
    "anxiety": "psychology",
    "depression": "psychiatry",
    "schizophrenia": "psychiatry",
    "bipolar": "psychiatry",
    "mentalillness": "psychology",
    "bpd": "psychology"
}

# Fallback database for when Practo fails
FALLBACK_DOCTORS = {
    "delhi": [
        {
            "name": "VIMHANS (Vidyasagar Institute of Mental Health)",
            "specialty": "psychiatry",
            "address": "Institutional Area, Nehru Nagar, New Delhi - 110065",
            "phone": "011-26592222",
            "website": "http://www.vimhans.in",
            "lat": 28.5494,
            "lon": 77.2668
        },
        {
            "name": "IHBAS (Institute of Human Behaviour)",
            "specialty": "psychiatry",
            "address": "Dilshad Garden, Delhi - 110095",
            "phone": "011-22112222",
            "website": "http://www.ihbas.delhigovt.nic.in",
            "lat": 28.6863,
            "lon": 77.3191
        },
        {
            "name": "AIIMS Department of Psychiatry",
            "specialty": "psychiatry",
            "address": "Ansari Nagar, New Delhi - 110029",
            "phone": "011-26588500",
            "website": "https://www.aiims.edu",
            "lat": 28.5672,
            "lon": 77.2100
        },
        {
            "name": "Max Super Speciality Hospital - Psychiatry",
            "specialty": "psychiatry",
            "address": "Saket, New Delhi - 110017",
            "phone": "011-26515050",
            "website": "https://www.maxhealthcare.in",
            "lat": 28.5244,
            "lon": 77.2066
        },
        {
            "name": "Fortis Healthcare - Mental Health",
            "specialty": "psychiatry",
            "address": "Vasant Kunj, New Delhi - 110070",
            "phone": "011-42776222",
            "website": "https://www.fortishealthcare.com",
            "lat": 28.5200,
            "lon": 77.1600
        }
    ]
}

def get_doctors_for_disorder(disorder: str, city="Delhi"):
    disorder = disorder.lower().strip()
    speciality = doctor_speciality_map.get(disorder, "psychology")
    
    # Map to Practo search terms
    practo_speciality = "psychiatrist" if speciality == "psychiatry" else "psychologist"
    city_slug = city.lower().replace(" ", "-")
    
    doctors = []
    seen_names = set()  # Avoid duplicates
    
    try:
        # Practo URL for doctors
        url = f"https://www.practo.com/{city_slug}/{practo_speciality}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.practo.com/",
            "Connection": "keep-alive"
        }
        
        print(f"Fetching doctors from Practo: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors to find doctor cards (Practo's structure varies)
            doctor_cards = (
                soup.find_all('div', {'data-qa-id': 'doctor_card'}) or
                soup.find_all('div', class_=lambda x: x and 'listing-item' in str(x)) or
                soup.find_all('div', class_=lambda x: x and 'doctor-card' in str(x))
            )
            
            print(f"Found {len(doctor_cards)} doctor cards on Practo")
            
            for card in doctor_cards:
                try:
                    # Extract doctor name - try multiple selectors
                    name_elem = (
                        card.find('h2', {'data-qa-id': 'doctor_name'}) or
                        card.find('a', {'data-qa-id': 'doctor_name'}) or
                        card.find('h2', class_=lambda x: x and 'doctor-name' in str(x)) or
                        card.find('div', class_=lambda x: x and 'doctor-name' in str(x))
                    )
                    
                    if not name_elem:
                        continue
                    
                    name = name_elem.text.strip()
                    
                    # Skip duplicates and invalid names
                    if name in seen_names or name == "Unknown Doctor" or len(name) < 3:
                        continue
                    seen_names.add(name)
                    
                    # Extract clinic/practice name
                    clinic_elem = (
                        card.find('span', {'data-qa-id': 'practice_name'}) or
                        card.find('div', class_=lambda x: x and 'practice-name' in str(x)) or
                        card.find('span', class_=lambda x: x and 'clinic-name' in str(x))
                    )
                    clinic = clinic_elem.text.strip() if clinic_elem else ""
                    
                    # Extract locality/area
                    locality_elem = (
                        card.find('span', {'data-qa-id': 'practice_locality'}) or
                        card.find('span', class_=lambda x: x and 'locality' in str(x)) or
                        card.find('div', class_=lambda x: x and 'location' in str(x))
                    )
                    locality = locality_elem.text.strip() if locality_elem else city
                    
                    # Combine clinic and locality for address
                    address_parts = [p for p in [clinic, locality] if p]
                    address = ", ".join(address_parts) if address_parts else f"{city}"
                    
                    # Extract experience (optional)
                    exp_elem = card.find('span', {'data-qa-id': 'doctor_experience'})
                    experience = exp_elem.text.strip() if exp_elem else ""
                    
                    # Extract consultation fee (optional)
                    fee_elem = (
                        card.find('span', {'data-qa-id': 'consultation_fee'}) or
                        card.find('span', class_=lambda x: x and 'fee' in str(x))
                    )
                    fee = fee_elem.text.strip() if fee_elem else "Not available"
                    
                    # Extract phone (usually not shown, requires login)
                    phone = "Available on Practo (login required)"
                    
                    # Build doctor profile URL
                    doctor_link = card.find('a', href=True)
                    doctor_url = f"https://www.practo.com{doctor_link['href']}" if doctor_link else "https://www.practo.com"
                    
                    doctors.append({
                        "name": name,
                        "specialty": speciality,
                        "address": address,
                        "phone": phone,
                        "website": doctor_url,
                        "lat": None,  # Practo doesn't expose coordinates easily
                        "lon": None,
                        "experience": experience,
                        "fee": fee
                    })
                    
                except Exception as e:
                    print(f"Error parsing doctor card: {e}")
                    continue
            
            print(f"Successfully scraped {len(doctors)} doctors from Practo")
            
        else:
            print(f"Practo returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Practo scraping error: {e}")
    
    # Add fallback data if we got less than 3 results
    if len(doctors) < 3:
        print(f"Adding fallback doctors (found only {len(doctors)} from Practo)")
        city_lower = city.lower()
        fallback_list = FALLBACK_DOCTORS.get(city_lower, [])
        
        # Filter fallback by specialty
        if speciality in ["psychology", "psychiatry"]:
            filtered = [d for d in fallback_list if speciality in d["specialty"]]
            fallback_list = filtered if filtered else fallback_list
        
        for fallback_doc in fallback_list:
            if fallback_doc["name"] not in seen_names:
                seen_names.add(fallback_doc["name"])
                doctors.append(fallback_doc)
    
    print(f"Found {len(doctors)} mental health facilities total")
    return doctors[:15]  # Limit to 15 results


# Test the function
if __name__ == "__main__":
    results = get_doctors_for_disorder("anxiety")
    for doc in results[:5]:  # Show first 5 results
        print(f"\n{doc['name']}")
        print(f"  Address: {doc['address']}")
        print(f"  Phone: {doc['phone']}")