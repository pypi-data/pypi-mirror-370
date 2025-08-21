from fbnconfig import Deployment, identity


def configure(env):
    application = identity.ApplicationResource(
        id="test_app",
        client_id="robTest-app-client",
        display_name="robTest Application",
        application_type=identity.ApplicationType.NATIVE,
    )
    return Deployment("application", [application])


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
