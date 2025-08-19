from pytest import mark

from seedcase_sprout import (
    ContributorProperties,
    LicenseProperties,
    PackageProperties,
    ResourceProperties,
    as_readme_text,
)


def test_creates_readme():
    """Should be able to create a README for a set of properties."""
    properties = PackageProperties(
        name="diabetes-hypertension-study",
        title="Diabetes and Hypertension Study",
        homepage="www.my-page.com/diabetes-2021",
        id="123-abc-123",
        description="This is my package.",
        version="2.0.0",
        created="2024-05-14T05:00:01+00:00",
        contributors=[
            ContributorProperties(
                title="Jamie Jones",
                email="jamie_jones@example.com",
                path="example.com/jamie_jones",
                roles=["creator"],
            )
        ],
        resources=[
            ResourceProperties(
                title="First Resource", description="This is my first resource."
            ),
            ResourceProperties(
                title="Second Resource", description="This is my second resource."
            ),
        ],
        licenses=[
            LicenseProperties(
                name="ODC-BY-1.0",
                path="https://opendatacommons.org/licenses/by",
                title="Open Data Commons Attribution License 1.0",
            ),
            LicenseProperties(
                name="APL-1.0",
                path="https://opensource.org/license/apl1-0-php",
                title="Adaptive Public License 1.0",
            ),
        ],
    )
    assert as_readme_text(properties)


def test_creates_readme_with_empty_values():
    """Should be able to create a README for an empty set of properties."""
    assert as_readme_text(PackageProperties())


@mark.parametrize(
    "description, expected",
    [
        # Empty or whitespace-only.
        ("", ""),
        ("    ", ""),
        # Single line text.
        ("Non-indented one-line text.", "Non-indented one-line text."),
        ("    Indented one-line text.", "Indented one-line text."),
        (
            "    Indented one-line text with trailing whitespace.   ",
            "Indented one-line text with trailing whitespace.   ",
        ),
        # Multiline text.
        ("Non-indented\nmultiline\ntext.", "Non-indented\nmultiline\ntext."),
        ("    Indented\n    multiline text.", "Indented\nmultiline text."),
        (
            """Non-indented first line,
            indented second line.""",
            "Non-indented first line,\nindented second line.",
        ),
        (
            """
            Indented multiline
            text
            """,
            "Indented multiline\ntext",
        ),
        # Tab indentation.
        (
            "\tIndented with tab\n\tAlso indented with tab",
            "Indented with tab\nAlso indented with tab",
        ),
        # Mixed indentation.
        (
            "\tIndented with tab\n    Indented with spaces\n\t  Mixed indented line",
            "Indented with tab\nIndented with spaces\nMixed indented line",
        ),
        (
            "  Indented with 2 spaces\n    Indented with 4 spaces\n  Back to 2 spaces",
            "Indented with 2 spaces\nIndented with 4 spaces\nBack to 2 spaces",
        ),
        # Multi-level list (relative indentation removed, not ideal).
        (
            """
            Description with multilevel list:
            - Item 1
                - Item 2""",
            "Description with multilevel list:\n- Item 1\n- Item 2",
        ),
    ],
)
def test_dedents_multiline_description(description, expected):
    """Should be able to dedent description."""
    properties = PackageProperties(
        name="diabetes-hypertension-study",
        description=description,
    )

    readme_text = as_readme_text(properties)
    assert expected in readme_text
