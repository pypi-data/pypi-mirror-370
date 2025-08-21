from fbnconfig import Deployment, scheduler
from fbnconfig import workflows as wf


def configure(host_vars) -> Deployment:
    deployment_name = getattr(host_vars, "name", "workflows_test")
    tag = "v5.0"
    i = scheduler.ImageResource(
        id="img1",
        source_image="harbor.finbourne.com/ceng/fbnconfig-pipeline:0.1",
        dest_name="beany",
        dest_tag=tag,
    )
    job = scheduler.JobResource(
        id="job1",
        scope=deployment_name,
        code="jobwf",
        image=i,
        name="wfjob",
        description="something nice",
        min_cpu="1",
        max_cpu="2",
        argument_definitions={},
    )

    worker = wf.WorkerResource(
        id="wr3-example",
        scope=deployment_name,
        code="wr3",
        display_name="I am worker3",
        worker_configuration=wf.SchedulerJob(job=job),
    )

    pending_state = wf.TaskStateDefinition(name="pending")
    in_progress_state = wf.TaskStateDefinition(name="inprogress")
    end_state = wf.TaskStateDefinition(name="end")
    start_trigger = wf.TriggerDefinition(name="start", type="External")
    end_trigger = wf.TriggerDefinition(name="end", type="External")

    some_field = wf.TaskFieldDefinition(name="imafield", type=wf.TaskFieldDefinitionType.STRING)
    do_something_action = wf.ActionDefinition(
        name="start-something-worker",
        action_details=wf.RunWorkerAction(
            worker=worker,
            worker_parameters={},
            worker_status_triggers=wf.WorkerStatusTriggers(completed_with_results=end_trigger),
        ),
    )

    task_def = wf.TaskDefinitionResource(
        id="integrationtest-task-definition",
        scope=deployment_name,
        code="DoSomething",
        display_name="Does something",
        description="Task description",
        states=[pending_state, in_progress_state, end_state],
        field_schema=[some_field],
        initial_state=wf.InitialState(name=pending_state),
        triggers=[start_trigger, end_trigger],
        transitions=[
            wf.TaskTransitionDefinition(
                from_state=pending_state,
                to_state=in_progress_state,
                trigger=start_trigger,
                action=do_something_action,
            ),
            wf.TaskTransitionDefinition(
                from_state=in_progress_state, to_state=end_state, trigger=end_trigger
            ),
        ],
        actions=[do_something_action],
    )

    event_handler = wf.EventHandlerResource(
        id="integrationtest-eventhandler",
        scope=deployment_name,
        code="testeventhandler",
        display_name="new name",
        description="something",
        status=wf.EventStatus.INACTIVE,
        event_matching_pattern=wf.EventMatchingPattern(
            event_type="FileCreated",
            filter="body.filePath startswith '/somedomain/quotes'"),
        run_as_user_id=wf.EventHandlerMapping(
            map_from="header.userId"
        ),
        task_definition=task_def,
        task_activity=wf.CreateNewTaskActivity(
            correlation_ids=[wf.EventHandlerMapping(set_to="int-test")],
            task_fields={
                some_field: wf.FieldMapping(map_from="body.filePath")  # pyright: ignore
            },
            initial_trigger=start_trigger
        )
    )

    return Deployment(deployment_name, [event_handler])


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
