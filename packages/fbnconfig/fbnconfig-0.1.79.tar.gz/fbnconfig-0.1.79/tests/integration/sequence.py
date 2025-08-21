from fbnconfig import Deployment, sequence


def configure(env):
    deployment_name = getattr(env, "name", "seq_example")
    seq1 = sequence.SequenceResource(id="seq1", scope=deployment_name, code="seq1")
    return Deployment(deployment_name, [seq1])


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
