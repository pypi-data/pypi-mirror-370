"""
The icons downloaded by this script are Copyright (c) 2018 PrimeTek
See https://github.com/primefaces/primeicons/blob/master/LICENSE

The master copy of this file is in the book repository. Don't edit its copy in a
slave repository.  See https://dev.lino-framework.org/writedocs/shared.html

To see a list of available primefaces icons, visit:
https://github.com/primefaces/primeicons/tree/master/raw-svg


"""
import requests
from pathlib import Path

# TODO: from lino.core.constants import ICON_NAMES
ICON_NAMES = ("external-link", "filter", "plus", "plus-circle", "user",
              "refresh", "trash", "bell", "times-circle", "envelope", "copy",
              "save", "home", "bars", "eject", "sliders-h")

dest = Path(__file__).parent.absolute()
root = "https://raw.githubusercontent.com/primefaces/primeicons/master/raw-svg"
found = []
for name in ICON_NAMES:
    filename = name + ".svg"
    target = dest / filename
    if target.exists():
        found.append(filename)
    else:
        url = "{}/{}".format(root, filename)
        print("Downloading {} from primeicons master...".format(filename))
        r = requests.get(url, stream=True)
        with open(target, "wb") as f:
            for chunk in r.iter_content(chunk_size=16 * 1024):
                f.write(chunk)
if len(found):
    print("No need to download {}".format(", ".join(found)))
