import requests

doctor_map = {
    "Anxiety": "Psychologist",
    "depression": "Psychiatrist",
    "schizophrenia": "Neuropsychiatrist",
    "bipolar": "Psychiatrist",
    "mentalillness": "Clinical Psychologist",
    "BPD": "Therapist"
}

def get_doctors(disorder, city="Delhi"):
    specialty = doctor_map.get(disorder, "Mental Health Doctor")

    url = f"https://nominatim.openstreetmap.org/search?q={specialty} near {city}&format=json&limit=5"

    r = requests.get(url, headers={"User-Agent": "MentalHealthApp"})
    data = r.json()

    doctors = [{
        "name": specialty,
        "address": d["display_name"]
    } for d in data]

    return doctors
