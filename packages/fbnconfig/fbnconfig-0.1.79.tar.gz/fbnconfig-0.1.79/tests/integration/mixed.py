from fbnconfig import Deployment, drive, scheduler


def configure(env):
    deployment_name = getattr(env, "name", "mixed")

    client_folder = drive.FolderResource(id="base_folder", name=env.base_dir, parent=drive.root)
    files_folder = drive.FolderResource(id="files", name="files", parent=client_folder)
    content = """
    a little poem
        about ducks
            quack quack
    """
    data_file = drive.FileResource(id="file1", folder=files_folder, name="mydata.txt", content=content)
    version = 101
    docker_image = scheduler.ImageResource(
        id="img_mixed",
        source_image="harbor.finbourne.com/ceng/fbnconfig-pipeline:0.1",
        dest_name="beany_mixed",
        dest_tag=f"v{version}",
    )
    data_job = scheduler.JobResource(
        id="data_job",
        scope=deployment_name,
        code="mixed-job",
        image=docker_image,
        name="myjob",
        description="banana",
    )
    data_sched = scheduler.ScheduleResource(
        id="data_sch",
        name="my-schedule",
        scope=deployment_name,
        code="data-sched",
        job=data_job,
        expression="0 50 4 * * ? *",
        timezone="Europe/London",
        description="whatever",
    )
    return Deployment(
        deployment_name, [client_folder, files_folder, data_file, docker_image, data_job, data_sched]
    )


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
