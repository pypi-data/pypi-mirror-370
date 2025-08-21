from fbnconfig import Deployment, datatype, property


def configure(env):
    deployment_name = getattr(env, "name", "property")

    df = property.DefinitionRef(
        id="property/dfdomccy", domain=property.Domain.Holding, scope="default", code="DfDomCcy"
    )
    nominal = property.DefinitionRef(
        id="property/nominal", domain=property.Domain.Holding, scope="default", code="Nominal"
    )
    rating = property.DefinitionResource(
        id="rating",
        domain=property.Domain.Instrument,
        scope=deployment_name,
        code="rating",
        display_name="robtest rating ",
        data_type_id=datatype.DataTypeRef(id="default_str", scope="system", code="string"),
        constraint_style=property.ConstraintStyle.Collection,
        property_description="robTest property",
        life_time=property.LifeTime.Perpetual,
        collection_type=property.CollectionType.Array,
    )
    pd = property.DefinitionResource(
        id="pd1",
        domain=property.Domain.Instrument,
        scope=deployment_name,
        code="pd1",
        display_name="robtest pd ",
        data_type_id=property.ResourceId(scope="system", code="number"),
        constraint_style=property.ConstraintStyle.Property,
        property_description="robTest property",
        life_time=property.LifeTime.Perpetual,
        collection_type=None,
    )
    pv_nominal = property.DefinitionResource(
        id="derived",
        domain=property.Domain.Holding,
        data_type_id=property.ResourceId(scope="system", code="number"),
        scope=deployment_name,
        code="PVNominal",
        property_description="nominal_x_df",
        display_name="DF Nominal",
        derivation_formula=property.Formula("{x} * {y}", x=df, y=nominal),
        is_filterable=False,
    )
    more_derived = property.DefinitionResource(
        id="derived_more",
        domain=property.Domain.Holding,
        data_type_id=property.ResourceId(scope="system", code="number"),
        scope=deployment_name,
        code="more_derived",
        property_description="pd1 x df x nominal",
        display_name="DF Nominal pd1",
        derivation_formula=property.Formula("{x} * {y}", x=pv_nominal, y=pd),
        is_filterable=True,
    )

    return Deployment(deployment_name, [pd, df, nominal, pv_nominal, more_derived, rating])


if __name__ == "__main__":
    import os

    import click

    import fbnconfig

    @click.command()
    @click.argument("lusid_url", type=str)
    @click.option("-v", "--vars_file", type=click.File("r"))
    def cli(lusid_url, vars_file):
        host_vars = fbnconfig.load_vars(vars_file)
        d = configure(host_vars)
        fbnconfig.deploy(d, lusid_url, os.environ["FBN_ACCESS_TOKEN"])

    cli()
