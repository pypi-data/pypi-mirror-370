#  hakisto - logging reimagined
#
#  Copyright (C) 2024  Bernhard Radermacher
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
from typing import NamedTuple

from ._base import _LoggerHandlerBase
from ._logger_globals import logger_globals

from .colors import colorize_string

from .severity import Severity, CRITICAL
from .subject import FrameInformation


# from ._severity import CRITICAL, values, ERROR

# from ._logger import Logger

__all__ = ["Identifier", "Handler"]


class Identifier(NamedTuple):
    identifier: str
    """.. include:: identifier.txt"""
    continuation: str
    """Only the indicator, indented for use in additional lines."""


class Handler(_LoggerHandlerBase, metaclass=ABCMeta):
    """Ancestor of every concrete Handler.

    A handler processes a possible log entry and adds it to the respective log.

    .. warning:: This class **must** be the last in the list of inherited classes to allow correct processing via Mixin classes.

    .. include:: handler_name.txt

    :param topic: The highest level in the logging structure the Handler should process
    :param settings: :py:class:`hakisto.HandlerSettings`
    """

    def __call__(self, subject) -> None:
        """Called when a log entry is processed.

        Both the topic and the severity must be considered
        """
        if all(
            (
                self._is_active,
                self.settings.severity <= subject.severity,
                subject.topic in self._topic,
            )
        ):
            self.process(subject)

    @staticmethod
    def render(identifier: Identifier, content: str, color: str = "") -> str:
        """Render the provided content for output.

        :param identifier: The identifier that will be used.
        :type identifier: :class:`Identifier`
        :param content: The content to be rendered. Might contain new-line(s).
        :type content: str
        :param color: The color of the content if applicable.
        :type content: str
        :return: The rendered content.
        :rtype: str
        """
        if "\n" in content:
            content = f"\n{colorize_string(identifier.continuation, color)} ".join(
                content.split("\n")
            )
        return f"{colorize_string(identifier.identifier, color)} {content}"

    @abstractmethod
    def write(self, content: str) -> None:
        raise NotImplementedError()

    def get_color(self, severity: Severity) -> str:
        """Get Color for respective Severity. Override if color should be not be used."""
        if self.settings.use_color:
            return severity.color(self.settings.color_palette)
        return ""

    def process(self, subject) -> None:
        color = self.get_color(subject.severity)
        content_lines = [subject.message]
        if subject.severity >= CRITICAL or subject.force_location:
            content_lines.append(subject.source_location)
        if subject.severity >= CRITICAL:
            content_lines.append(
                self.format_frame_information(
                    FrameInformation(subject.source.copy(), subject.local_vars.copy())
                )
            )

        # noinspection PyUnresolvedReferences
        content = self.render(
            identifier=self.get_identifier(subject=subject),
            content="\n".join(content_lines),
            color=color,
        )
        self.write(content)

    @staticmethod
    def format_frame_information(frame_information: FrameInformation) -> str:
        """Render Source and local variables for CRITICAL and Exceptions.

        :param frame_information:
        :type frame_information: :class:`hakisto.FrameInformation`
        """
        if not any([frame_information.source, frame_information.local_vars]):
            return ""

        # noinspection PyTypeChecker
        lines: list[tuple[int | str], str] = frame_information.source.copy()
        num_width = len(str(lines[-1][0]))
        txt_width = max((len(i[1]) for i in lines))

        try:
            var_width = max((len(i) for i in frame_information.local_vars))
        except ValueError:
            var_width = 1
        var_lines = [
            f"   {k:{var_width}} = {v!r}"
            for k, v in frame_information.local_vars.items()
        ]

        while len(lines) < len(var_lines):
            lines.insert(0, ("", ""))
        while len(lines) > len(var_lines):
            var_lines.insert(0, "")

        return "\n".join(
            [" " * num_width + " ┌──" + "─" * txt_width + "┐"]
            + [
                f"{lines[i][0]:{num_width}} │ {lines[i][1]:{txt_width}} │{var_lines[i]}"
                for i in range(len(lines))
            ]
            + [" " * num_width + " └──" + "─" * txt_width + "┘"]
        )

    def handle_exception(self, subject) -> None:
        """Renders the full traceback with source and local variables.

        :param subject: The subject being processed.
        :type subject: :class:`hakisto.Subject`
        """
        color = self.get_color(CRITICAL)

        content_lines = [colorize_string(subject.message, color)]
        traceback_blocks = []
        for i in subject.traceback:
            traceback_blocks.append(
                [i.source_location, self.format_frame_information(i.frame_information)]
            )

        if logger_globals.short_trace:
            content_lines.extend(traceback_blocks[-1])
        else:
            for i in traceback_blocks:
                content_lines.extend(i)

        content_lines.append(colorize_string(subject.message, color))

        # noinspection PyUnresolvedReferences
        content = self.render(
            identifier=self.get_identifier(subject=subject, indicator="X"),
            content="\n".join(content_lines),
            color=color,
        )
        self.write(content)

    def get_identifier(self, subject, indicator=None) -> Identifier:
        """Return standard Identifier

        .. include:: identifier.txt

        :param subject: The subject to be handled
        :type subject: hakisto.Subject:class:`hakisto.Subject`
        :param indicator: Indicator to use instead of the one determined by Subject.severity
        :type indicator: str
        :returns: Identifier
        :rtype: :class:`hakisto.Identifier`
        """
        indicator = indicator or str(subject.severity)[0]
        parts = [f"{indicator} {subject.created.strftime(self.settings.date_format)}"]
        if subject.message_id:
            parts.append(f"<{subject.message_id}>")
        if subject.process_name != "MainProcess":
            parts.append(
                f"*{subject.process_name}:{subject.process_id}*"
                if subject.process_id
                else f"*{subject.process_name}*"
            )
        if subject.thread_name != "MainThread":
            parts.append(
                f"({subject.thread_name}:{subject.thread_id})"
                if subject.thread_id
                else f"({subject.thread_name})"
            )
        if subject.asyncio_task_name:
            parts.append(f"'{subject.asyncio_task_name}'")
        if subject.severity in self.settings.inline_location:
            parts.append(f"»{subject.inline_location}«")
        if subject.topic:
            parts.append(str(subject.topic))
        identifier = f"[{' '.join(parts)}]"
        return Identifier(
            identifier, f"{' ' * (len(identifier) - len(indicator) - 2)}[{indicator}]"
        )

    def __hash__(self) -> int:
        return id(self)
