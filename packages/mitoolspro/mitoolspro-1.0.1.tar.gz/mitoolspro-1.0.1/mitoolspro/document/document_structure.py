import base64
from math import isclose
from typing import List

from mitoolspro.exceptions import ArgumentStructureError

CHAR_SIZE_TOLERANCE = 0.001


class BBox:
    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0

    @property
    def center(self):
        return (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2

    @property
    def xcenter(self):
        return (self.x0 + self.x1) / 2

    @property
    def ycenter(self):
        return (self.y0 + self.y1) / 2

    def overlaps(self, other: "BBox", tolerance: float = 1.0) -> bool:
        return not (
            self.y0 >= other.y1 + tolerance
            or other.y0 >= self.y1 + tolerance
            or self.x1 <= other.x0 - tolerance
            or other.x1 <= self.x0 - tolerance
        )

    def clone(self) -> "BBox":
        return BBox(self.x0, self.y0, self.x1, self.y1)

    def merge(self, other: "BBox") -> "BBox":
        return BBox(
            min(self.x0, other.x0),
            min(self.y0, other.y0),
            max(self.x1, other.x1),
            max(self.y1, other.y1),
        )

    def __repr__(self):
        return f"BBox(x0={self.x0}, y0={self.y0}, x1={self.x1}, y1={self.y1})"

    def __eq__(self, other):
        if not isinstance(other, BBox):
            return False
        return (
            self.x0 == other.x0
            and self.y0 == other.y0
            and self.x1 == other.x1
            and self.y1 == other.y1
        )

    def to_json(self):
        return {"x0": self.x0, "y0": self.y0, "x1": self.x1, "y1": self.y1}

    @classmethod
    def from_json(cls, json_data):
        return cls(
            x0=json_data["x0"],
            y0=json_data["y0"],
            x1=json_data["x1"],
            y1=json_data["y1"],
        )


class Char:
    def __init__(self, text: str, fontname: str, size: float, bbox: BBox):
        if len(text) != 1:
            raise ArgumentStructureError(f"Char text={text} must be a single character")
        self.text = text
        self.fontname = fontname
        self.size = size
        self.bbox = bbox

    def to_json(self):
        return {
            "text": self.text,
            "fontname": self.fontname,
            "size": self.size,
            "bbox": self.bbox.to_json(),
        }

    def __repr__(self):
        return f"Char({self.text!r}, font={self.fontname}, size={self.size})"

    @property
    def width(self):
        return self.bbox.width

    @property
    def height(self):
        return self.bbox.height

    @property
    def bold(self):
        return "bold" in self.fontname.lower()

    @property
    def italic(self):
        return "italic" in self.fontname.lower() or "oblique" in self.fontname.lower()

    @classmethod
    def from_json(cls, json_data):
        return cls(
            text=json_data["text"],
            fontname=json_data["fontname"],
            size=json_data["size"],
            bbox=BBox.from_json(json_data["bbox"]),
        )

    def __eq__(self, other):
        if not isinstance(other, Char):
            return False
        return (
            self.text == other.text
            and self.fontname == other.fontname
            and abs(self.size - other.size) < CHAR_SIZE_TOLERANCE
            and self.bbox == other.bbox
        )


class Run:
    def __init__(
        self, fontname: str, size: float, text: str = None, chars: List[Char] = None
    ):
        self.fontname = fontname
        self.size = size
        self.chars = []
        if text is not None:
            for char in text:
                self.chars.append(
                    Char(text=char, fontname=fontname, size=size, bbox=BBox(0, 0, 0, 0))
                )
        elif chars is not None:
            self.chars = chars

    @property
    def text(self):
        return "".join(c.text for c in self.chars)

    @property
    def bbox(self):
        chars_bboxs = [char.bbox for char in self.chars]
        x0 = min(bbox.x0 for bbox in chars_bboxs)
        y0 = min(bbox.y0 for bbox in chars_bboxs)
        x1 = max(bbox.x1 for bbox in chars_bboxs)
        y1 = max(bbox.y1 for bbox in chars_bboxs)
        return BBox(x0, y0, x1, y1)

    def append_char(self, char):
        self.chars.append(char)

    def __add__(self, other):
        if not isinstance(other, Run):
            raise TypeError(f"Cannot add Run with {type(other)}")
        combined_chars = self.chars + other.chars
        return Run(fontname=self.fontname, size=self.size, chars=combined_chars)

    def __eq__(self, other):
        if not isinstance(other, Run):
            return False
        return (
            self.fontname == other.fontname
            and abs(self.size - other.size) < CHAR_SIZE_TOLERANCE
            and self.text == other.text
            and len(self.chars) == len(other.chars)
            and all(c1.bbox == c2.bbox for c1, c2 in zip(self.chars, other.chars))
        )

    def to_json(self):
        return {
            "fontname": self.fontname,
            "size": self.size,
            "text": self.text,
            "chars": [c.to_json() for c in self.chars],
        }

    def __repr__(self):
        return f"Run(text={self.text!r}, font={self.fontname}, size={self.size}, bbox={self.bbox})"

    @classmethod
    def from_text(cls, text, fontname, size):
        return cls(fontname=fontname, size=size, text=text)

    @classmethod
    def from_chars(cls, chars, fontname=None, size=None):
        if not chars:
            raise ValueError("Cannot create Run from empty chars list")
        fontname = fontname or chars[0].fontname
        size = size or chars[0].size
        return cls(fontname=fontname, size=size, chars=chars)

    @classmethod
    def from_json(cls, json_data):
        chars = [Char.from_json(char_data) for char_data in json_data["chars"]]
        return cls(fontname=json_data["fontname"], size=json_data["size"], chars=chars)

    def is_bold(self):
        return "bold" in self.fontname.lower()

    def is_italic(self):
        return "italic" in self.fontname.lower() or "oblique" in self.fontname.lower()


class BoxElement:
    pass


class Line(BoxElement):
    def __init__(self, bbox: BBox):
        self.runs = []
        self.bbox = bbox

    @property
    def text(self):
        return "".join(run.text for run in self.runs)

    def add_run(self, run):
        self.runs.append(run)

    def get_all_chars(self):
        return [char for run in self.runs for char in run.chars]

    def to_json(self):
        return {
            "bbox": self.bbox.to_json(),
            "text": self.text,
            "runs": [r.to_json() for r in self.runs],
        }

    def __repr__(self):
        return f"Line(text={self.text!r})"

    @classmethod
    def from_json(cls, json_data):
        runs = [Run.from_json(run_data) for run_data in json_data["runs"]]
        line = cls(bbox=BBox.from_json(json_data["bbox"]))
        line.runs = runs
        return line

    def __eq__(self, other):
        if not isinstance(other, Line):
            return False
        return (
            self.bbox == other.bbox
            and len(self.runs) == len(other.runs)
            and all(r1 == r2 for r1, r2 in zip(self.runs, other.runs))
        )


class Image(BoxElement):
    def __init__(
        self, bbox: BBox, stream: bytes = None, name: str = "", mimetype: str = None
    ):
        self.bbox = bbox
        self.stream = stream
        self.name = name
        self.mimetype = mimetype

    def to_json(self):
        return {
            "bbox": self.bbox.to_json(),
            "stream": base64.b64encode(self.stream).decode("utf-8")
            if self.stream
            else None,
            "name": self.name,
            "mimetype": self.mimetype,
        }

    @classmethod
    def from_json(cls, json_data):
        stream = json_data.get("stream")
        if stream:
            stream = base64.b64decode(stream)
        return cls(
            bbox=BBox.from_json(json_data["bbox"]),
            stream=stream,
            name=json_data.get("name", ""),
            mimetype=json_data.get("mimetype"),
        )

    def __repr__(self):
        return f"Image(name={self.name}, bbox={self.bbox})"

    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        return (
            self.bbox == other.bbox
            and self.stream == other.stream
            and self.name == other.name
            and self.mimetype == other.mimetype
        )


class Box:
    def __init__(self, bbox: BBox):
        self.bbox = bbox
        self.elements: List[BoxElement] = []

    @property
    def text(self):
        return "\n".join(el.text for el in self.elements if isinstance(el, Line))

    def add_line(self, line):
        if not isinstance(line, Line):
            raise ValueError("Line must be a Line")
        self.elements.append(line)

    def add_image(self, image):
        if not isinstance(image, Image):
            raise ValueError("Image must be an Image")
        self.elements.append(image)

    def get_all_lines(self):
        return [el for el in self.elements if isinstance(el, Line)]

    def get_all_images(self):
        return [el for el in self.elements if isinstance(el, Image)]

    def get_all_chars(self):
        return [
            char
            for el in self.elements
            if isinstance(el, Line)
            for char in el.get_all_chars()
        ]

    def merge(self, other: "Box") -> "Box":
        new_bbox = self.bbox.merge(other.bbox)
        merged_box = Box(new_bbox)

        for element in self.elements:
            if isinstance(element, Line):
                merged_box.add_line(element)
            elif isinstance(element, Image):
                merged_box.add_image(element)

        for element in other.elements:
            if isinstance(element, Line):
                merged_box.add_line(element)
            elif isinstance(element, Image):
                merged_box.add_image(element)

        return merged_box

    def to_json(self):
        return {
            "bbox": self.bbox.to_json(),
            "text": self.text,
            "elements": [
                {"type": "line", **el.to_json()}
                if isinstance(el, Line)
                else {"type": "image", **el.to_json()}
                for el in self.elements
            ],
        }

    def __repr__(self):
        return f"Box(lines={len(self.get_all_lines())}, images={len(self.get_all_images())})"

    @classmethod
    def from_json(cls, json_data):
        box = cls(BBox.from_json(json_data["bbox"]))
        for el_data in json_data["elements"]:
            if el_data["type"] == "line":
                box.add_line(Line.from_json(el_data))
            elif el_data["type"] == "image":
                box.add_image(Image.from_json(el_data))
        return box

    def __eq__(self, other):
        if not isinstance(other, Box):
            return False
        return (
            self.bbox == other.bbox
            and len(self.elements) == len(other.elements)
            and all(l1 == l2 for l1, l2 in zip(self.elements, other.elements))
        )


class Page:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.boxes = []

    @property
    def text(self):
        return "\n".join(box.text for box in self.boxes)

    def add_box(self, box):
        self.boxes.append(box)

    def get_all_runs(self, merge=True):
        runs = []
        for line in self.get_all_lines():
            runs.extend(line.runs)
        return merge_runs(runs) if merge else runs

    def get_all_lines(self):
        lines = []
        for box in self.boxes:
            lines.extend(box.get_all_lines())
        return lines

    def get_all_chars(self):
        chars = []
        for box in self.boxes:
            chars.extend(box.get_all_chars())
        return chars

    def to_json(self):
        return {
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "boxes": [b.to_json() for b in self.boxes],
        }

    def __repr__(self):
        return f"Page({self.width}x{self.height}, boxes={len(self.boxes)})"

    @classmethod
    def from_json(cls, json_data):
        page = cls(json_data["width"], json_data["height"])
        for box_data in json_data["boxes"]:
            page.add_box(Box.from_json(box_data))
        return page

    def append_run(self, run):
        last_box = self.boxes[-1]
        new_line = Line(last_box.bbox)
        new_line.add_run(run)
        last_box.add_line(new_line)

    def __eq__(self, other):
        if not isinstance(other, Page):
            return False
        return (
            self.width == other.width
            and self.height == other.height
            and len(self.boxes) == len(other.boxes)
            and all(b1 == b2 for b1, b2 in zip(self.boxes, other.boxes))
        )


class Document:
    def __init__(self):
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

    @property
    def text(self):
        return "\n".join(page.text for page in self.pages)

    @property
    def chars(self):
        return self.get_all_chars()

    def get_all_pages(self):
        return self.pages

    def get_all_boxes(self):
        boxes = []
        for p in self.pages:
            boxes.extend(p.boxes)
        return boxes

    def get_all_lines(self):
        lines = []
        for p in self.pages:
            lines.extend(p.get_all_lines())
        return lines

    def get_all_chars(self):
        chars = []
        for p in self.pages:
            chars.extend(p.get_all_chars())
        return chars

    def get_all_runs(self, merge=True):
        runs = []
        for line in self.get_all_lines():
            runs.extend(line.runs)
        return merge_runs(runs) if merge else runs

    def get_text(self):
        return "\n".join(page.text for page in self.pages)

    def to_json(self):
        return {"text": self.text, "pages": [p.to_json() for p in self.pages]}

    def __repr__(self):
        return f"Document(pages={len(self.pages)})"

    @classmethod
    def from_json(cls, json_data):
        doc = cls()
        for page_data in json_data["pages"]:
            doc.add_page(Page.from_json(page_data))
        return doc

    def __eq__(self, other):
        if not isinstance(other, Document):
            return False
        return len(self.pages) == len(other.pages) and all(
            p1 == p2 for p1, p2 in zip(self.pages, other.pages)
        )


def merge_runs(runs: List):
    if not runs:
        return []
    merged_runs = []
    current_run = runs[0]
    for next_run in runs[1:]:
        same_font = next_run.fontname == current_run.fontname
        same_size = isclose(next_run.size, current_run.size, abs_tol=0.01)
        if same_font and same_size:
            current_run = current_run + next_run
        else:
            merged_runs.append(current_run)
            current_run = next_run
    merged_runs.append(current_run)
    return merged_runs
