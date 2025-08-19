# Contributing

## Issues and bugs :bug:

The easiest way to contribute is to report issues or bugs that you might
find while using Sprout. You can do this by creating a
[new](https://github.com/seedcase-project/seedcase-sprout/issues/new/choose)
issue on our GitHub repository.

## Adding or modifying content :pencil2:

If you would like to contribute content, please check out our
[guidebook](https://guidebook.seedcase-project.org/) for more specific
details on how we work and develop. It is a regularly evolving document,
so is at various states of completion.

To install Sprout to contribute, you first need to install
[uv](https://docs.astral.sh/uv/) and
[justfile](https://just.systems/man/en/packages.html). We use uv and
justfile to manage our project, such as to install development
dependencies. Both the uv and justfile websites have a more detailed guide on
using uv, but below are some simple instructions to get you started.

To install uv, run:

``` bash
pipx install uv
```

Then, open a terminal so that the working directory is the root of this
project (`seedcase-sprout/`) and run:

``` bash
just install-deps
```

We keep all our development workflows in the `justfile`, so you can
explore it to see what commands are available. To see a list of commands
available, run:

``` bash
just
```
