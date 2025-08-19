from __future__ import annotations

import mu


def main():
    print("This is Mu-XML!")
    doc = ["foo", dict(a=10, b=True), "bar"]
    print("... it converts this:")
    print(doc)
    print("... into this:")
    print(mu.xml(doc))


if __name__ == "__main__":
    main()
