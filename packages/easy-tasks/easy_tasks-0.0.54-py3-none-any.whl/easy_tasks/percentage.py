import math
from threading import Thread
from time import sleep, time

import know_the_time
from colorful_terminal import Fore, TermAct, colored_print
from exception_details import print_exception_details

# from .rounding import round_relative_to_decimal
from easy_tasks.rounding import round_relative_to_decimal


def get_percentage_as_fitted_string(
    count: int, total: int, round_to: int = 2, with_percentage_symbol: bool = True
):
    if total == 0:
        count = 0
        perc = 100
    else:
        perc = count / total * 100
    perc = str(round_relative_to_decimal(perc, round_to))
    if with_percentage_symbol:
        perc += " %"
    return perc


def progress_printer(
    count: int, total: int, pre_string: str = "Progress: ", post_string: str = ""
):
    TermAct.clear_current_line_action()
    print(
        f"\r{pre_string}{str(count).rjust(len(str(total)))} / {total}    ({get_percentage_as_fitted_string(count, total)}){post_string}",
        end="",
    )
    if count == total:
        print()


def main_and_sub_progress_printer(
    maincount: int,
    maintotal: int,
    subcount: int,
    subtotal: int,
    pre_string: str = "Progress: ",
    mainpre_string: str = "Main-Progress: ",
    subpre_string: str = "Sub-Progress: ",
    post_string: str = "",
    mainpost_string: str = "",
    subpost_string: str = "",
):
    if maincount == 0 and subcount == 0:
        print(TermAct.hide_cursor(), end="")

    if post_string == "":
        lines = 3
    else:
        lines = 4 + post_string.count("\n")
    if maincount != 0 and subcount != 0:
        for i in range(lines):
            colored_print(TermAct.cursor_previous_line, end="")
    if len(mainpre_string) < len(subpre_string):
        mainpre_string = mainpre_string.ljust(len(subpre_string))
    elif len(mainpre_string) > len(subpre_string):
        subpre_string = subpre_string.ljust(len(mainpre_string))
    length = (
        len(str(subtotal))
        if len(str(subtotal)) > len(str(maintotal))
        else len(str(maintotal))
    )
    maintotal_str = str(maintotal).rjust(length)
    subtotal_str = str(subtotal).rjust(length)
    maincount_str = str(maincount).rjust(length)
    _subcount = subcount if subtotal != 0 else 0
    subcount_str = str(_subcount).rjust(length)

    try:
        # s = ""
        # s += f"{pre_string}" + "\n"
        # s += f"\r{mainpre_string}{maincount_str} / {maintotal_str}  ({get_percentage_as_fitted_string(maincount, maintotal)}){mainpost_string}" + "\n"
        # s += f"\r{subpre_string}{subcount_str} / {subtotal_str}  ({get_percentage_as_fitted_string(subcount, subtotal)}){subpost_string}" + "\n"
        # s += post_string + "\n"
        # print(s + "\r", end="")
        s = f"{pre_string}"
        TermAct.clear_current_line_action()
        print(s)
        s = f"\r{mainpre_string}{maincount_str} / {maintotal_str}  ({get_percentage_as_fitted_string(maincount, maintotal)}){mainpost_string}"
        TermAct.clear_current_line_action()
        print(s)
        s = f"\r{subpre_string}{subcount_str} / {subtotal_str}  ({get_percentage_as_fitted_string(subcount, subtotal)}){subpost_string}"
        TermAct.clear_current_line_action()
        print(s)
        s = post_string
        TermAct.clear_current_line_action()
        print(s)
    except Exception as e:
        print("\n" * 20)
        print_exception_details(e)
        print("\n" * 20)
    if maincount == maintotal and (subcount == subtotal or subtotal == 0):
        print(TermAct.show_cursor(), end="")
    else:
        print(TermAct.cursor_up * 4 + "\r", end="")


