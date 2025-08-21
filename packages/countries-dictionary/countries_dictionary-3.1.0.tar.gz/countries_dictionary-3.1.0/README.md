# Countries Dictionary
Countries Dictionary provides: 
- A dictionary contains all members and observer states of the United Nations and information about them:
    - Formal name
    - Continent(s) of the country's mainland
    - Area and land area (in square kilometre)
    - Population
    - Official language(s)
    - Nominal GDP (in dollar)
    - Human Development Index
    - ISO 3166-1 codes
- Another dictionary contains all federal subjects of the Russian Federation (including occupied zones in Ukraine) and information about them:
    - Federal district
    - Economic region
    - Capital or administrative centre
    - Area (in square kilometre)
    - Population
- Another one contains all provinces and municipalities of the Socialist Republic of Vietnam and information about them:
    - Region
    - Administrative centre
    - Area (in square kilometre)
    - Population
- Another one contains all states, federal district and inhabited territories of the United Nations and information about them:
    - Capital
    - Date of ratification/establishment/acquiring
    - Area (in square kilometre)
    - Population
    - House Representatives
    - Postal code
- Some functions which you might find helpful

I created this module as an offline source of countries' information which is easy to access and use by coders.

See [CHANGELOG.md](https://github.com/ThienFakeVN/countries_dictionary/blob/main/CHANGELOG.md) for changes of releases.

Before using, it is recommended to see the code on [GitHub](https://github.com/ThienFakeVN/countries_dictionary/) or the below section to understand how the module works and how you can use it

## Codes
### Main Countries Dictionary
#### Structure
The Countries Dictionary has a structure like this:
```python
COUNTRIES = {
    "Afghanistan": {
        "formal name": "Islamic Emirate of Afghanistan",
        "continents": ["Asia"],
        "area": 652864.0,
        "land area": 652230.0,
        "population": 42045000,
        "official languages": ["Dari", "Pashto"],
        "nominal GDP": 16417000000,
        "HDI": 0.496,
        "ISO 3166-1": {"alpha-2": "AF", "alpha-3": "AFG", "numeric": "004"},
    },
    # ...
}
```

#### Usage example
```python
from countries_dictionary import COUNTRIES # Remember to import the module!

# Prints the formal name of the country
print(COUNTRIES["Vietnam"]["formal name"])

# Compares the population of two countries
print(COUNTRIES["North Korea"]["population"] > COUNTRIES["South Korea"]["population"])
print(COUNTRIES["North Korea"]["population"] == COUNTRIES["South Korea"]["population"])
print(COUNTRIES["North Korea"]["population"] < COUNTRIES["South Korea"]["population"])

# Creates the list of all countries
list_of_countries = list(COUNTRIES.keys())
print(list_of_countries)
```

### Russia dictionary
#### Structure
The Russia dictionary has a structure like this:
```python
RUSSIA = {
    "Adygea": {
        "federal district": "Southern",
        "economic region": "North Caucasus",
        "capital/administrative centre": "Maykop",
        "area": 7792.0,
        "population": 501038},
    # ...
}
```

#### Usage example
```python
from countries_dictionary.russia import RUSSIA # Remember to import the module

# Prints the administrative centre of a krai
print(RUSSIA["Primorsky Krai"]["capital/administrative centre"])

# Sees if the two federal subjects are in the same federal district
print(RUSSIA["Tuva"]["federal district"] == RUSSIA["Altai Republic"]["federal district"])

# Creates the list of all federal subjects
list_of_federal_subjects = list(RUSSIA.keys())
print(list_of_federal_subjects)
```

### United States dictionary
#### Structure
The United States dictionary has a structure like this:
```python
UNITED_STATES = {
    "Alabama": {
        "capital": "Montgomery",
        "date of ratification/establishment/acquiring": "1819.12.14",
        "area": 135767.0,
        "population": 5024279,
        "House Representatives": 7,
        "postal code": "AL",
    }
    # ...
}
```

#### Usage example
```python
from countries_dictionary.united_states import UNITED_STATES # Remember to import the module...

# Prints the postal code of a state
print(UNITED_STATES["Ohio"]["postal code"])

# Compares the numbers of House Representatives of two states
print(UNITED_STATES["Oklahoma"]["House Representatives"] > UNITED_STATES["Connecticut"]["House Representatives"])
print(UNITED_STATES["Oklahoma"]["House Representatives"] == UNITED_STATES["Connecticut"]["House Representatives"])
print(UNITED_STATES["Oklahoma"]["House Representatives"] < UNITED_STATES["Connecticut"]["House Representatives"])

# Creates the list of all states
list_of_states = list(UNITED_STATES.keys())
print(list_of_states)
```

### Vietnam dictionary
#### Structure
The Vietnam dictionary has a structure like this:
```python
VIETNAM = {
    "Hanoi": {
        "region": "Red River Delta",
        "administrative centre": "Hoàn Kiếm ward",
        "area": 3359.84,
        "population": 8807523},
    # ...
}
```

#### Usage example
```python
from countries_dictionary.vietnam import VIETNAM # Of course...

# Prints the population of a province
print(VIETNAM["Ho Chi Minh City"]["population"])

# Sees if the two provinces are in the same region
print(VIETNAM["Nghệ An province"]["region"] == VIETNAM["Hà Tĩnh province"]["region"])

# Creates the list of all provinces
list_of_provinces = list(VIETNAM.keys())
print(list_of_provinces)
```

### Quick functions
There are many functions in this submodule.
```python
import countries_dictionary.quick_functions as qf # What have you expected?

# Converts the dictionary into JSON and creates/overwrites a JSON file which contains the converted dictionary
with open("countries_dictionary.json", "w") as f:
    f.write(qf.json_dictionary(indent=4))

# Prints a ISO 3166-2 code of a country
iso = qf.countries_iso_3166_2()
print(iso["Russia"]["ISO 3166-2"])
```

### ISO finder
*ISO finder* is a module which provides a function which has the same name. *ISO finder* can find a country based on the provided ISO code. Note that it does not include US states' postal codes.
```python
from countries_dictionary.iso_finder import iso_finder

print(iso_finder("VN"))
print(iso_finder("RUS"))
print(iso_finder("840"))
```
