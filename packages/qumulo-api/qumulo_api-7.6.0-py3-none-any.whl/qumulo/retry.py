# Copyright (c) 2023 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# XXX: Please add type parameters to all generics in this file!
# mypy: allow-any-generics


import functools
import logging
import random
import textwrap
import time
import traceback

from typing import Any, Callable, cast, Iterator, Optional, Tuple, Type, TypeVar, Union

log = logging.getLogger(__name__)


def exponential_backoff(
    base_sec: float,
    factor: float,
    max_backoff: float = 30.0,
    with_jitter: bool = False,
    random_func: Callable[[], float] = random.random,
) -> Iterator[float]:
    """
    Generator for calculating the amount of exponential back off sleep time
    with optional random jitter between 0 and the next amount of sleep time
    provided by the given iterator.

    For an explanation of why we would choose to use "full jitter" (i.e. 0 <=
    sleep_time <= next_backoff) as opposed to other jitter adjustments, see
    https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

    @param base_sec     The first backoff time in seconds
    @param factor       The factor by which to increase the amount of backoff
                        time for each iteration.
    @param max_backoff  The maximum amount of time between retries, defaulted to
                        30 seconds. For more information, see:
                        cloud.google.com/iot/docs/how-tos/exponential-backoff
    @param with_jitter  jitter the backoff randomly to avoid clustering of
                        retries across multiple callers
    @param random_func  The function to use to generate random numbers
                        in the range [0.0, 1.0)
    """

    jitter: Callable[[], float] = lambda: 1  # noqa: E731
    if with_jitter:
        jitter = random_func

    count = 0
    while True:
        yield jitter() * min(max_backoff, base_sec * factor**count)
        count += 1


F = TypeVar('F', bound=Callable)

ExceptionOrPredicate = Union[
    Type[Exception], Tuple[Type[Exception], ...], Callable[[Exception], bool]
]


def on_exception(
    exception_or_predicate: ExceptionOrPredicate,
    *,
    attempts: float = 3.0,  # XXX cwallace: this is float (not int) to allow for inf?
    delay_sec: float = 0.5,
    backoff: float = 1.0,
    max_backoff: float = 30.0,
    with_jitter: bool = False,
    on_retry: Optional[Callable[[], None]] = None,
) -> Callable[[F], F]:
    """
    Retries an operation using basic exponential backoff with optional jitter.

    @param exception_or_predicate   the exception type(s) on which to retry
                                    or a predicate function returning true to
                                    retry or false to raise the exception.

    @param attempts                 number of times to try before failing
    @param delay_sec                time to wait between attempts
    @param backoff                  delay multiplier for exponential backoff
    @param max_backoff              The maximum amount of time between attempts,
                                    defaulted to 30 seconds
    @param with_jitter              jitter the backoff randomly to avoid
                                    clustering of retries across multiple
                                    callers
    @param on_retry                 function to run between attempts
    """

    assert attempts > 0, attempts

    if isinstance(exception_or_predicate, (tuple, type)):
        callback_applies = lambda e: isinstance(e, exception_or_predicate)  # noqa: E731
    else:
        assert callable(exception_or_predicate)
        callback_applies = exception_or_predicate

    def retry_decorator(f: F) -> F:
        @functools.wraps(f)
        def retry_function(*args: Any, **kwargs: Any) -> Optional[Any]:
            outer_stack = traceback.extract_stack()
            backoff_generator = exponential_backoff(
                delay_sec, backoff, max_backoff=max_backoff, with_jitter=with_jitter
            )

            for attempt, sleep_time in enumerate(backoff_generator, 1):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    tabbed_outer_trace = textwrap.indent(
                        ''.join(traceback.format_list(outer_stack)), '\t'
                    )
                    tabbed_inner_trace = textwrap.indent(traceback.format_exc(), '\t')
                    log.debug(
                        f'attempt {attempt} from \n{tabbed_outer_trace}\nthrew'
                        f' exception:\n{tabbed_inner_trace}'
                    )

                    if not callback_applies(e) or attempt == attempts:
                        log.debug(f'Exception found was {e.__dict__}')
                        raise

                    if on_retry:
                        on_retry()

                time.sleep(sleep_time)

            return None  # Never reached

        return cast(F, retry_function)

    return retry_decorator