PREFIX_COLOR = (127, 184, 0)
SUFFIX = ""
# SUFFIX_COLOR = (12, 99, 231)
SUFFIX_COLOR = (50, 150, 255)
SHOW_PROGRESS = True
PROGRESS_COLOR = (255, 234, 0)
SHOW_PERCENTAGE = True
PERCENTAGE_COLOR = (255, 180, 0)
SHOW_TIMER = True
TIMER_COLOR = (247, 127, 0)
TIMER_PREFIX = ""
TIMER_WITH_MILLISEC = False
SHOW_DELTA_TIMER = True
DELTA_TIMER_COLOR = (246, 81, 29)
DELTA_TIMER_PREFIX = "Δ: "
BAR_TYPE = "━"
TOTAL_BAR_LENGTH = 50
BAR_COLOR = (0, 166, 237)
BACKGROUND_COLOR = (77, 77, 77)
VANISH_WITH_FINISH = False
INDENTATION = 0
INDENTATION_BLOCK = "    "
PRECISION = 5
SPACING = "  "
POST_BAR_SPACING = "  "
SHOW_ESTIMATED_REMAINING_TIME = True
SHOW_ESTIMATED_REMAINING_TIME_COLOR = (220, 50, 170)
SHOW_ESTIMATED_REMAINING_TIME_PREFIX = "Remaining time: ~ "



