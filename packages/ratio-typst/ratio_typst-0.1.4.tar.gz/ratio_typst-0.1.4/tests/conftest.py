import difflib
import shutil
import subprocess
from datetime import date
from pathlib import Path
from warnings import warn

import typst
from pytest import fixture

from ratio_typst import Author, Info, Report, Theme
from ratio_typst.document import Cover, Slides

HERE = Path(__file__).parent
DATA = HERE / "data"


class FormattingError(Warning):
    """
    Error during formatting using Typstyle. Are you sure it's installed?
    """


@fixture
def data() -> Path:
    """
    Test data directory.
    """
    return DATA


@fixture
def update() -> bool:
    """
    Boolean flag to toggle test update behavior.
    Toggled by the existence of an `.update` file.
    """
    return (HERE / ".update").exists()


@fixture
def check_typst(tmp_path, update):
    """
    Check Typst content for the following:

    - Difference to expected generated Typst content (updated using the `update` flag).
    - Successful Typst compilation (toggled by `compile` flag).
      Output is saved in the data directory.
    - Tries to format the file (toggled by `format` flag).
    """

    def _check_typst(
        text: str,
        ref_name: str,
        compile: bool = True,
        format: bool = True,
        update: bool = update,
    ):
        filename = f"{ref_name}.typ"
        path = tmp_path / filename
        ref_dir = DATA / ref_name
        ref_path = ref_dir / filename

        update = update or not ref_path.exists()

        path.write_text(text, encoding="utf-8")
        lines = text.splitlines(False)

        ref_text = ref_path.read_text(encoding="utf-8") if ref_path.exists() else ""
        ref_lines = ref_text.splitlines(False)

        diff = difflib.unified_diff(
            ref_lines,
            lines,
            fromfile=str(ref_path),
            tofile=str(path),
            lineterm="",
        )
        diffstr = "\n".join(diff)

        if diffstr and update:
            if not ref_dir.exists():
                ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_text(text)
        else:
            assert not diffstr, diffstr

        if compile:
            temp_pdf, data_pdf = path.with_suffix(".pdf"), ref_path.with_suffix(".pdf")
            typst.compile(path, output=temp_pdf)
            if update or not ref_path.with_suffix(".pdf").exists():
                shutil.copyfile(temp_pdf, data_pdf)

        if format:
            try:
                ref_path.with_suffix(".fmt.typ").write_text(
                    subprocess.run(
                        ["typstyle", ref_path, "--column", "100"], capture_output=True
                    ).stdout.decode(),
                    encoding="utf-8",
                )
            except Exception as e:
                warn(str(e), category=FormattingError)

    return _check_typst


@fixture
def cover() -> Cover:
    """Example coverpage settings."""
    return Cover(hero="orange")


@fixture
def info() -> Info:
    """Example document info."""
    return Info(
        title="Example document title",
        abstract="An example document using the Ratio theme.",
        authors=[
            Author("Jane Doe"),
            Author("John Doe", "Foo Inc.", "https://bar.foo.inc"),
        ],
        date=date(year=2024, month=12, day=18),
    )


@fixture
def theme(info, cover) -> Theme:
    """Example theme settings."""
    return Theme(
        info=info, cover=cover, frontmatter="= Hello world\nHello world, this is an introduction."
    )


@fixture
def report(theme) -> Report:
    """Example report document."""
    return Report(theme=theme)


@fixture
def slides(theme) -> Slides:
    """Example slides document."""
    return Slides(theme=theme)
