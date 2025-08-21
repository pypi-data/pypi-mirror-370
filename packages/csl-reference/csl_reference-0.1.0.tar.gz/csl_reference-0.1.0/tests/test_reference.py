# SPDX-FileCopyrightText: 2025-present The CSL-Reference Team <https://github.com/Fusion-Power-Plant-Framework/csl-reference>
#
# SPDX-License-Identifier: MIT
"""Tests for the reference package."""

import logging

import pytest

from csl_reference import Reference
from tests.tools import assert_no_warnings


class TestReference:
    def setup_method(self):
        self.book_ref = Reference(
            id="[1]",
            type="book",
            url="https://www.book.com",
            isbn="1000000000100101010",
        )

    def test_url_kwarg_is_lowercase(self):
        ref = Reference(id="[1]", type="webpage", url="https://www.science.com")

        assert ref.url == "https://www.science.com"

    @pytest.mark.parametrize("field", ["url", "doi", "isbn", "issn", "pmcid", "pmid"])
    def test_field_with_alias_is_deserialized_from_uppercase(self, field):
        ref = Reference.model_validate({
            "id": "[1]",
            "type": "webpage",
            field.upper(): "some_string",
        })

        assert getattr(ref, field) == "some_string"

    @pytest.mark.parametrize("field", ["url", "doi", "isbn", "issn", "pmcid", "pmid"])
    def test_field_with_alias_serialized_in_uppercase(self, field):
        ref = Reference(**{
            "id": "[1]",
            "type": "webpage",
            field: "some_string",
            "chapter_number": 1,
        })

        serialized = ref.model_dump(exclude_unset=True, by_alias=True)

        assert serialized[field.upper()] == "some_string"

    def test_serialization_round_trip_by_alias_successful(self):
        d = self.book_ref.model_dump(by_alias=True, exclude_unset=True)
        parsed_ref = Reference.model_validate(d)

        assert "URL" in d
        assert self.book_ref == parsed_ref

    def test_csl_dump_writes_keys_by_alias(self):
        cls_dict = self.book_ref.csl_dump()

        assert cls_dict["URL"] == "https://www.book.com"
        assert cls_dict["ISBN"] == "1000000000100101010"
        assert cls_dict["id"] == "[1]"

    def test_csl_dump_does_not_return_unset_fields(self):
        cls_dict = self.book_ref.csl_dump()

        assert len(cls_dict) == 4

    def test_str_generates_reference(self):
        ref = Reference(
            id="[1]",
            author=[{"family": "Bohr", "given": "Niels"}],
            title="On the constitution of atoms and molecules",
            volume="26",
            type="article-journal",
            container_title=(
                "The London, Edinburgh, and Dublin Philosophical Magazine "
                "and Journal of Science"
            ),
            issue="151",
            issued={"date-parts": [["1913"]]},
            page="1-25",
            doi="10.1080/14786441308634955",
        )

        str_ref = str(ref)

        assert "[1]" not in str_ref
        assert "Bohr, N." in str_ref
        assert "On the constitution of atoms and molecules" in str_ref
        assert "1913" in str_ref
        assert (
            "The London, Edinburgh, and Dublin Philosophical Magazine "
            "and Journal of Science"
        ) in str_ref
        assert "26(151)" in str_ref
        assert "pp.1–25" in str_ref  # noqa: RUF001

    def test_repr_excludes_unset_fields(self):
        ref = Reference(
            id="[1]",
            author=[{"family": "Bohr", "given": "Niels"}],
            title="On the constitution of atoms and molecules",
            volume="26",
            type="article-journal",
            container_title=(
                "The London, Edinburgh, and Dublin Philosophical Magazine"
                "and Journal of Science"
            ),
            issue="151",
            issued={"date-parts": [["1913"]]},
            page="1-25",
            doi="10.1080/14786441308634955",
        )

        ref_repr = repr(ref)

        assert ref_repr.startswith("Reference(")
        assert "doi" in ref_repr
        assert "volume_title" not in ref_repr
        assert ref_repr.count("=") == 13  # same as no. of = & : in initialisation kwargs

    @pytest.mark.parametrize(
        "constructor",
        [
            lambda d: Reference(**d),
            Reference.model_validate,
        ],
    )
    def test_constructors_prefer_alias_to_name_but_warn(self, constructor, caplog):
        with caplog.at_level(logging.WARNING):
            ref = constructor({
                "id": "[1]",
                "type": "webpage",
                "title-short": "test",
                "URL": "https://www.CAPITALISED.com",
                "url": "https://lowercase.org",
            })

        assert len(caplog.messages) == 1
        assert "Ignoring Reference.url" in caplog.messages[0]
        assert ref.url == "https://www.CAPITALISED.com"

    def test_citeproc_unknown_argument_warnings_are_suppressed(self):
        ref = Reference(
            id="bohr_1913",
            author=[{"family": "Bohr", "given": "Niels"}],
            title="On the constitution of atoms and molecules",
            type="article-journal",
            issued={"date-parts": [["1913"]]},
            # Citeproc doesn't like 'custom'
            custom={"fuelcycle_id": "[1]"},
        )

        with assert_no_warnings():
            str(ref)
