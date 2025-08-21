# Standard Libraries
from pathlib import Path
from typing import Tuple, Sequence
from dataclasses import make_dataclass
from copy import copy
import re
from warnings import warn
import os

# Relative Imports
from .types import PathLike
from .reader import HDF5Reader, Bookshelf, Book, Page

# Constants
PYI_FILE = Path(__file__).with_suffix(".pyi")
TYPE_ALIASES = "PathLike = str | os.PathLike | Path"
FUNC_DEFS = "def add_file_to_library(file_path: PathLike) -> None: ..."
INDENT = "    "

if not PYI_FILE.exists():
    PYI_FILE.touch()

path_pattern = re.compile(r"\w:(?:\\\\\w+)+.hdf5")
libcache_pattern = re.compile(
    r"libcache\s=\s\[(?:\r?\n\s{4}\"\w:(?:\\\\\w+)+.hdf5\",)+"
)

with open(PYI_FILE) as f:
    file_string = f.read()
    libcache_list = re.findall(libcache_pattern, file_string)
    if len(libcache_list) > 0:
        libcache_string = libcache_list[0]
    else:
        libcache_string = ""

libcache = [
    Path(i).__str__() for i in (re.findall(path_pattern, libcache_string))
]


def bind_book(book: Book) -> None:

    book_cls = make_dataclass(
        book.name.capitalize(), [(page.name, Page) for page in book.pages]
    )
    bound_book = book_cls(**{page.name: page for page in book.pages})

    book.book_type = book_cls
    book.typed_object = bound_book


def build_bookshelf(file_path: PathLike) -> Bookshelf:
    reader = HDF5Reader(file_path)

    for book in reader.bookshelf.books:
        bind_book(book)

    bookshelf_cls = make_dataclass(
        reader.bookshelf.name,
        [
            (book.name.lower(), book.book_type)
            for book in (reader.bookshelf.books)
        ]
        + [
            (page.name.lower(), Page)
            for page in (reader.bookshelf.loose_pages)
        ],
    )

    books = {
        book.name.lower(): book.typed_object
        for book in (reader.bookshelf.books)
    }
    loose_pages = {
        page.name.lower(): page for page in reader.bookshelf.loose_pages
    }

    bookshelf_constructor = {**books, **loose_pages}
    built_bookshelf = bookshelf_cls(**bookshelf_constructor)

    reader.bookshelf.shelf_type = bookshelf_cls
    reader.bookshelf.typed_object = built_bookshelf

    return reader.bookshelf