class ProgressBarOld:
    """A progress bar printer with subprogress support and many customization options.

    colorama and moviepy break this since they manipulate the terminal output.
    """

    post_bar_spacing = "  "

    def __init__(
        self,
        total: float,
        prefix: str = "Progress: ",
        prefix_color: tuple = PREFIX_COLOR,
        suffix: str = SUFFIX,
        suffix_color: tuple = SUFFIX_COLOR,
        show_progress: bool = SHOW_PROGRESS,
        progress_color: tuple = PROGRESS_COLOR,
        show_percentage: bool = SHOW_PERCENTAGE,
        percentage_color: tuple = PERCENTAGE_COLOR,
        show_timer: bool = SHOW_TIMER,
        timer_color: tuple = TIMER_COLOR,
        timer_prefix: str = TIMER_PREFIX,
        timer_with_millisec: bool = TIMER_WITH_MILLISEC,
        show_delta_timer: bool = SHOW_DELTA_TIMER,
        delta_timer_color: tuple = DELTA_TIMER_COLOR,
        delta_timer_prefix: str = DELTA_TIMER_PREFIX,
        bar_type: str = BAR_TYPE,
        total_bar_length: int = TOTAL_BAR_LENGTH,
        bar_color: tuple = BAR_COLOR,
        background_color: tuple = BACKGROUND_COLOR,
        vanish_with_finish: bool = VANISH_WITH_FINISH,
        auto_start: bool = True,
        indentation: int = INDENTATION,
        indentation_block: str = INDENTATION_BLOCK,
        constant_output: bool = True,
        constant_output_rate: float = 0.1,
        precision: int = PRECISION,
        spacing: str = SPACING,
        post_bar_spacing: str = POST_BAR_SPACING,
        _parent_progress=None,
        # show_estimated_remaining_time: bool = SHOW_ESTIMATED_REMAINING_TIME,
        # show_estimated_remaining_time_color: tuple = SHOW_ESTIMATED_REMAINING_TIME_COLOR,
        # show_estimated_remaining_time_prefix: str = SHOW_ESTIMATED_REMAINING_TIME_PREFIX,
    ) -> None:
        self.progress = 0
        self.total = total
        self.prefix = prefix
        self.prefix_color = prefix_color
        self.suffix = suffix
        self.suffix_color = suffix_color
        self.show_progress = show_progress
        self.progress_color = progress_color
        self.show_percentage = show_percentage
        self.percentage_color = percentage_color
        self.show_timer = show_timer
        self.timer_color = timer_color
        self.timer_prefix = timer_prefix
        self.timer_with_millisec = timer_with_millisec
        self.show_delta_timer = show_delta_timer
        self.delta_timer_color = delta_timer_color
        self.delta_timer_prefix = delta_timer_prefix
        self.bar_type = bar_type
        self.total_bar_length = total_bar_length
        self.bar_color = bar_color
        self.background_color = background_color
        self.vanish_with_finish = vanish_with_finish
        self.subprogresses = {}
        self.indentation = indentation
        self.indentation_block = indentation_block
        self.constant_output = constant_output
        self.constant_output_rate = constant_output_rate
        self.precision = precision
        self.post_bar_spacing = post_bar_spacing
        self.spacing = spacing
        self._parent_progress = _parent_progress
        self.ratio = 0
        self.lines = 1
        self.finished = False
        self._stop_output = False
        self.starting_time = None
        self.last_updated = None
        self.progress_precision = 0
        self.delta_timer_history = []
        self.show_estimated_remaining_time = False  # show_estimated_remaining_time
        self.show_estimated_remaining_time_color = SHOW_ESTIMATED_REMAINING_TIME_COLOR  # show_estimated_remaining_time_color
        self.show_estimated_remaining_time_prefix = SHOW_ESTIMATED_REMAINING_TIME_PREFIX  # show_estimated_remaining_time_prefix
        self.remaining_time = "--:--:--:---" if self.timer_with_millisec else "--:--:--"

        if auto_start:
            self.update(0)
            if constant_output:
                Thread(target=self._constant_output, daemon=True).start()

    def get_progress_str(self):
        self.ratio = (
            round(self.progress / self.total, self.precision)
            if not self.total == 0
            else 1
        )
        progress = round(self.progress, self.precision)
        progress_precision = (
            len(str(progress).split(".")[-1])
            if "." in str(progress)
            else 0
        )
        if progress_precision > self.progress_precision:
            self.progress_precision = progress_precision
        bars_amount = math.floor(self.ratio * self.total_bar_length)
        no_bars = self.total_bar_length - bars_amount
        done_str = Fore.rgb(*self.bar_color) + bars_amount * self.bar_type
        not_done_str = Fore.rgb(*self.background_color) + no_bars * self.bar_type
        bar = done_str + not_done_str + self.post_bar_spacing
        _suffix = ""
        if self.show_progress:
            prgrs = (
                round_relative_to_decimal(progress, self.progress_precision)
                if self.progress_precision != 0
                else progress
            )
            prgrs = str(prgrs).rjust(len(str(self.total)))
            _suffix += (
                Fore.rgb(*self.progress_color)
                + f"{prgrs} / {self.total}".rjust(2 * len(str(self.total)) + 2)
                + self.spacing
            )
        if self.show_percentage:
            _suffix += (
                Fore.rgb(*self.percentage_color)
                + f"{round_relative_to_decimal(self.ratio*100, 2)} %".rjust(7)
                + self.spacing
            )
        if self.show_timer:
            if not self.starting_time:
                self.starting_time = time()
            timer = know_the_time.get_time_delta_prettystring(
                self.starting_time,
                time(),
                include_milliseconds=self.timer_with_millisec,
            )
            _suffix += (
                Fore.rgb(*self.timer_color) + self.timer_prefix + timer + self.spacing
            )
        if not self.last_updated:
            self.last_updated = time()
        if self.show_delta_timer:
            delta_timer = know_the_time.get_time_delta_prettystring(
                self.last_updated,
                time(),
                include_milliseconds=self.timer_with_millisec,
            )
            _suffix += (
                Fore.rgb(*self.delta_timer_color)
                + self.delta_timer_prefix
                + delta_timer
                + self.spacing
            )
        if self.show_estimated_remaining_time:
            if self.ratio != 0:
                remaining_time = math.floor((self.last_updated - self.starting_time) / self.ratio) - (time() - self.last_updated)
                if remaining_time >= 0: self.remaining_time = remaining_time
                else: remaining_time = self.remaining_time
                remaining_time = know_the_time.get_time_delta_prettystring(
                    remaining_time,
                    start_is_delta=True,
                    include_milliseconds=self.timer_with_millisec,
                )
            else:
                remaining_time = "--:--:--:---" if self.timer_with_millisec else "--:--:--"
            _suffix += (
                Fore.rgb(*self.show_estimated_remaining_time_color)
                + self.show_estimated_remaining_time_prefix
                + remaining_time
                + self.spacing
            )
        _suffix += Fore.rgb(*self.suffix_color) + self.suffix
        main_bar = (
            self.indentation * self.indentation_block
            + Fore.rgb(*self.prefix_color)
            + self.prefix
            + bar
            + _suffix
        )
        main_bar = "\n".join(
            [line + TermAct.erase_in_line() for line in main_bar.splitlines()]
        )
        return main_bar

    def update(self, amount=1, name=None):
        if self._parent_progress:
            myname = [n for n, p in self._parent_progress.subprogresses.items() if p == self][0]
            self._parent_progress.update(amount, myname)
            return
        if amount:
            self.delta_timer_history.append(time()-self.last_updated)
            if name:
                self.subprogresses[name].last_updated = time()
            else:
                self.last_updated = time()
        else:
            amount = 0
        if not name:
            self.progress += amount
        output = self.get_progress_str()

        for sub_name, sub_progress in self.subprogresses.items():
            sub_progress: ProgressBar
            if sub_name == name and not sub_progress.finished:
                sub_progress.progress += amount
            elif sub_name == name:
                sub_progress.progress = amount
                sub_progress.finished = False
            sub_bar = sub_progress.get_progress_str()
            if sub_name == name and sub_progress.ratio == 1:
                sub_progress.finished = True
                sub_progress.starting_time = None
                sub_progress.last_updated = None
            if sub_bar != "":
                output += "\n" + sub_bar

        self.lines = len(output.splitlines())
        output += TermAct.cursor_up * (self.lines - 1)

        self.finished = (
            True
            if all([s.ratio == 1 or s.finished for s in self.subprogresses.values()])
            and self.ratio == 1
            else False
        )

        self.output = output

        self.output_progress()

    def output_progress(self):
        colored_print(TermAct.hide_cursor() + self.output, end="\r")

        if self.finished == True:
            print(TermAct.show_cursor(), end="")
            print((self.lines - 1) * "\n")

            if self.vanish_with_finish:
                TermAct.clear_previous_line_action(self.lines)

    def add_subprogress(
        self,
        name: str,
        total: float,
        prefix: str = "Sub-Progress: ",
        prefix_color: tuple = PREFIX_COLOR,
        suffix: str = SUFFIX,
        suffix_color: tuple = SUFFIX_COLOR,
        show_progress: bool = SHOW_PROGRESS,
        progress_color: tuple = PROGRESS_COLOR,
        show_percentage: bool = SHOW_PERCENTAGE,
        percentage_color: tuple = PERCENTAGE_COLOR,
        show_timer: bool = SHOW_TIMER,
        timer_color: tuple = TIMER_COLOR,
        timer_prefix: str = TIMER_PREFIX,
        timer_with_millisec: bool = TIMER_WITH_MILLISEC,
        show_delta_timer: bool = SHOW_DELTA_TIMER,
        delta_timer_color: tuple = DELTA_TIMER_COLOR,
        delta_timer_prefix: str = DELTA_TIMER_PREFIX,
        bar_type: str = BAR_TYPE,
        total_bar_length: int = TOTAL_BAR_LENGTH,
        bar_color: tuple = BAR_COLOR,
        background_color: tuple = BACKGROUND_COLOR,
        vanish_with_finish: bool = VANISH_WITH_FINISH,
        indentation: int = 1,
        indentation_block: str = INDENTATION_BLOCK,
        precision: int = PRECISION,
        spacing: str = SPACING,
        post_bar_spacing: str = POST_BAR_SPACING,
        # show_estimated_remaining_time: bool = SHOW_ESTIMATED_REMAINING_TIME,
        # show_estimated_remaining_time_color: tuple = SHOW_ESTIMATED_REMAINING_TIME_COLOR,
        # show_estimated_remaining_time_prefix: str = SHOW_ESTIMATED_REMAINING_TIME_PREFIX,
    ):
        progress = ProgressBar(
            total=total,
            prefix=prefix,
            prefix_color=prefix_color,
            suffix=suffix,
            suffix_color=suffix_color,
            show_progress=show_progress,
            progress_color=progress_color,
            show_percentage=show_percentage,
            percentage_color=percentage_color,
            show_timer=show_timer,
            timer_color=timer_color,
            timer_prefix=timer_prefix,
            timer_with_millisec=timer_with_millisec,
            show_delta_timer=show_delta_timer,
            delta_timer_color=delta_timer_color,
            delta_timer_prefix=delta_timer_prefix,
            bar_type=bar_type,
            total_bar_length=total_bar_length,
            bar_color=bar_color,
            background_color=background_color,
            vanish_with_finish=vanish_with_finish,
            auto_start=False,
            indentation=indentation,
            indentation_block=indentation_block,
            constant_output=False,
            constant_output_rate=0.1,
            precision=precision,
            spacing=spacing,
            post_bar_spacing=post_bar_spacing,
            _parent_progress=self,
            # show_estimated_remaining_time=show_estimated_remaining_time,
            # show_estimated_remaining_time_color=show_estimated_remaining_time_color,
            # show_estimated_remaining_time_prefix=show_estimated_remaining_time_prefix,
        )
        self.subprogresses[name] = progress
        return progress

    def _constant_output(self):
        while not self.finished and not self._stop_output:
            self.update(None)
            sleep(self.constant_output_rate)

    def stop_output(self, correct_lines=False):
        self._stop_output = True
        if correct_lines:
            lines = len(self.subprogresses)
            print("\n"*lines)

    def completed(self):
        for child in self.subprogresses.values():
            child.progress = child.total
        self.progress = self.total
        if self._parent_progress:
            self._parent_progress.update(0)
        else:
            self.update(0)

    def do_break(self):
        for child in self.subprogresses.values():
            child.stop_output()
        self.stop_output(True)

    def reset(self, total=None, prefix=None, suffix=None):
        "set progress to 0 and set new total, prefix and suffix"
        self.progress = 0
        if total: self.total = total
        if prefix: self.prefix = prefix
        if suffix: self.suffix = suffix


