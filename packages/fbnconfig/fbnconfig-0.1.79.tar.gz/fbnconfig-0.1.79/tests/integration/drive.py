import pathlib

from fbnconfig import Deployment, drive


def configure(env):
    deployment_name = getattr(env, "name", "folders")
    base_folder = getattr(env, "base_dir", "folder")

    f1 = drive.FolderResource(id="base_folder", name=base_folder, parent=drive.root)
    f2 = drive.FolderResource(id="sub_folder", name="subfolder", parent=f1)
    f3 = drive.FolderResource(id="sub_sub_folder", name="subfolder2", parent=f2)
    content_path = pathlib.Path(__file__).parent.resolve() / pathlib.Path("poem.txt")
    ff = drive.FileResource(id="file1", folder=f3, name="myfile.txt", content_path=content_path)
    return Deployment(deployment_name, [f1, f2, f3, ff])


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
