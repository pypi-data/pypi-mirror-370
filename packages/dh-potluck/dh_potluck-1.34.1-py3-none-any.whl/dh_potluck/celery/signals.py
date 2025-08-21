from ddtrace import tracer

from dh_potluck.utils import get_arg_names

try:
    from celery.signals import task_prerun

    @task_prerun.connect
    def celer_task_prerun(task_id, task, args, **kwargs):
        # This will add the args specified in the celery task "dd_args" argument and add
        # them as tags to the current trace.

        if current_span := tracer.current_span():
            arg_names = get_arg_names(task.run)
            arg_values = dict(zip(arg_names, task.request.args or []), **task.request.kwargs)

            for arg in getattr(task, 'dd_args', []):
                if arg in arg_values:
                    current_span.set_tag(f'celery.task_args.{arg}', arg_values[arg])

except ModuleNotFoundError:
    pass
