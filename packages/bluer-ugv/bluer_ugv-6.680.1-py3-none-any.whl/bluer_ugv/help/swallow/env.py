from typing import List

from bluer_options.terminal import show_usage, xtra


def help_cp(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@swallow",
            "env",
            "cp",
            "<env-name>",
        ],
        "cp swallow swallow-raspbian-<env-name>.",
        mono=mono,
    )


def help_list(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@swallow",
            "env",
            "list",
        ],
        "list swallow envs.",
        mono=mono,
    )


help_functions = {
    "cp": help_cp,
    "list": help_list,
}
