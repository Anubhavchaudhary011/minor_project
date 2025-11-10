import requests

# Mapping predicted disorder → doctor type
doctor_map = {
    "Anxiety": "Psychologist",
    "depression": "Psychiatrist",
    "schizophrenia": "Neuropsychiatrist",
    "bipolar": "Psychiatrist",
    "mentalillness": "Clinical Psychologist",
    "BPD": "Therapist"
}

def get_doctors_for_disorder(disorder, city="Delhi, India"):
    specialty = doctor_map.get(disorder, "Mental Health Specialist")

    # ✅ Correct OpenStreetMap query (your earlier query was wrong)
    query = f"{specialty} in {city}"

    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?q={query}&format=json&addressdetails=1&limit=5"
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "MentalHealthApp/1.0 (contact: test@example.com)"}
        )
        data = response.json()

        doctors = []
        for d in data:
            doctors.append({
                "name": specialty,
                "address": d.get("display_name", "Unknown"),
                "lat": d.get("lat"),
                "lon": d.get("lon")
            })

        return doctors

    except Exception as e:
        print("Error:", e)
        return []
