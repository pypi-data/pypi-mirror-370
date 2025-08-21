from ddtrace.filters import TraceFilter


class ErrorFilter(TraceFilter):
    """
    See https://ddtrace.readthedocs.io/en/stable/troubleshooting.html
    #root-span-is-missing-error-details
    """

    def process_trace(self, trace):
        # Find first child span with an error and copy its error details to root span
        if not trace:
            return trace

        local_root = trace[0]
        try:
            status_code = int(local_root.get_tag('http.status_code'))
        except (ValueError, TypeError):
            status_code = 0

        if status_code >= 500:
            for span in trace[1:]:
                if span.error == 1:
                    local_root.error = 1
                    local_root.set_tags(
                        {
                            'error.msg': span.get_tag('error.msg'),
                            'error.type': span.get_tag('error.type'),
                            'error.stack': span.get_tag('error.stack'),
                        }
                    )
                    break

        return trace
