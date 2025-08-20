import re
from typing import Dict, List


def get_top_level_sections(text: str) -> List[Dict]:
    """Uses regex to break the text down into sections based on the text CHAPTER and ANNEX, includes the text before the first CHAPTER as the first entry in the List.

    Args:
        text (str): The text of an EU Law document

    Returns:
        List[Dict]: List of Dictionaries, containg the following keys:
            - text: The text of the section
    """
    return [
        {"text": s.strip()}
        for s in re.split(
            r"(?=(^|[\s?.])(\b(CHAPTER|ANNEX)\s?([IVX]{1,3}|\d+)\b))", text
        )
        if s and len(s.strip()) > 5 and s != "CHAPTER" and s != "ANNEX"
    ]


def sectionise_eu_law_document(
    top_level_sections: List[Dict], verbose: bool = False
) -> List[str]:
    """Takes an EU Law document and breaks it into sections were each section is an article within a chapter, or an annex.
    The preamble before the first chapter is just placed in one section.

    ToDo: section out the first section (before the first chapter)

    Args:
        top_level_sections (List[str]): A list of strings broken down by the regex in
        verbose (bool, optional): Display output progress. Defaults to False.

    Returns:
        List[Dict]: A list of dictionary objects, each object contains the following keys:
            - "section_number": Chapter and Article Title, or Annex Number or 'INTRODUCTION' if it is the text before the first Chapter header
            - "text": The text

    """
    section_number: str = ""
    sections: List[Dict] = []
    for section in top_level_sections:
        # Handle the case with '.' matches on the first char and remove the full stop
        if section["text"].startswith("."):
            section["text"] = section["text"][1:]
        # Using the regex
        text = section["text"].strip()
        if text.startswith("CHAPTER"):
            # No newline, so no content skip
            first_newline = text.find("\n") + 1
            if first_newline == 0:
                continue
            else:
                # Split on lines
                lines = text.split("\n")
                section["chapter_number"] = lines[0]  # first line is chapter numbet
                title = []
                contents = ""
                for line in lines[1:]:  # start from the second line
                    if line.isupper():  # check if the line only has capital letters then its still title
                        title.append(line)
                    else:
                        contents += line + "\n"
                section["chapter_title"] = " ".join(
                    title
                )  # join the title lines into a single string
                if verbose:
                    print(section["chapter_number"], ",", section["chapter_title"])
                # Now we need to split on Article..
                articles = [
                    s.strip()
                    for s in re.split(r"(Article \d+\n)", contents)
                    if s and len(s.strip()) > 7
                ]
                index = 0  # Get back pairs of articles, one with name then the text, get the number and append to chapter name and then the text from the second part
                while index < len(articles):
                    a_section = {
                        "section_number": f"{section['chapter_number']}: {articles[index]}",
                        "text": articles[index + 1],
                    }
                    if verbose:
                        print(a_section["section_number"], ",", a_section["text"][:50])
                    sections.append(a_section)
                    index = index + 2
        elif text.startswith("ANNEX"):
            first_newline = text.find("\n")
            if first_newline == -1:  # Firt occurence will be just the name
                section_number = text
                continue
            a_section = {  # next occurent will be the content, remove the ANNEX II type content from the start
                "section_number": section_number,
                "text": text[len(section_number) + 1 :],
            }
            if verbose:
                print(a_section["section_number"], ",", a_section["text"][:50])
            sections.append(a_section)
        else:  # Only occurs before the first section
            a_section = {"section_number": "INTRODUCTION", "text": text}
            if verbose:
                print(a_section["section_number"], ",", a_section["text"][:50])
            sections.append(a_section)

    return sections
