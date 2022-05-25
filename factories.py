import models


FILING_TYPES = {
    "employe": models.Employe,
    "pensioner": models.Pensioner,
    "independentserviceprovider": models.IndependentServiceProvider,
    "independentcapitalannuitant": models.IndependentCapitalAnnuitant,
    "independentbusinessowner": models.IndependentBusinessOwner,
    "independentdriver": models.IndependentDriver,
}


class FilingFactory:
    @staticmethod
    def get_filing(profile):
        if not profile.get("type"):
            raise Exception("The type field is required")

        if profile.get("type") not in FILING_TYPES:
            raise Exception("Profile type not found")

        Filing = FILING_TYPES[profile.get("type")]
        return Filing(**profile)
