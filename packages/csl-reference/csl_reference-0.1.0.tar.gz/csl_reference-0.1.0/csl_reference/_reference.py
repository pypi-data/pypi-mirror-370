# SPDX-FileCopyrightText: 2025-present The CSL-Reference Team <https://github.com/Fusion-Power-Plant-Framework/csl-reference>
#
# SPDX-License-Identifier: MIT

"""Package to represent references."""

from __future__ import annotations

import enum
import logging
import warnings
from typing import Any, Literal

from citeproc import (
    Citation,
    CitationItem,
    CitationStylesBibliography,
    CitationStylesStyle,
    formatter,
)
from citeproc.source.json import CiteProcJSON
from pydantic import BaseModel, Field

logging.basicConfig()
logger = logging.getLogger("reference")
logger.setLevel(logging.INFO)


__all__ = ["DateVariable", "NameVariable", "Reference", "ReferenceType"]


class ReferenceType(str, enum.Enum):
    """String enumeration of the possible values for a reference type."""

    article = "article"
    article_journal = "article-journal"
    article_magazine = "article-magazine"
    article_newspaper = "article-newspaper"
    bill = "bill"
    book = "book"
    broadcast = "broadcast"
    chapter = "chapter"
    classic = "classic"
    collection = "collection"
    dataset = "dataset"
    document = "document"
    entry = "entry"
    entry_dictionary = "entry-dictionary"
    entry_encyclopedia = "entry-encyclopedia"
    event = "event"
    figure = "figure"
    graphic = "graphic"
    hearing = "hearing"
    interview = "interview"
    legal_case = "legal_case"
    legislation = "legislation"
    manuscript = "manuscript"
    map = "map"
    motion_picture = "motion_picture"
    musical_score = "musical_score"
    pamphlet = "pamphlet"
    paper_conference = "paper-conference"
    patent = "patent"
    performance = "performance"
    periodical = "periodical"
    personal_communication = "personal_communication"
    post = "post"
    post_weblog = "post-weblog"
    regulation = "regulation"
    report = "report"
    review = "review"
    review_book = "review-book"
    software = "software"
    song = "song"
    speech = "speech"
    standard = "standard"
    thesis = "thesis"
    treaty = "treaty"
    webpage = "webpage"


