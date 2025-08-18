from countries_dictionary import COUNTRIES

def iso_finder(code: str):
    for x in COUNTRIES:
        if code == COUNTRIES[x]["ISO 3166-1"]["alpha-2"]: return f"{x} — {COUNTRIES[x]["formal name"]}"
        else:
            if code == COUNTRIES[x]["ISO 3166-1"]["alpha-3"]: return f"{x} — {COUNTRIES[x]["formal name"]}"
            else:
                if code == COUNTRIES[x]["ISO 3166-1"]["numeric"]: return f"{x} — {COUNTRIES[x]["formal name"]}"
    raise Exception("No United Nations' member or observer state has this code")