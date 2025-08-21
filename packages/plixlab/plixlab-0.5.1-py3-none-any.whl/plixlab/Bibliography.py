"""
PlixLab Bibliography Module

This module provides functionality for parsing and formatting bibliographic citations
from BibTeX files. It supports various entry types including articles, books, and
software citations with automatic formatting for PlixLab presentations.
"""

import os
from typing import Dict, Any, Optional
from bibtexparser.bparser import BibTexParser


def get_authors(authors_str: str) -> str:
    """
    Generate a formatted string representation of authors from a BibTeX-style string.

    Formats author names according to academic conventions:
    - Single author: "F. M. LastName, "
    - Multiple authors: "FirstAuthor et al."

    Args:
        authors_str (str): Authors string in BibTeX format
                          (e.g., "Last, First Middle and Last2, First2")

    Returns:
        str: Formatted author string ready for citation display

    Examples:
        >>> get_authors("Smith, John and Doe, Jane")
        "J. Smith et al."
        >>> get_authors("Johnson, Alice Marie")
        "A. M. Johnson, "
    """
    if not authors_str:
        return "No authors available."

    # Split the authors string into individual authors
    author_list = [author.strip() for author in authors_str.split(" and ")]

    # List to hold formatted author names
    formatted_names = []

    for author in author_list:
        try:
            # Handle "Last, First Middle" format
            if ", " in author:
                last_name, first_name_middle = author.split(", ", 1)
                name_parts = first_name_middle.split()
            else:
                # Handle "First Middle Last" format
                name_parts = author.split()
                last_name = name_parts[-1] if name_parts else ""
                name_parts = name_parts[:-1]  # Remove last name from parts

            if not name_parts:
                # Only last name available
                formatted_names.append(last_name)
                continue

            # Extract first and middle names
            first_name = name_parts[0]
            middle_names = name_parts[1:] if len(name_parts) > 1 else []

            # Construct the formatted name with initials
            first_initial = f"{first_name[0]}." if first_name else ""
            middle_initials = " ".join([f"{name[0]}." for name in middle_names if name])

            # Combine all parts
            initials_part = " ".join(filter(None, [first_initial, middle_initials]))
            formatted_name = f"{initials_part} {last_name}".strip()
            formatted_names.append(formatted_name)

        except (IndexError, AttributeError):
            # Fallback for malformed author names
            formatted_names.append(author)

    # Generate the final author string based on the number of authors
    if len(formatted_names) == 1:
        return f"{formatted_names[0]}, "
    elif len(formatted_names) > 1:
        return f"{formatted_names[0]} _et al_."
    else:
        return "No authors available."


def render_software(bib_data: Dict[str, Any]) -> str:
    """
    Render a software citation in PlixLab format.

    Args:
        bib_data (dict): BibTeX entry data for software

    Returns:
        str: Formatted software citation with markdown links
    """
    try:
        authors = get_authors(bib_data.get("author", ""))
        year = bib_data.get("year", "n.d.")
        url = bib_data.get("url", "#")
        title = bib_data.get("title", "Untitled Software")

        return f"{authors} [{title}]({url}), {year}"
    except Exception as e:
        return f"Error formatting software citation: {e}"


def render_book(bib_data: Dict[str, Any]) -> str:
    """
    Render a book citation in PlixLab format.

    Args:
        bib_data (dict): BibTeX entry data for book

    Returns:
        str: Formatted book citation with markdown links
    """
    try:
        authors = get_authors(bib_data.get("author", ""))
        year = bib_data.get("year", "n.d.")
        url = bib_data.get("url", "#")
        publisher = bib_data.get("publisher", "Unknown Publisher")
        title = bib_data.get("title", "Untitled Book")

        return f"{authors} [{title}]({url}), {publisher}, {year}"
    except Exception as e:
        return f"Error formatting book citation: {e}"


def render_article(bib_data: Dict[str, Any]) -> str:
    """
    Render a journal article citation in PlixLab format.

    Args:
        bib_data (dict): BibTeX entry data for article

    Returns:
        str: Formatted article citation with markdown links
    """
    try:
        authors = get_authors(bib_data.get("author", ""))
        journal = bib_data.get("journal", "Unknown Journal")
        year = bib_data.get("year", "n.d.")
        pages = bib_data.get("pages", "n.p.")
        volume = bib_data.get("volume", "n.v.")
        url = bib_data.get("url", "#")

        return f"{authors} [{journal}]({url}) {volume}, {pages} ({year})"
    except Exception as e:
        return f"Error formatting article citation: {e}"


def format(entry_key: str, bibfile: str) -> str:
    """
    Format a bibliographic entry from a BibTeX file.

    Retrieves and formats a specific bibliographic entry based on its key.
    Supports multiple entry types including articles, books, and software.

    Args:
        entry_key (str): The BibTeX key for the desired entry
        bibfile (str): Path to BibTeX file. Defaults to biblio.bib
       
    Returns:
        str: Formatted citation string with markdown formatting

    Examples:
        >>> format("smith2023")
        "J. Smith et al. [Nature](https://example.com) 123, 45-67 (2023)"
    """
    # Default to user-wide bibliography file
    if not bibfile:
        bibfile = os.path.expanduser("~/biblio.bib")

    if not os.path.exists(bibfile):
        return f"Error: Bibliography file not found at {bibfile}"

    try:
        with open(bibfile, encoding="utf-8") as f:
            parser = BibTexParser()
            library = parser.parse_file(f)

        entries = library.entries

        # Find the entry with the specified key
        bib_data = next((e for e in entries if e.get("ID") == entry_key), None)

        if not bib_data:
            return f"Error: Entry '{entry_key}' not found in bibliography"

        # Format based on entry type
        entry_type = bib_data.get("ENTRYTYPE", "").lower()

        if entry_type == "software":
            return render_software(bib_data)
        elif entry_type == "book":
            return render_book(bib_data)
        elif entry_type == "article":
            return render_article(bib_data)
        else:
            return (
                f"Error: Unsupported entry type '{entry_type}' for entry '{entry_key}'"
            )

    except Exception as e:
        return f"Error processing bibliography: {e}"