class _CslBaseModel(BaseModel, populate_by_name=True):
    """Base class for Pydantic models for CSL JSON data structures."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pydantic aliases + the 'populate_by_name' setting, means that
        # fields can be set either by their name, or their alias. The
        # name is ignored if the alias is present, so let users know
        # with a warning.
        for kwarg in kwargs:
            if (field_info := type(self).model_fields.get(kwarg)) and (
                field_info.alias in kwargs
            ):
                logger.warning(
                    f"Fields {type(self).__name__}.{kwarg} and "
                    f"{type(self).__name__}.{field_info.alias} are both set for "
                    f"reference with ID {self.id}. "
                    f"Ignoring {type(self).__name__}.{kwarg}."
                )

    def __repr__(self) -> str:
        """
        Generate a string representation for the structure.

        Make the output more compact by only displaying fields that have
        been set.
        """  # noqa: DOC201
        args = (
            f"{f}={value!r}"
            for f in self.model_fields_set
            if (value := getattr(self, f)) is not None
        )
        return f"{self.__class__.__name__}({', '.join(args)})"


class NameVariable(_CslBaseModel):
    """Pydantic model for a name within a :class:`.Reference`."""

    family: str | None = None
    given: str | None = None
    dropping_particle: str | None = Field(None, alias="dropping-particle")
    non_dropping_particle: str | None = Field(None, alias="non-dropping-particle")
    suffix: str | None = None
    comma_suffix: str | float | bool | None = Field(None, alias="comma-suffix")
    static_ordering: str | float | bool | None = Field(None, alias="static-ordering")
    literal: str | None = None
    parse_names: str | float | bool | None = Field(None, alias="parse-names")


class DateVariable(_CslBaseModel):
    """Pydantic model for a date within a :class:`.Reference`."""

    date_parts: list[list[str | float]] | None = Field(
        None, alias="date-parts", max_length=2, min_length=1
    )
    season: str | float | None = None
    circa: str | float | bool | None = None
    literal: str | None = None
    raw: str | None = None


class Reference(_CslBaseModel):
    """
    Class representing a reference.

    The only required fields are ``type`` and ``id``.

    The class is designed to be CSL JSON compliant on serialization and
    deserialization. Use the :meth:`.Reference.csl_dump` method to
    perform CSL-compatible serialization.

    Notes
    -----
    This class uses `citeproc-py` as a CSL processor. `citeproc-py`
    implements the CSL v1.0.1 specification, hence that is what this
    class supports.

    The fields of this class were generated using the
    'datamodel-code-generator (v0.25.2)' tool on the CSL JSON schema.
    With manual updates like aliases to make the class more Pythonic.

    CSL JSON schema:
    https://github.com/citation-style-language/schema/blob/40b3ce0b/schemas/input/csl-data.json
    """

    id: str | float
    type: ReferenceType

    # Optional
    abstract: str | None = None
    accessed: DateVariable | None = None
    annote: str | None = None
    archive_collection: str | None = None
    archive_location: str | None = None
    archive_place: str | None = Field(None, alias="archive-place")
    archive: str | None = None
    author: list[NameVariable] | None = None
    authority: str | None = None
    available_date: DateVariable | None = Field(None, alias="available-date")
    call_number: str | None = Field(None, alias="call-number")
    categories: list[str] | None = None
    chair: list[NameVariable] | None = None
    chapter_number: str | float | None = Field(None, alias="chapter-number")
    citation_key: str | None = Field(None, alias="citation-key")
    citation_label: str | None = Field(None, alias="citation-label")
    citation_number: str | float | None = Field(None, alias="citation-number")
    collection_editor: list[NameVariable] | None = Field(None, alias="collection-editor")
    collection_number: str | float | None = Field(None, alias="collection-number")
    collection_title: str | None = Field(None, alias="collection-title")
    compiler: list[NameVariable] | None = None
    composer: list[NameVariable] | None = None
    container_author: list[NameVariable] | None = Field(None, alias="container-author")
    container_title_short: str | None = Field(None, alias="container-title-short")
    container_title: str | None = Field(None, alias="container-title")
    contributor: list[NameVariable] | None = None
    curator: list[NameVariable] | None = None
    dimensions: str | None = None
    director: list[NameVariable] | None = None
    division: str | None = None
    doi: str | None = Field(None, alias="DOI")
    edition: str | float | None = None
    editor: list[NameVariable] | None = None
    editorial_director: list[NameVariable] | None = Field(
        None, alias="editorial-director"
    )
    event_date: DateVariable | None = Field(None, alias="event-date")
    event_place: str | None = Field(None, alias="event-place")
    event_title: str | None = Field(None, alias="event-title")
    event: str | None = Field(
        None,
        description="[Deprecated - use 'event-title' instead. Will be removed in 1.1]",
    )
    executive_producer: list[NameVariable] | None = Field(
        None, alias="executive-producer"
    )
    first_reference_note_number: str | float | None = Field(
        None, alias="first-reference-note-number"
    )
    genre: str | None = None
    guest: list[NameVariable] | None = None
    host: list[NameVariable] | None = None
    illustrator: list[NameVariable] | None = None
    interviewer: list[NameVariable] | None = None
    isbn: str | None = Field(None, alias="ISBN")
    issn: str | None = Field(None, alias="ISSN")
    issue: str | float | None = None
    issued: DateVariable | None = None
    journal_abbreviation: str | None = Field(None, alias="journalAbbreviation")
    jurisdiction: str | None = None
    keyword: str | None = None
    language: str | None = None
    locator: str | float | None = None
    medium: str | None = None
    narrator: list[NameVariable] | None = None
    note: str | None = None
    number_of_pages: str | float | None = Field(None, alias="number-of-pages")
    number_of_volumes: str | float | None = Field(None, alias="number-of-volumes")
    number: str | float | None = None
    organizer: list[NameVariable] | None = None
    original_author: list[NameVariable] | None = Field(None, alias="original-author")
    original_date: DateVariable | None = Field(None, alias="original-date")
    original_publisher_place: str | None = Field(None, alias="original-publisher-place")
    original_publisher: str | None = Field(None, alias="original-publisher")
    original_title: str | None = Field(None, alias="original-title")
    page_first: str | float | None = Field(None, alias="page-first")
    page: str | float | None = None
    part_title: str | None = Field(None, alias="part-title")
    part: str | float | None = None
    performer: list[NameVariable] | None = None
    pmcid: str | None = Field(None, alias="PMCID")
    pmid: str | None = Field(None, alias="PMID")
    printing: str | float | None = None
    producer: list[NameVariable] | None = None
    publisher_place: str | None = Field(None, alias="publisher-place")
    publisher: str | None = None
    recipient: list[NameVariable] | None = None
    references: str | None = None
    reviewed_author: list[NameVariable] | None = Field(None, alias="reviewed-author")
    reviewed_genre: str | None = Field(None, alias="reviewed-genre")
    reviewed_title: str | None = Field(None, alias="reviewed-title")
    scale: str | None = None
    script_writer: list[NameVariable] | None = Field(None, alias="script-writer")
    section: str | None = None
    series_creator: list[NameVariable] | None = Field(None, alias="series-creator")
    short_title: str | None = Field(None, alias="shortTitle")
    source: str | None = None
    status: str | None = None
    submitted: DateVariable | None = None
    supplement: str | float | None = None
    title_short: str | None = Field(None, alias="title-short")
    title: str | None = None
    translator: list[NameVariable] | None = None
    url: str | None = Field(None, alias="URL")
    version: str | None = None
    volume_title_short: str | None = Field(None, alias="volume-title-short")
    volume_title: str | None = Field(None, alias="volume-title")
    volume: str | float | None = None
    year_suffix: str | None = Field(None, alias="year-suffix")
    custom: dict[str, Any] | None = Field(
        None,
        description=(
            "Used to store additional information that does not have a designated CSL "
            "JSON field. The custom field is preferred over the note field for storing "
            "custom data, particularly for storing key-value pairs, as the note field "
            "is used for user annotations in annotated bibliography styles."
        ),
        examples=[
            {"short_id": "xyz", "other-ids": ["alternative-id"]},
            {"metadata-double-checked": True},
        ],
        title="Custom key-value pairs.",
    )

    def csl_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
        exclude_unset: bool = True,
        exclude_defaults: bool = True,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        """
        Generate a dictionary representation of the model conforming to CSL.

        This is a wrapper around ``model_dump`` configured such that the
        output is CSL-JSON compatible.

        See :meth:`pydantic.BaseModel.model_dump` for parameter
        descriptions.

        Returns
        -------
        :
            dictionary representation of reference
        """
        return super().model_dump(
            mode=mode,
            # Include all.
            include=None,
            # Do not exclude any (set) fields.
            exclude=None,
            # Always dump keys by aliases.
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=False,
            round_trip=round_trip,
            warnings=warnings,
        )

    def __str__(self) -> str:
        """Format the reference as a bibliography string."""  # noqa: DOC201
        return str(self._make_bib().bibliography()[0])

    def _make_bib(self) -> CitationStylesBibliography:
        sources = self._make_citeproc_source()
        bib = CitationStylesBibliography(
            style=CitationStylesStyle("harvard1", validate=False),
            source=sources,
            formatter=formatter.plain,
        )
        bib.register(Citation([CitationItem(s) for s in sources]))
        return bib

    def _make_citeproc_source(self) -> CiteProcJSON:
        csl_dict = self.csl_dump()
        with warnings.catch_warnings():
            # citeproc is very noisy when reading references with unknown
            # fields.
            # Swallow these warnings as the only point we would want to warn
            # users about unknown fields is when importing new references.
            warnings.filterwarnings(
                "ignore",
                message="The following arguments for .* are unsupported",
            )
            return CiteProcJSON([csl_dict])
