from tenacity.stop import stop_base
from tenacity import retry, retry_if_exception, after_log, wait_exponential, before_sleep_log, RetryCallState
from pmsintegration.platform import concurrent_utils

class stop_when_halt_requested(stop_base):  # noqa
    """Stop when the given event is set."""
    def __call__(self, retry_state: "RetryCallState") -> bool:
        return concurrent_utils.halt_requested()


class RetryableGrpcException(Exception):
    pass


def retryable_grpc_exception(exception):
    return isinstance(exception, RetryableGrpcException)


__all__ = [retry, retry_if_exception, after_log, wait_exponential, before_sleep_log]
