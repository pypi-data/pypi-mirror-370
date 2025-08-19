from bluer_objects.README.items import ImageItems

assets2 = "https://github.com/kamangir/assets2/blob/main/bluer-sparrow"
assets2_swallow = "https://github.com/kamangir/assets2/blob/main/bluer-swallow"


items = ImageItems(
    {
        "https://github.com/kamangir/bluer-ugv/raw/main/diagrams/bluer_swallow/digital.png": "https://github.com/kamangir/bluer-ugv/blob/main/diagrams/bluer_swallow/digital.svg",
        f"{assets2_swallow}/20250609_164433.jpg": "",
        f"{assets2_swallow}/20250614_102301.jpg": "",
        f"{assets2_swallow}/20250614_114954.jpg": "",
        f"{assets2_swallow}/20250615_192339.jpg": "",
        f"{assets2_swallow}/20250703_153834.jpg": "",
        f"{assets2_swallow}/design/v2/01.jpg": "",
    }
)


docs = [
    {
        "path": "../docs/bluer_swallow/digital/design/shield.md",
        "items": items,
    },
]
