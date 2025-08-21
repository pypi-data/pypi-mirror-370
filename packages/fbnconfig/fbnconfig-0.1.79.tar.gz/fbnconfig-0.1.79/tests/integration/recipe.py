import pathlib

from fbnconfig import Deployment, recipe


def configure(env):
    deployment_name = getattr(env, "name", "recipe")

    recipe_from_dict = recipe.RecipeResource(
        id="recipe1",
        scope="sc1",
        code="cd1",
        recipe={
            "market": {
                "marketRules": [
                    {
                        "key": "Fx.CurrencyPair.*",
                        "supplier": "DataScope",
                        "dataScope": "SomeScopeToLookAt",
                        "quoteType": "Rate",
                        "field": "Mid",
                        "priceSource": "",
                        "sourceSystem": "Lusid",
                    }
                ],
                "suppliers": {},
                "options": {
                    "defaultSupplier": "Lusid",
                    "defaultInstrumentCodeType": "LusidInstrumentId",
                    "defaultScope": "default",
                    "attemptToInferMissingFx": False,
                    "calendarScope": "CoppClarkHolidayCalendars",
                    "conventionScope": "Conventions",
                },
                "specificRules": [],
                "groupedMarketRules": [],
            },
            "pricing": {
                "modelRules": [],
                "modelChoice": {},
                "options": {
                    "modelSelection": {"library": "Lusid", "model": "SimpleStatic"},
                    "useInstrumentTypeToDeterminePricer": False,
                    "allowAnyInstrumentsWithSecUidToPriceOffLookup": False,
                    "allowPartiallySuccessfulEvaluation": False,
                    "produceSeparateResultForLinearOtcLegs": False,
                    "enableUseOfCachedUnitResults": False,
                    "windowValuationOnInstrumentStartEnd": False,
                    "removeContingentCashflowsInPaymentDiary": False,
                    "useChildSubHoldingKeysForPortfolioExpansion": False,
                    "validateDomesticAndQuoteCurrenciesAreConsistent": False,
                    "conservedQuantityForLookthroughExpansion": "PV",
                },
                "resultDataRules": [],
            },
            "aggregation": {
                "options": {
                    "useAnsiLikeSyntax": False,
                    "allowPartialEntitlementSuccess": False,
                    "applyIso4217Rounding": False,
                }
            },
            "description": "",
            "holding": {"taxLotLevelHoldings": True},
        },
    )

    configuration_recipe_from_drive = recipe.RecipeResource(
        id="recipe2",
        scope="sc1",
        code="cd2",
        recipe=pathlib.Path(__file__).parent.resolve() / pathlib.Path("./recipe.json"),
    )

    return Deployment(deployment_name, [recipe_from_dict, configuration_recipe_from_drive])


if __name__ == "__main__":
    import os

    import click

    import fbnconfig

    @click.command()
    @click.argument("lusid_url", envvar="LUSID_ENV", type=str)
    @click.option("-v", "--vars_file", type=click.File("r"))
    def cli(lusid_url, vars_file):
        host_vars = fbnconfig.load_vars(vars_file)
        d = configure(host_vars)
        fbnconfig.deploy(d, lusid_url, os.environ["FBN_ACCESS_TOKEN"])

    cli()
