#import "@local/ratio-theme:0.1.0": *
#import variants.report: *

#show: {
  themed(
    info: (
      title: [Example document title],
      abstract: [An example document using the Ratio theme.],
      authors: (
        (name: "Jane Doe", affiliation: none, contact: none),
        (name: "John Doe", affiliation: "Foo Inc.", contact: "https://bar.foo.inc"),
      ),
      date: datetime(year: 2024, month: 12, day: 18),
      keywords: (),
    ),
    cover: (hero: orange),
    frontmatter: [
      = Hello world
      Hello world, this is an introduction.
    ],
  )
}
