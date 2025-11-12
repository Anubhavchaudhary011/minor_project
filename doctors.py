import requests

doctor_map = {
    "Anxiety": "Psychologist",
    "depression": "Psychiatrist",
    "schizophrenia": "Neuropsychiatrist",
    "bipolar": "Psychiatrist",
    "mentalillness": "Clinical Psychologist",
    "BPD": "Therapist"
}

def get_doctors_for_disorder(disorder: str, city="Delhi, India"):
    specialty = doctor_map.get(disorder, "Mental Health Doctor")
    url = (
        f"https://nominatim.openstreetmap.org/search?"
        f"q={specialty} near {city}&format=json&limit=5"
    )
    try:
        data = requests.get(url, headers={"User-Agent": "MentalHealthApp"}).json()
        return [{"name": specialty, "address": d.get("display_name", "")} for d in data]
    except Exception:
        return []
