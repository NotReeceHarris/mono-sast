"""Utilities for converting between data serialisation formats."""

import xmltodict
import json


def xml_to_json(xmlContent):
    """Convert an XML string to a JSON string.

    Parses *xmlContent* with xmltodict and serialises the resulting ordered
    dict to JSON.  Used by tools whose only output format is XML (e.g. SpotBugs).
    """
    parsedXml = xmltodict.parse(xmlContent)

    jsonContent = json.dumps(parsedXml)

    return jsonContent
