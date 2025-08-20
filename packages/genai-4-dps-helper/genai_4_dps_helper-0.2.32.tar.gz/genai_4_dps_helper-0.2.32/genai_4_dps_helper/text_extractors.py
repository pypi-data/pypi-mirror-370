import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

from pypdf import PdfReader

from genai_4_dps_helper.base_obj import BaseObj


class TextExtractors(BaseObj):
    """
    A class used to convert documents (.docx / .pdf) to plain text.

    Attributes:
    ----------
    None

    Methods:
    -------
    word2text(filename: str, data_bytes: bytes) -> str
        Converts a Word document to plain text.
    pdf2text(filename: str, data_bytes: bytes) -> str:
        Converts a PDF document to plain text.

    __iterate_through_xml(xml_obj, ns, text, parent_tag=None)
        Recursively iterates through the XML object to extract text.
    """

    def __init__(self) -> None:
        """
        Initializes the WordToText object.

        Parameters:
        ----------
        None
        """
        super(TextExtractors, self).__init__()

    def pdf2text(self, filename: str, data_bytes: bytes) -> str:
        """
        Converts a PDF document to plain text.

        Parameters:
        ----------
        filename : str
            The name of the file (used to determine the file type).
        data_bytes : bytes
            The contents of the file as bytes.

        Returns:
        -------
        str
            The text extracted from the Word document.
        """
        # Check if the file is a PDF  document (.pdf)
        if not filename.lower().endswith(".pdf"):  # PDF pdf extraction
            raise ValueError("filename must be a PDF file, ending in .pdf")

        doc = PdfReader(stream=data_bytes)
        # Extract text from the PDF
        text = ""
        for page in doc.pages:
            text += page.extract_text()
        # Print the extracted text
        return text

    def word2text(self, filename: str, data_bytes: bytes) -> str:
        """
        Converts a Word document to plain text.

        Parameters:
        ----------
        filename : str
            The name of the file (used to determine the file type).
        data_bytes : bytes
            The contents of the file as bytes.

        Returns:
        -------
        str
            The text extracted from the Word document.
        """
        # Check if the file is a Word document (.docx)
        if not filename.lower().endswith(".docx"):  # Word docx extraction
            raise ValueError("filename must be a word file, ending in .docx")

            # Initialize the zip object
        if hasattr(data_bytes, "read"):
            zip_file = zipfile.ZipFile(data_bytes)
        elif isinstance(data_bytes, bytes):
            zip_file = zipfile.ZipFile(BytesIO(data_bytes))
        else:
            raise TypeError("data_bytes must be a bytes object or a file-like object")

        text = []
        # Define the namespace for the XML parsing
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        # Extract text from header sections
        for file_name in zip_file.namelist():
            if file_name.startswith("word/header"):
                # Read the header XML
                header_xml = zip_file.read(file_name)
                # Parse the XML
                root = ET.fromstring(header_xml)
                # Recursively iterate through the XML to extract text
                self.__iterate_through_xml(root, ns, text)

            # Extract text from document sections
            for file_name in zip_file.namelist():
                if file_name.startswith("word/document"):
                    # Read the document XML
                    document_xml = zip_file.read(file_name)
                    # Parse the XML
                    root = ET.fromstring(document_xml)
                    # Recursively iterate through the XML to extract text
                    self.__iterate_through_xml(root, ns, text)

            # Extract text from footer sections
            for file_name in zip_file.namelist():
                if file_name.startswith("word/footer"):
                    # Read the footer XML
                    footer_xml = zip_file.read(file_name)
                    # Parse the XML
                    root = ET.fromstring(footer_xml)
                    # Recursively iterate through the XML to extract text
                    self.__iterate_through_xml(root, ns, text)

            # Join the extracted text into a single string
            return "".join(text)

    def __iterate_through_xml(self, xml_obj, ns, text, parent_tag=None):
        """
        Recursively iterates through the XML object to extract text.

        Parameters:
        ----------
        xml_obj : object
            The current XML object.
        ns : dict
            The namespace for the XML parsing.
        text : list
            The list of extracted text.
        parent_tag : str, optional
            The parent tag of the current XML object (default is None).
        """
        in_bullets = False
        # Iterate through the child elements of the current XML object
        for child in xml_obj:
            # Check if the child is a paragraph
            if child.tag.endswith("}p"):
                # Recursively iterate through the paragraph
                self.__iterate_through_xml(child, ns, text, child.tag)
            # Check if the child is a text element
            elif child.tag.endswith("}t"):
                # Extract the text and replace non-breaking spaces with regular spaces
                text.append(child.text.replace("\xa0", " "))
            # Check if the child is a paragraph style element
            elif child.tag.endswith("}pStyle"):
                # Check if the paragraph style indicates a list
                for attrib in child.attrib:
                    if attrib.endswith("val") and (
                        child.attrib[attrib] == "ListParagraph"
                        or child.attrib[attrib] == "Liststycke"
                    ):
                        in_bullets = True
            # Check if the child is a number properties element and we are in a list
            elif child.tag.endswith("}numPr") and in_bullets:
                # Recursively iterate through the number properties
                self.__iterate_through_xml(child, ns, text, child.tag)
                # Reset the in_bullets flag
                in_bullets = False
            # Check if the child is a line break element
            elif child.tag.endswith("}br"):
                # Append a newline character to the text
                text.append("\n")
            # Check if the child is an indentation level element and we are in a list
            elif (
                child.tag.endswith("}ilvl")
                and parent_tag
                and parent_tag.endswith("}numPr")
            ):
                # Append indentation and a bullet point to the text
                for attrib in child.attrib:
                    if attrib.endswith("val"):
                        text.append(("    " * int(child.attrib[attrib])) + "* ")
            # If none of the above conditions are met, recursively iterate through the child
            else:
                self.__iterate_through_xml(child, ns, text)
        # If we are at the end of a paragraph, append a newline character to the text
        if parent_tag and parent_tag.endswith("}p"):
            text.append("\n\n")
