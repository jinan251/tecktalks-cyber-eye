import pycountry
import phonenumbers
from phonenumbers.phonenumberutil import country_code_for_region

from fastapi import APIRouter

router = APIRouter()

@router.get("/countries")
def get_countries():

    countries = []

    for country in pycountry.countries:

        try:
            phone_code = country_code_for_region(country.alpha_2)

            # skip invalid countries
            if phone_code == 0:
                continue

            countries.append({
                "name": country.name,
                "iso": country.alpha_2,
                "code": str(phone_code)
            })

        except:
            continue

    return countries