class ProgressBar:
    """A progress bar printer with subprogress support and many customization options.

    colorama and moviepy break this since they manipulate the terminal output.
    """

    post_bar_spacing = "  "

    def __init__(
        self,
        total: float,
        prefix: str = "Progress: ",
        prefix_color: tuple = PREFIX_COLOR,
        suffix: str = SUFFIX,
        suffix_color: tuple = SUFFIX_COLOR,
        show_progress: bool = SHOW_PROGRESS,
        progress_color: tuple = PROGRESS_COLOR,
        show_percentage: bool = SHOW_PERCENTAGE,
        percentage_color: tuple = PERCENTAGE_COLOR,
        show_timer: bool = SHOW_TIMER,
        timer_color: tuple = TIMER_COLOR,
        timer_prefix: str = TIMER_PREFIX,
        timer_with_millisec: bool = TIMER_WITH_MILLISEC,
        show_delta_timer: bool = SHOW_DELTA_TIMER,
        delta_timer_color: tuple = DELTA_TIMER_COLOR,
        delta_timer_prefix: str = DELTA_TIMER_PREFIX,
        bar_type: str = BAR_TYPE,
        total_bar_length: int = TOTAL_BAR_LENGTH,
        bar_color: tuple = BAR_COLOR,
        background_color: tuple = BACKGROUND_COLOR,
        vanish_with_finish: bool = VANISH_WITH_FINISH,
        auto_start: bool = True,
        indentation: int = INDENTATION,
        indentation_block: str = INDENTATION_BLOCK,
        constant_output: bool = True,
        constant_output_rate: float = 0.1,
        precision: int = PRECISION,
        spacing: str = SPACING,
        post_bar_spacing: str = POST_BAR_SPACING,
        _parent_progress=None,
        # show_estimated_remaining_time: bool = SHOW_ESTIMATED_REMAINING_TIME,
        # show_estimated_remaining_time_color: tuple = SHOW_ESTIMATED_REMAINING_TIME_COLOR,
        # show_estimated_remaining_time_prefix: str = SHOW_ESTIMATED_REMAINING_TIME_PREFIX,
    ) -> None:
        self.progress = 0
        self.total = total
        self.prefix = prefix
        self.prefix_color = prefix_color
        self.suffix = suffix
        self.suffix_color = suffix_color
        self.show_progress = show_progress
        self.progress_color = progress_color
        self.show_percentage = show_percentage
        self.percentage_color = percentage_color
        self.show_timer = show_timer
        self.timer_color = timer_color
        self.timer_prefix = timer_prefix
        self.timer_with_millisec = timer_with_millisec
        self.show_delta_timer = show_delta_timer
        self.delta_timer_color = delta_timer_color
        self.delta_timer_prefix = delta_timer_prefix
        self.bar_type = bar_type
        self.total_bar_length = total_bar_length
        self.bar_color = bar_color
        self.background_color = background_color
        self.vanish_with_finish = vanish_with_finish
        self.subprogresses = []
        self.indentation = indentation
        self.indentation_block = indentation_block
        self.constant_output = constant_output
        self.constant_output_rate = constant_output_rate
        self.precision = precision
        self.post_bar_spacing = post_bar_spacing
        self.spacing = spacing
        self._parent_progress = _parent_progress
        self.ratio = 0
        self.lines = 1
        self.finished = False
        self._broke = False
        self._stop_output = False
        self.starting_time = None
        self.last_updated = None
        self.progress_precision = 0
        self.delta_timer_history = []
        self.show_estimated_remaining_time = False  # show_estimated_remaining_time
        self.show_estimated_remaining_time_color = SHOW_ESTIMATED_REMAINING_TIME_COLOR  # show_estimated_remaining_time_color
        self.show_estimated_remaining_time_prefix = SHOW_ESTIMATED_REMAINING_TIME_PREFIX  # show_estimated_remaining_time_prefix
        self.remaining_time = "--:--:--:---" if self.timer_with_millisec else "--:--:--"
        self._completed_called = False

        if auto_start:
            self.update(0)
            if constant_output:
                Thread(target=self._constant_output, daemon=True).start()

    def __enter__(self):
        # This is executed when entering the context (i.e., the 'with' block)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # This is executed when exiting the context (i.e., the 'with' block)
        if not self.finished:
            self.do_break()
            # If an exception occurred, exc_type, exc_value, and traceback are set
            if exc_type is not None:
                # Returning False re-raises the exception
                return False

    def get_progress_str(self):
        self.ratio = (
            round(self.progress / self.total, self.precision)
            if not self.total == 0
            else 1
        )
        progress = round(self.progress, self.precision)
        progress_precision = (
            len(str(progress).split(".")[-1])
            if "." in str(progress)
            else 0
        )
        if progress_precision > self.progress_precision:
            self.progress_precision = progress_precision
        bars_amount = math.floor(self.ratio * self.total_bar_length)
        no_bars = self.total_bar_length - bars_amount
        done_str = Fore.rgb(*self.bar_color) + bars_amount * self.bar_type
        not_done_str = Fore.rgb(*self.background_color) + no_bars * self.bar_type
        bar = done_str + not_done_str + self.post_bar_spacing
        _suffix = ""
        if self.show_progress:
            prgrs = (
                round_relative_to_decimal(progress, self.progress_precision)
                if self.progress_precision != 0
                else progress
            )
            prgrs = str(prgrs).rjust(len(str(self.total)))
            _suffix += (
                Fore.rgb(*self.progress_color)
                + f"{prgrs} / {self.total}".rjust(2 * len(str(self.total)) + 2)
                + self.spacing
            )
        if self.show_percentage:
            _suffix += (
                Fore.rgb(*self.percentage_color)
                + f"{round_relative_to_decimal(self.ratio*100, 2)} %".rjust(7)
                + self.spacing
            )
        if self.show_timer:
            if not self.starting_time:
                self.starting_time = time()
            timer = know_the_time.get_time_delta_prettystring(
                self.starting_time,
                time(),
                include_milliseconds=self.timer_with_millisec,
            )
            _suffix += (
                Fore.rgb(*self.timer_color) + self.timer_prefix + timer + self.spacing
            )
        if not self.last_updated:
            self.last_updated = time()
        if self.show_delta_timer:
            delta_timer = know_the_time.get_time_delta_prettystring(
                self.last_updated,
                time(),
                include_milliseconds=self.timer_with_millisec,
            )
            _suffix += (
                Fore.rgb(*self.delta_timer_color)
                + self.delta_timer_prefix
                + delta_timer
                + self.spacing
            )
        if self.show_estimated_remaining_time:
            if self.ratio != 0:
                remaining_time = math.floor((self.last_updated - self.starting_time) / self.ratio) - (time() - self.last_updated)
                if remaining_time >= 0: self.remaining_time = remaining_time
                else: remaining_time = self.remaining_time
                remaining_time = know_the_time.get_time_delta_prettystring(
                    remaining_time,
                    start_is_delta=True,
                    include_milliseconds=self.timer_with_millisec,
                )
            else:
                remaining_time = "--:--:--:---" if self.timer_with_millisec else "--:--:--"
            _suffix += (
                Fore.rgb(*self.show_estimated_remaining_time_color)
                + self.show_estimated_remaining_time_prefix
                + remaining_time
                + self.spacing
            )
        _suffix += Fore.rgb(*self.suffix_color) + self.suffix
        main_bar = (
            self.indentation * self.indentation_block
            + Fore.rgb(*self.prefix_color)
            + self.prefix
            + bar
            + _suffix
        )
        main_bar = "\n".join(
            [line + TermAct.erase_in_line() for line in main_bar.splitlines()]
        )
        return main_bar

    def update(self, amount=1, _subprocess_index=None):
        if self._parent_progress:
            my_index = [i for i, p in enumerate(self._parent_progress.subprogresses) if p == self][0]
            my_index = self._parent_progress.subprogresses.index(self)
            self._parent_progress.update(amount, my_index)
            return
        if amount:
            self.delta_timer_history.append(time()-self.last_updated)
            if _subprocess_index:
                self.subprogresses[_subprocess_index].last_updated = time()
            else:
                self.last_updated = time()
        else:
            amount = 0
        if _subprocess_index == None:
            self.progress += amount
        output = self.get_progress_str()

        for sub_index, sub_progress in enumerate(self.subprogresses):
            sub_progress: ProgressBar
            if sub_index == _subprocess_index and not sub_progress.finished:
                sub_progress.progress += amount
            elif sub_index == _subprocess_index:
                sub_progress.progress = amount
                sub_progress.finished = False
            sub_bar = sub_progress.get_progress_str()
            if sub_index == _subprocess_index and sub_progress.ratio == 1:
                sub_progress.finished = True
                sub_progress.starting_time = None
                sub_progress.last_updated = None
            if sub_bar != "":
                output += "\n" + sub_bar

        self.lines = len(output.splitlines())
        output += TermAct.cursor_up * (self.lines - 1)

        self.finished = (
            True
            if all([s.ratio == 1 or s.finished for s in self.subprogresses])
            and self.ratio == 1
            else False
        )

        self.output = output

        self.output_progress()

    def output_progress(self):
        colored_print(TermAct.hide_cursor() + self.output, end="\r")

        if self.finished == True:
            self._completed_called = True
            print(TermAct.show_cursor(), end="")
            print((self.lines - 1) * "\n")

            if self.vanish_with_finish:
                TermAct.clear_previous_line_action(self.lines)

    def add_subprogress(
        self,
        total: float,
        prefix: str = "Sub-Progress: ",
        prefix_color: tuple = PREFIX_COLOR,
        suffix: str = SUFFIX,
        suffix_color: tuple = SUFFIX_COLOR,
        show_progress: bool = SHOW_PROGRESS,
        progress_color: tuple = PROGRESS_COLOR,
        show_percentage: bool = SHOW_PERCENTAGE,
        percentage_color: tuple = PERCENTAGE_COLOR,
        show_timer: bool = SHOW_TIMER,
        timer_color: tuple = TIMER_COLOR,
        timer_prefix: str = TIMER_PREFIX,
        timer_with_millisec: bool = TIMER_WITH_MILLISEC,
        show_delta_timer: bool = SHOW_DELTA_TIMER,
        delta_timer_color: tuple = DELTA_TIMER_COLOR,
        delta_timer_prefix: str = DELTA_TIMER_PREFIX,
        bar_type: str = BAR_TYPE,
        total_bar_length: int = TOTAL_BAR_LENGTH,
        bar_color: tuple = BAR_COLOR,
        background_color: tuple = BACKGROUND_COLOR,
        vanish_with_finish: bool = VANISH_WITH_FINISH,
        indentation: int = 1,
        indentation_block: str = INDENTATION_BLOCK,
        precision: int = PRECISION,
        spacing: str = SPACING,
        post_bar_spacing: str = POST_BAR_SPACING,
    ):
        progress = ProgressBar(
            total=total,
            prefix=prefix,
            prefix_color=prefix_color,
            suffix=suffix,
            suffix_color=suffix_color,
            show_progress=show_progress,
            progress_color=progress_color,
            show_percentage=show_percentage,
            percentage_color=percentage_color,
            show_timer=show_timer,
            timer_color=timer_color,
            timer_prefix=timer_prefix,
            timer_with_millisec=timer_with_millisec,
            show_delta_timer=show_delta_timer,
            delta_timer_color=delta_timer_color,
            delta_timer_prefix=delta_timer_prefix,
            bar_type=bar_type,
            total_bar_length=total_bar_length,
            bar_color=bar_color,
            background_color=background_color,
            vanish_with_finish=vanish_with_finish,
            auto_start=False,
            indentation=indentation,
            indentation_block=indentation_block,
            constant_output=False,
            constant_output_rate=0.1,
            precision=precision,
            spacing=spacing,
            post_bar_spacing=post_bar_spacing,
            _parent_progress=self,
            # show_estimated_remaining_time=show_estimated_remaining_time,
            # show_estimated_remaining_time_color=show_estimated_remaining_time_color,
            # show_estimated_remaining_time_prefix=show_estimated_remaining_time_prefix,
        )
        self.subprogresses.append(progress)
        return progress

    def remove_subprogress(self, subprogress):
        length = len(self.subprogresses)
        self.subprogresses.remove(subprogress)
        constant_output = self.constant_output
        self.constant_output = False
        TermAct.clear_current_line_action()
        for i in range(length):
            print()
            TermAct.clear_current_line_action()
        for i in range(length):
            TermAct.clear_previous_line_action()
        self.constant_output = constant_output

    def _constant_output(self):
        while not self.finished and not self._stop_output and self.constant_output:
            self.update(None)
            sleep(self.constant_output_rate)

    def stop_output(self, correct_lines=False):
        self._stop_output = True
        if correct_lines:
            lines = len(self.subprogresses)
            print("\n"*lines)

    def completed(self):
        self.finish()

    def finish(self):
        if self._completed_called:
            return
        for child in self.subprogresses:
            if child.progress != child.total:
                child.progress = child.total

        if self.progress != self.total:
            self.progress = self.total
        if self._parent_progress:
            self._parent_progress.update(0)
        else:
            self.update(0)

    def do_break(self):
        "will stop the output stream without raising the progress and sets self._broke and every child._broke to True so this function is only called once - reverse with self.unbreak()"
        for child in self.subprogresses:
            if not child._broke:
                child.stop_output()
            child._broke = True
        if not self._broke:
            self.stop_output(True)
        self._broke = True

    def unbreak(self):
        "sets self._broke and every child._broke to False so this self.do_break can be called again"
        for child in self.subprogresses:
            child._broke = False
        self._broke = False

    def reset(self, total=None, prefix=None, suffix=None):
        "set progress to 0 and set new total, prefix and suffix"
        self._completed_called = False
        self.progress = 0
        if total: self.total = total
        if prefix: self.prefix = prefix
        if suffix: self.suffix = suffix



