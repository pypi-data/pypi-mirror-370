from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.swallow.README import items
from bluer_ugv.swallow.parts import dict_of_parts

docs = [
    {
        "items": items,
        "path": "../docs/bluer_swallow",
    },
    {"path": "../docs/bluer_swallow/analog"},
    {"path": "../docs/bluer_swallow/digital"},
    {"path": "../docs/bluer_swallow/digital/design"},
    {"path": "../docs/bluer_swallow/digital/design/operation.md"},
    {
        "path": "../docs/bluer_swallow/digital/design/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../../../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="../../../parts",
                log=False,
            ),
        },
    },
    {"path": "../docs/bluer_swallow/digital/design/terraform.md"},
    {"path": "../docs/bluer_swallow/digital/design/steering-over-current-detection.md"},
    {"path": "../docs/bluer_swallow/digital/design/rpi-pinout.md"},
    {"path": "../docs/bluer_swallow/digital/dataset"},
    {"path": "../docs/bluer_swallow/digital/dataset/collection"},
    {"path": "../docs/bluer_swallow/digital/dataset/collection/validation.md"},
    {"path": "../docs/bluer_swallow/digital/dataset/collection/one.md"},
    {"path": "../docs/bluer_swallow/digital/dataset/combination"},
    {"path": "../docs/bluer_swallow/digital/dataset/combination/validation.md"},
    {"path": "../docs/bluer_swallow/digital/dataset/combination/one.md"},
    {"path": "../docs/bluer_swallow/digital/dataset/review.md"},
    {"path": "../docs/bluer_swallow/digital/model"},
    {"path": "../docs/bluer_swallow/digital/model/validation.md"},
    {"path": "../docs/bluer_swallow/digital/model/one.md"},
]
