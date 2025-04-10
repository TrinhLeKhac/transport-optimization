import contextlib
import io
import re
import sys
import threading

import streamlit as st


class _Redirect:
    class IOStuff(io.StringIO):
        def __init__(
            self, trigger, max_buffer, buffer_separator, regex, dup, need_dup, on_thread
        ):
            super().__init__()
            self._trigger = trigger
            self._max_buffer = max_buffer
            self._buffer_separator = buffer_separator
            self._regex = regex and re.compile(regex)
            self._dup = dup
            self._need_dup = need_dup
            self._on_thread = on_thread

        def write(self, __s: str) -> int:
            res = None
            if self._on_thread == threading.get_ident():
                if self._max_buffer:
                    concatenated_len = super().tell() + len(__s)
                    if concatenated_len > self._max_buffer:
                        rest = self.get_filtered_output()[
                            concatenated_len - self._max_buffer :
                        ]
                        if self._buffer_separator is not None:
                            rest = rest.split(self._buffer_separator, 1)[-1]
                        super().seek(0)
                        super().write(rest)
                        super().truncate(super().tell() + len(__s))
                res = super().write(__s)
                self._trigger(self.get_filtered_output())
            if self._on_thread != threading.get_ident() or self._need_dup:
                self._dup.write(__s)
            return res

        def get_filtered_output(self):
            if self._regex is None or self._buffer_separator is None:
                return self.getvalue()

            return self._buffer_separator.join(
                filter(
                    self._regex.search, self.getvalue().split(self._buffer_separator)
                )
            )

        def print_at_end(self):
            self._trigger(self.get_filtered_output())

    def __init__(
        self,
        stdout=None,
        stderr=False,
        format=None,
        to=None,
        max_buffer=None,
        buffer_separator="\n",
        regex=None,
        duplicate_out=False,
    ):
        self.io_args = {
            "trigger": self._write,
            "max_buffer": max_buffer,
            "buffer_separator": buffer_separator,
            "regex": regex,
            "on_thread": threading.get_ident(),
        }
        self.redirections = []
        self.st = None
        self.stderr = stderr is True
        self.stdout = stdout is True or (stdout is None and not self.stderr)
        self.format = format or "code"
        self.to = to
        self.fun = None
        self.duplicate_out = duplicate_out or None
        self.active_nested = None

        if not self.stdout and not self.stderr:
            raise ValueError("one of stdout or stderr must be True")

        if self.format not in ["text", "markdown", "latex", "code", "write"]:
            raise ValueError(
                f"format need one of the following: {', '.join(['text', 'markdown', 'latex', 'code', 'write'])}"
            )

        if self.to and (not hasattr(self.to, "text") or not hasattr(self.to, "empty")):
            raise ValueError(f"'to' is not a streamlit container object")

    def __enter__(self):
        if self.st is not None:
            if self.to is None:
                if self.active_nested is None:
                    self.active_nested = self(
                        format=self.format,
                        max_buffer=self.io_args["max_buffer"],
                        buffer_separator=self.io_args["buffer_separator"],
                        regex=self.io_args["regex"],
                        duplicate_out=self.duplicate_out,
                    )
                return self.active_nested.__enter__()
            else:
                raise Exception("Already entered")
        to = self.to or st
        # to.text(f"Redirected output from "
        #         f"{'stdout and stderr' if self.stdout and self.stderr else 'stdout' if self.stdout else 'stderr'}"
        #         f"{' [' + self.io_args['regex'] + ']' if self.io_args['regex'] else ''}"
        #         f":")
        to.info(":blue[**Info logs**]")
        self.st = to.empty()
        self.fun = getattr(self.st, self.format)

        io_obj = None

        def redirect(to_duplicate, context_redirect):
            nonlocal io_obj
            io_obj = _Redirect.IOStuff(
                need_dup=self.duplicate_out and True, dup=to_duplicate, **self.io_args
            )
            redirection = context_redirect(io_obj)
            self.redirections.append((redirection, io_obj))
            redirection.__enter__()

        if self.stderr:
            redirect(sys.stderr, contextlib.redirect_stderr)
        if self.stdout:
            redirect(sys.stdout, contextlib.redirect_stdout)

        return io_obj

    def __call__(
        self,
        to=None,
        format=None,
        max_buffer=None,
        buffer_separator="\n",
        regex=None,
        duplicate_out=False,
    ):
        return _Redirect(
            self.stdout,
            self.stderr,
            format=format,
            to=to,
            max_buffer=max_buffer,
            buffer_separator=buffer_separator,
            regex=regex,
            duplicate_out=duplicate_out,
        )

    def __exit__(self, *exc):
        if self.active_nested is not None:
            nested = self.active_nested
            if nested.active_nested is None:
                self.active_nested = None
            return nested.__exit__(*exc)

        res = None
        for redirection, io_obj in reversed(self.redirections):
            res = redirection.__exit__(*exc)
            io_obj.print_at_end()

        self.redirections = []
        self.st = None
        self.fun = None
        return res

    def _write(self, data):
        self.fun(data)


stdout = _Redirect()
stderr = _Redirect(stderr=True)
stdouterr = _Redirect(stdout=True, stderr=True)