def showcase_behavior_on_normal():
    # On nomrl completion
    total = 5
    _break = False
    with ProgressBar(total) as prg:
        prg2 = prg.add_subprogress(total)
        for i in range(total):
            prg2.reset(total)
            for j in range(total):
                sleep(0.2)
                prg2.update()
            prg.update()
        prg.completed()
    print("test finished")

def showcase_behavior_on_early_completion():
    # On early completion
    total = 100
    _break = False
    with ProgressBar(total) as prg:
        prg2 = prg.add_subprogress(100)
        prg3 = prg.add_subprogress(100, indentation=2)
        for i in range(100):
            prg2.reset(100)
            for j in range(100):
                prg3.reset(100)
                sleep(0.001)
                for k in range(10):
                    sleep(0.001)
                    prg3.update()
                    if i == 0 and j == 1 and k == 5:
                        _break = True
                        break
                if _break:
                    break
                prg2.update()
            if _break:
                break
            prg.update()
        prg.completed()
    print("test finished")

def showcase_behavior_on_early_exits():
    # On early exits
    total = 100
    _break = False
    with ProgressBar(total) as prg:
        prg2 = prg.add_subprogress(100)
        prg3 = prg.add_subprogress(100, indentation=2)
        for i in range(100):
            prg2.reset(100)
            for j in range(100):
                prg3.reset(100)
                sleep(0.001)
                for k in range(10):
                    sleep(0.001)
                    prg3.update()
                    if i == 0 and j == 1 and k == 5:
                        _break = True
                        break
                if _break:
                    break
                prg2.update()
            if _break:
                break
            prg.update()
    print("test finished")

def showcase_behavior_on_exceptions():
    # On exceptions
    total = 100
    _break = False
    with ProgressBar(total) as prg:
        prg2 = prg.add_subprogress(100)
        prg3 = prg.add_subprogress(100, indentation=2)
        for i in range(100):
            prg2.reset(100)
            for j in range(100):
                prg3.reset(100)
                sleep(0.001)
                for k in range(10):
                    sleep(0.001)
                    prg3.update()
                    if i == 0 and j == 0 and k == 5:
                        _break = True
                        break
                if _break:
                    break
                prg2.update()
            if _break:
                break
            prg.update()
        raise Exception