class StubFileString:
    def __init__(
        self,
        # h5lib: H5Library,
        import_list: list[Tuple[str, str]] = [],
        starting_bookshelves: list[Bookshelf] = [],
    ):
        import_list += [("pathlib", "Path"), ("", "os")]
        self.import_statements = ""
        for i in import_list:
            if len(i[0]) != 0:
                self.import_statements += f"from {i[0]} import {i[1]}\n"
            else:
                self.import_statements += f"import {i[1]}"
        self.bookshelf_list: list[Bookshelf] = []
        self.book_set: set[Tuple[str, Tuple]] = set()
        self.classes = ""
        self.libclass = ""
        self.libcache = "\n\nlibcache = [\n"

        self._write_libcache()

        for shelf in starting_bookshelves:
            self.add_bookshelf(shelf)

    def _write_libcache(self):
        global libcache
        if len(libcache) == 0:
            self.libcache += "]\n"
            warn("Your H5Library is empty. Please add bookshelves.")
            return
        self.libcache = "\n\nlibcache = [\n"
        for shelf in self.bookshelf_list:
            self.libcache += f'{INDENT}"{shelf.path}",\n'
        self.libcache += "]\n"

    def _write_classes(
        self, class_list: list[Tuple[str, Sequence[Tuple[str, str]]]]
    ):
        for class_name, attr_list in class_list:
            self.classes += f"class {class_name}:"
            if len(attr_list) == 0:
                self.classes += f"\n{INDENT}...\n"
            else:
                self.classes += "\n"
            for attr in attr_list:
                self.classes += f"{INDENT}{attr[0]}: {attr[1]}\n"
            self.classes += "\n\n"

    def _write_libclass(self):
        self.libclass = "class H5LibraryClass:\n"
        for i in self.bookshelf_list:
            self.libclass += (
                f"{INDENT}{i.name.lower()}: " f"{i.name.capitalize()}\n"
            )
        self.libclass += (
            f"{INDENT}def add_bookshelf(self, "
            "p: PathLike | Bookshelf) -> None: ...\n\n"
        )
        self.libclass += "\nH5Library: H5LibraryClass\n"

    def add_bookshelf(self, shelf: Bookshelf) -> None:
        global libcache

        if shelf.path in libcache:
            print(f"{shelf.name.lower()} is an already existing bookshelf.")
            return None

        self.bookshelf_list.append(shelf)
        book_attr_types: dict[str, list[str]] = {}
        old_book_set = copy(self.book_set)
        for book in shelf.books:
            self.book_set.add(
                (
                    book.book_type.__name__,
                    tuple(book.typed_object.__dataclass_fields__.keys()),
                )
            )
            book_attr_types[book.book_type.__name__] = [
                i.type.__name__
                for i in (book.typed_object.__dataclass_fields__.values())
            ]
        book_set_with_types: list[Tuple[str, Sequence[Tuple[str, str]]]] = []
        for class_name, class_attr in self.book_set - old_book_set:
            book_set_with_types.append(
                (
                    class_name,
                    [
                        (attr_name, attr_type)
                        for attr_name, attr_type in zip(
                            class_attr, book_attr_types[class_name]
                        )
                    ],
                )
            )

        self._write_classes(
            [(cls_nm, cls_attrs) for cls_nm, cls_attrs in book_set_with_types]
        )

        self._write_classes(
            [
                (
                    shelf.shelf_type.__name__,
                    [
                        (k.lower(), v.type.__name__)
                        for k, v in (
                            shelf.typed_object.__dataclass_fields__.items()
                        )
                    ],
                )
            ]
        )

        self._write_libclass()

        libcache.append(shelf.path)

        self._write_libcache()

    def compile(self):
        with open(PYI_FILE, "w") as f:
            f.write(self.import_statements)
            f.write("\n\n")
            f.write(TYPE_ALIASES)
            f.write("\n\n\n")
            f.write(FUNC_DEFS)
            f.write("\n\n\n")
            f.write(self.classes)
            f.write(self.libclass)
            f.write(self.libcache)


class H5LibraryClass:
    """
    Represents several HDF5 files (Bookshelves) that have been stubbed to
    enable statically-typed reading.

    Parameters
    ----------
    None

    Methods
    -------
    add_bookshelf()

    Examples
    --------
    ```
    from h5lib import H5Library  # warning: No bookshelves in the library.
    mypath = ".../*.hdf5"
    H5Library.add_bookshelf(mypath)
    dataset = H5Library.bookshelf.book.page  # Fields are autocomplete enabled.
    ```
    """

    def __init__(self) -> None:
        global libcache
        starting_shelves = [build_bookshelf(i) for i in libcache]

        self._stub_file = StubFileString(
            import_list=[(".reader", "Page"), (".reader", "Bookshelf")],
            starting_bookshelves=starting_shelves,
        )

        for shelf in starting_shelves:
            setattr(
                self, shelf.shelf_type.__name__.lower(), shelf.typed_object
            )

        self._stub_file._write_libclass()
        self._stub_file.compile()

    def add_bookshelf(self, p: Bookshelf | PathLike) -> None:
        if isinstance(p, PathLike):
            global libcache
            libcache.append(Path(p).__str__())
            shelf = build_bookshelf(p)
        else:
            shelf = p
        setattr(self, shelf.shelf_type.__name__.lower(), shelf.typed_object)
        self._stub_file.add_bookshelf(shelf)
        self._stub_file.compile()

    def clear(self):
        os.remove(PYI_FILE)


H5Library = H5LibraryClass()


def add_file_to_library(filepath: PathLike) -> None:
    global H5Library
    shelf = build_bookshelf(filepath)
    H5Library.add_bookshelf(shelf)
