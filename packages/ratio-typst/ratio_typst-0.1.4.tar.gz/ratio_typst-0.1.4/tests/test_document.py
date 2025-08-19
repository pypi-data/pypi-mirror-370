"""Overarching Document tests."""

import pytest
from pypst import Plain

from ratio_typst.document import (
    Author,
    Cover,
    DocumentBar,
    Info,
    NavigationBar,
    PageBar,
    ProgressBar,
    Theme,
    Themed,
)


@pytest.mark.parametrize(
    "obj,rendered",
    [
        (
            Author(),
            "#(name: none, affiliation: none, contact: none)",
        ),
        (
            Author(name="Foo", affiliation="https://foo.bar", contact="foo@bar.baz"),
            '#(name: "Foo", affiliation: "https://foo.bar", contact: "foo@bar.baz")',
        ),
        (
            Info(),
            "#(authors: (), keywords: ())",
        ),
        (
            Info(
                title="The great Foo",
                authors=[
                    Author(name="Bar"),
                    Author(name="Baz", affiliation="Quux Co."),
                ],
            ),
            '#(title: [The great Foo], authors: ((name: "Bar", affiliation: none, contact: none), '
            '(name: "Baz", affiliation: "Quux Co.", contact: none)), keywords: ())',
        ),
        (
            Cover(),
            "#(:)",
        ),
        (
            Cover(background=Plain("none")),
            "#(background: none)",
        ),
        (
            DocumentBar(),
            '#(kind: "document")',
        ),
        (
            PageBar(),
            '#(kind: "page")',
        ),
        (
            NavigationBar(),
            '#(kind: "navigation")',
        ),
        (
            ProgressBar(),
            '#(kind: "progress")',
        ),
        (
            Themed(),
            "#themed()",
        ),
        (
            Themed(info=Info(title="#lorem(3)"), outline="none", header=NavigationBar()),
            "#themed(info: (title: [#lorem(3)], authors: (), keywords: ()), "
            'outline: none, header: (kind: "navigation"))',
        ),
        (
            Theme(info=Info(title="#lorem(3)"), outline="none", header=NavigationBar()),
            "#show: themed(info: (title: [#lorem(3)], authors: (), keywords: ()), "
            'outline: none, header: (kind: "navigation"))',
        ),
    ],
)
def test_render(obj, rendered):
    assert obj.render() == rendered


def test_empty_report(report, check_typst):
    check_typst(report.render(), "empty_report")


def test_empty_slides(slides, check_typst):
    check_typst(slides.render(), "empty_slides")
