"""
GCMD DIF 10.2 for identifying updates in metadata over time.
Note: Unchanged copy
"""

import copy
import json
import sys
from collections import OrderedDict
from logging import getLogger

from xmltodict import unparse

log = getLogger(__name__)


def convert_dif(metadata_record: dict) -> str:
    """Generate GCMD DIF 10.2 formatted XML string.

    Note:
        Converter is only valid for the metadata schema for EnviDat.

    Args:
        metadata_record (dict): Individual EnviDat metadata entry record dictionary.

    Returns:
        str: XML formatted string compatible with GCMD DIF 10.2 standard

    """
    try:
        converted_dict = dif_convert_dataset(
            metadata_record
        )  # Convert package to OrderedDict
        return unparse(converted_dict, pretty=True)  # Convert OrderedDict to XML
    except ValueError as e:
        log.error(e)
        log.error("Cannot convert package to GCMD DIF 10.2 format.")
        raise ValueError("Failed to convert package to GCMD DIF 10.2 format.")


def dif_convert_dataset(dataset_dict: dict):
    """Create the DIF string from API dictionary."""
    # some values only as custom fields
    extras_dict = extras_as_dict(dataset_dict.get("extras", {}))
    dif_extras = ["science_keywords", "purpose"]

    dif_metadata_dict = OrderedDict()

    # Header
    dif_metadata_dict["@xmlns"] = "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/"
    dif_metadata_dict["@xmlns:dif"] = "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/"
    dif_metadata_dict["@xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    namespace = "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/"
    schema = "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/dif_v10.2.xsd"
    dif_metadata_dict["@xsi:schemaLocation"] = f"{namespace} {schema}"

    # Entry_ID
    dif_metadata_dict["Entry_ID"] = OrderedDict()
    dif_metadata_dict["Entry_ID"]["Short_Name"] = dataset_dict.get("name", "")
    dif_metadata_dict["Entry_ID"]["Version"] = dataset_dict.get("version", "1.0")

    # Version_Description

    # Entry_Title
    dif_metadata_dict["Entry_Title"] = dataset_dict.get("title", "")

    # Dataset_Citation
    dif_metadata_dict["Dataset_Citation"] = OrderedDict()

    # "Dataset_Creator" organization
    author_names = []
    try:
        for author in json.loads(dataset_dict.get("author", "[]")):
            author_name = ""
            if author.get("given_name"):
                author_name += author["given_name"].strip() + " "
            author_names += [author_name + author["name"].strip()]
    except ValueError:
        pass

    if author_names:
        dif_metadata_dict["Dataset_Citation"]["Dataset_Creator"] = ", ".join(
            author_names
        )

    # "Dataset_Editor" maintainer
    try:
        maintainer = json.loads(dataset_dict.get("maintainer", "{}"))
        maintainer_name = ""
        if maintainer.get("given_name"):
            maintainer_name += maintainer["given_name"].strip() + " "
        maintainer_name += maintainer["name"]
        dif_metadata_dict["Dataset_Citation"]["Dataset_Editor"] = (
            maintainer_name.strip()
        )
    except ValueError:
        pass

    # "Dataset_Title"
    dif_metadata_dict["Dataset_Citation"]["Dataset_Title"] = dataset_dict.get(
        "title", ""
    )

    # "Dataset_Series_Name"
    # "Dataset_Release_Date"
    publication_year = json.loads(dataset_dict.get("publication", "{}")).get(
        "publication_year", ""
    )
    dif_metadata_dict["Dataset_Citation"]["Dataset_Release_Date"] = publication_year

    # "Dataset_Release_Place"
    dif_metadata_dict["Dataset_Citation"]["Dataset_Release_Place"] = (
        "Birmensdorf, Switzerland"
    )

    # "Dataset_Publisher"
    dif_metadata_dict["Dataset_Citation"]["Dataset_Publisher"] = (
        json.loads(dataset_dict.get("publication", "{}")).get("publisher", "").strip()
    )

    # "Version"
    dif_metadata_dict["Dataset_Citation"]["Version"] = dataset_dict.get("version", "")

    # "Issue_Identification"
    # "Data_Presentation_Form"
    dif_metadata_dict["Dataset_Citation"]["Data_Presentation_Form"] = ",".join(
        get_resource_formats(dataset_dict)
    )

    # "Other_Citation_Details"
    # "Persistent_Identifier"
    doi = dataset_dict.get("doi", "")
    if doi:
        identifier = OrderedDict()
        identifier["Type"] = "DOI"
        identifier["Identifier"] = "doi:" + doi.strip()
        dif_metadata_dict["Dataset_Citation"]["Persistent_Identifier"] = identifier

    # "Online_Resource"
    package_name = dataset_dict.get("name", "")
    package_url = f"https://www.envidat.ch/dataset/{package_name}"
    dif_metadata_dict["Dataset_Citation"]["Online_Resource"] = package_url

    # "Personnel"
    maintainer = json.loads(dataset_dict.get("maintainer", "{}"))
    dif_metadata_dict["Personnel"] = OrderedDict()
    dif_metadata_dict["Personnel"]["Role"] = "TECHNICAL CONTACT"
    dif_metadata_dict["Personnel"]["Contact_Person"] = OrderedDict()
    dif_metadata_dict["Personnel"]["Contact_Person"]["First_Name"] = maintainer.get(
        "given_name", maintainer.get("name", "").strip().split(" ")[0]
    ).strip()
    dif_metadata_dict["Personnel"]["Contact_Person"]["Last_Name"] = (
        maintainer.get("name", "").strip().split(" ")[-1]
    )
    dif_metadata_dict["Personnel"]["Contact_Person"]["Email"] = maintainer.get(
        "email", ""
    ).strip()

    # Science_Keywords (M)*
    science_keywords = get_science_keywords(dataset_dict, extras_dict)
    dif_metadata_dict["Science_Keywords"] = OrderedDict()
    dif_metadata_dict["Science_Keywords"]["Category"] = science_keywords[0]
    dif_metadata_dict["Science_Keywords"]["Topic"] = science_keywords[1]
    dif_metadata_dict["Science_Keywords"]["Term"] = science_keywords[2]
    if len(science_keywords) > 3:
        dif_metadata_dict["Science_Keywords"]["Variable_Level_1"] = science_keywords[3]
    if len(science_keywords) > 4:
        dif_metadata_dict["Science_Keywords"]["Variable_Level_2"] = science_keywords[4]

    # "ISOTopicCategoryType"
    # select from https://gcmd.nasa.gov/add/difguide/iso_topic_category.html
    dif_metadata_dict["ISO_Topic_Category"] = "environment"

    # Ancillary_Keyword
    dif_metadata_dict["Ancillary_Keyword"] = get_keywords(dataset_dict)

    # "Platform"
    dif_metadata_dict["Platform"] = OrderedDict()
    dif_metadata_dict["Platform"]["Type"] = "Not provided"
    dif_metadata_dict["Platform"]["Short_Name"] = "Not provided"
    dif_metadata_dict["Platform"]["Instrument"] = {"Short_Name": "Not provided"}

    # Temporal_Coverage
    dif_metadata_dict["Temporal_Coverage"] = OrderedDict()

    # default set to publication year
    dif_metadata_dict["Temporal_Coverage"]["Single_DateTime"] = (
        publication_year + "-01-01"
    )

    # "Dataset_Progress" draft or private -> IN WORK, doi -> COMPLETE (otherwise empty)
    if dataset_dict.get("private", False) or dataset_dict.get("num_resources", 0) == 0:
        dif_metadata_dict["Dataset_Progress"] = "IN WORK"
    elif dataset_dict.get("doi", ""):
        dif_metadata_dict["Dataset_Progress"] = "COMPLETE"

    # Spatial_Coverage
    dif_metadata_dict["Spatial_Coverage"] = OrderedDict()
    # "Spatial_Coverage_Type"
    # "Granule_Spatial_Representation"
    dif_metadata_dict["Spatial_Coverage"]["Granule_Spatial_Representation"] = (
        "CARTESIAN"
    )

    # <xs:element name="Zone_Identifier" type="xs:string" minOccurs="0"/>

    # "Geometry" [1]
    try:
        spatial = json.loads(dataset_dict.get("spatial", "{}"))
    except ValueError:
        spatial = {}
    if spatial:
        dif_metadata_dict["Spatial_Coverage"]["Geometry"] = OrderedDict()
        dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Coordinate_System"] = (
            "CARTESIAN"
        )

        coordinates = spatial.get("coordinates", [])
        if coordinates:
            bounding_rectangle = get_bounding_rectangle_dict(spatial)
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Bounding_Rectangle"] = (
                bounding_rectangle
            )

        # <xs:element name="Point" type="Point"/>
        if spatial.get("type") == "Point":
            bound_box_coordinates = get_bounding_rectangle(
                spatial.get("coordinates", [])
            )
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Point"] = OrderedDict()
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Point"][
                "Point_Longitude"
            ] = bound_box_coordinates[0]
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Point"][
                "Point_Latitude"
            ] = bound_box_coordinates[3]
            # latitude = bound_box_coordinates[3]
        elif spatial.get("type") == "MultiPoint":
            points = []
            for coordinate_pair in spatial.get("coordinates", []):
                point = OrderedDict()
                point["Point_Longitude"] = str(coordinate_pair[0])
                point["Point_Latitude"] = str(coordinate_pair[1])
                points += [point]
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Point"] = points
        elif spatial.get("type") == "Polygon":
            # <xs:element name="Polygon" type="GPolygon"/>
            points = []
            for coordinate_pair in spatial.get("coordinates", [])[0]:
                point = OrderedDict()
                point["Point_Longitude"] = str(coordinate_pair[0])
                point["Point_Latitude"] = str(coordinate_pair[1])
                points += [point]
            if len(points) > 1:
                points.pop()

            if is_counter_clockwise(points):
                log.debug(
                    dataset_dict.get("name", "") + " ** Counterclockwise REVERSING!! **"
                )
                points.reverse()
            else:
                log.debug(dataset_dict.get("name", "") + " Clockwise OK")

            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Polygon"] = OrderedDict()
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Polygon"]["Boundary"] = {
                "Point": points
            }
            dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Polygon"][
                "Center_Point"
            ] = copy.deepcopy(
                dif_metadata_dict["Spatial_Coverage"]["Geometry"]["Bounding_Rectangle"][
                    "Center_Point"
                ]
            )

    # <xs:element name="Orbit_Parameters" type="OrbitParameters" minOccurs="0"/>
    # <xs:element name="Vertical_Spatial_Info" type="VerticalSpatialInfo" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # <xs:element name="Spatial_Info" type="SpatialInfo" minOccurs="0"/>

    # <xs:element name="Location" type="LocationType" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # Cannot know type, could be set to CONTINENT type and then Europe (?)
    # <xs:element name="Data_Resolution" type="DataResolutionType" minOccurs="0"
    #   maxOccurs="unbounded"/>

    # Project
    dif_metadata_dict["Project"] = {"Short_Name": "Not provided"}

    # <xs:element name="Quality" type="QualityType" minOccurs="0"/>
    dif_metadata_dict["Access_Constraints"] = "Public access to the data"

    dataset_restrictions = get_resource_restrictions(dataset_dict)
    if "registered" in dataset_restrictions:
        dif_metadata_dict["Access_Constraints"] = (
            "Registration is required to access the data"
        )
    elif (
        ("any_organization" in dataset_restrictions)
        or ("same_organization" in dataset_restrictions)
        or ("only_allowed_users" in dataset_restrictions)
    ):
        dif_metadata_dict["Access_Constraints"] = "Access to the data upon request"

    # "Use_Constraints"
    license = dataset_dict.get("license_title", None)
    if not license:
        license = "Open Data Commons Open Database License (ODbL)"
    license_url = dataset_dict.get(
        "license_url", "http://www.opendefinition.org/licenses/odc-odbl"
    )
    dif_metadata_dict["Use_Constraints"] = (
        'Usage constraints defined by the license "'
        + license.strip()
        + '", see '
        + license_url
    )

    # Dataset_Language
    dif_metadata_dict["Dataset_Language"] = get_dif_language_code(
        dataset_dict.get("language", "en")
    )

    # "Originating_Center"
    dif_metadata_dict["Originating_Center"] = dataset_dict.get("organization", {}).get(
        "title", ""
    )

    # Organization
    dif_metadata_dict["Organization"] = OrderedDict()

    # "Organization_Type" * DISTRIBUTOR/ARCHIVER/ORIGINATOR/PROCESSOR
    dif_metadata_dict["Organization"]["Organization_Type"] = "DISTRIBUTOR"

    # "Organization_Name" "Short_Name" "Long_Name"
    dif_metadata_dict["Organization"]["Organization_Name"] = OrderedDict()
    dif_metadata_dict["Organization"]["Organization_Name"]["Short_Name"] = "WSL"
    dif_metadata_dict["Organization"]["Organization_Name"]["Long_Name"] = (
        "Swiss Federal Institute for Forest, Snow and Landscape Research WSL"
    )

    # <xs:element name="Hours_Of_Service" type="xs:string" minOccurs="0"/>
    # <xs:element name="Instructions" type="xs:string" minOccurs="0"/>
    #  "Organization_URL"
    dif_metadata_dict["Organization"]["Organization_URL"] = "https://www.wsl.ch"

    # <xs:element name="Dataset_ID" type="xs:string" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # <xs:element name="Personnel" type="OrgPersonnelType" maxOccurs="unbounded"/>
    dif_metadata_dict["Organization"]["Personnel"] = OrderedDict()
    dif_metadata_dict["Organization"]["Personnel"]["Role"] = "DATA CENTER CONTACT"
    dif_metadata_dict["Organization"]["Personnel"]["Contact_Group"] = OrderedDict()
    dif_metadata_dict["Organization"]["Personnel"]["Contact_Group"]["Name"] = "EnviDat"
    dif_metadata_dict["Organization"]["Personnel"]["Contact_Group"]["Email"] = (
        "envidat@wsl.ch"
    )

    # <xs:element name="Distribution" type="DistributionType" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # <xs:element name="Multimedia_Sample" type="MultimediaSampleType"
    #   minOccurs="0" maxOccurs="unbounded"/>

    # <xs:element name="Reference" type="ReferenceType" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # Find paper citation in the description and parse it to this element

    thumbnail_url = "https://www.envidat.ch/envidat_thumbnail.png"
    dif_metadata_dict["Multimedia_Sample"] = OrderedDict()
    dif_metadata_dict["Multimedia_Sample"]["URL"] = thumbnail_url

    # Summary
    dif_metadata_dict["Summary"] = OrderedDict()
    # Abstract
    dif_metadata_dict["Summary"]["Abstract"] = (
        dataset_dict.get("notes", "").replace("\n", " ").replace("\r", " ").strip()
    )
    # "Purpose"
    # purpose = get_ignore_case(extras_dict, 'purpose')
    # if purpose:
    # dif_metadata_dict['Summary']['Purpose'] = get_or_missing(
    #     extras_dict, 'purpose', ignore_case=True
    # )
    # Related_URL
    dif_metadata_dict["Related_URL"] = {"URL": package_url}

    # <xs:element name="Metadata_Association" type="MetadataAssociationType"
    #   minOccurs="0" maxOccurs="unbounded"/>
    # <xs:element name="IDN_Node" type="IDNNodeType" minOccurs="0"
    #   maxOccurs="unbounded"/>
    # <xs:element name="Originating_Metadata_Node" type="OriginatingMetadataNodeType"
    #   minOccurs="0"/>

    # Metadata_Name
    dif_metadata_dict["Metadata_Name"] = "gcmd_dif"

    # Metadata_Version
    dif_metadata_dict["Metadata_Version"] = "VERSION 10.2"

    # <xs:element name="DIF_Revision_History" type="DIFRevisionHistoryType"
    #   minOccurs="0"/>

    # Metadata_Dates (M)
    dif_metadata_dict["Metadata_Dates"] = OrderedDict()

    metadata_created = dataset_dict.get("metadata_created")
    metadata_modified = dataset_dict.get("metadata_modified")
    dif_metadata_dict["Metadata_Dates"]["Metadata_Creation"] = metadata_created
    dif_metadata_dict["Metadata_Dates"]["Metadata_Last_Revision"] = metadata_modified
    dif_metadata_dict["Metadata_Dates"]["Data_Creation"] = metadata_created
    dif_metadata_dict["Metadata_Dates"]["Data_Last_Revision"] = metadata_modified

    # "Private"
    if dataset_dict.get("private", False):
        dif_metadata_dict["Private"] = "True"
    else:
        dif_metadata_dict["Private"] = "False"

    # "Additional_Attributes"
    # Maybe the authors should go here

    # <xs:element name="Product_Level_Id" type="ProcessingLevelIdType" minOccurs="0"/>
    # <xs:element name="Collection_Data_Type" type="CollectionDataTypeEnum"
    #   minOccurs="0" maxOccurs="unbounded"/>
    # <xs:element name="Product_Flag" type="ProductFlagEnum" minOccurs="0"/>

    # "Extended_Metadata"
    extended_metadata = []
    for key in extras_dict:
        if key.lower() not in dif_extras:
            value = extras_dict[key]
            metadata = OrderedDict()
            metadata["Name"] = key.strip()
            metadata["Type"] = "String"
            metadata["Value"] = value.strip()
            extended_metadata += [metadata]
    if len(extended_metadata) > 0:
        dif_metadata_dict["Extended_Metadata"] = {"Metadata": extended_metadata}

    # Root element
    gcmd_dif_dict = OrderedDict()
    gcmd_dif_dict["DIF"] = dif_metadata_dict

    return gcmd_dif_dict


def get_keywords(data_dict):
    """Extract keywords from tags."""
    keywords = []
    for tag in data_dict.get("tags", []):
        name = tag.get("display_name", "").upper()
        keywords += [name]
    return keywords


def get_science_keywords(data_dict, extras_dict):
    """Guess keywords from organization."""
    default_keywords = [
        "EARTH SCIENCE",
        "CLIMATE INDICATORS",
        "LAND SURFACE/AGRICULTURE INDICATORS",
    ]

    # check if defined in extras, comma-separated
    custom_keywords = (
        get_ignore_case(extras_dict, "science_keywords").upper().split(",")
    )
    if len(custom_keywords) >= 3:
        return custom_keywords

    # map to organization
    dataset_organization = data_dict.get("organization", {}).get("name", "")

    # possible topics: AGRICULTURE, ATMOSPHERE, BIOSPHERE, BIOLOGICAL CLASSIFICATION,
    # CLIMATE INDICATORS, CRYOSPHERE, HUMAN DIMENSIONS, LAND SURFACE, OCEANS,
    # PALEOCLIMATE, SOLID EARTH, SPECTRAL/ENGINEERING, SUN-EARTH INTERACTIONS,
    # TERRESTRIAL HYDROSPHERE
    organizations_keywords_dict = {
        "biodiversity-and-conservation-biology": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOLOGICAL DYNAMICS",
            "COMMUNITY DYNAMICS",
            "BIODIVERSITY FUNCTIONS",
        ],
        "cces": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "clench": [
            "EARTH SCIENCE",
            "CLIMATE INDICATORS",
            "ATMOSPHERIC/OCEAN INDICATORS",
        ],
        "community-ecology": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOLOGICAL DYNAMICS",
            "COMMUNITY DYNAMICS",
        ],
        "conservation-biology": [
            "EARTH SCIENCE",
            "AGRICULTURE",
            "FOREST SCIENCE",
            "FOREST CONSERVATION",
        ],
        "cryos": ["EARTH SCIENCE", "CRYOSPHERE", "SNOW/ICE"],
        "d-baug": ["EARTH SCIENCE", "SPECTRAL/ENGINEERING", "PLATFORM CHARACTERISTICS"],
        "usys": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "dynamic-macroecology": ["EARTH SCIENCE", "BIOSPHERE", "ECOLOGICAL DYNAMICS"],
        "ecosystems-dynamics": ["EARTH SCIENCE", "BIOSPHERE", "ECOSYSTEMS"],
        "epfl": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "ethz": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "feh": ["EARTH SCIENCE", "AGRICULTURE", "FOOD SCIENCE"],
        "forema": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "TERRESTRIAL ECOSYSTEMS",
            "FOREST",
        ],
        "forest-dynamics": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "TERRESTRIAL ECOSYSTEMS",
            "FORESTS",
        ],
        "forest-soils-and-biogeochemistry": ["EARTH SCIENCE", "LAND SURFACE", "SOILS"],
        "gebirgshydrologie": [
            "EARTH SCIENCE",
            "TERRESTRIAL HYDROSPHERE",
            "SURFACE WATER",
        ],
        "gis": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "ANTHROPOGENIC/HUMAN INFLUENCED ECOSYSTEMS",
        ],
        "hazri": ["EARTH SCIENCE", "SOLID EARTH", "NATURAL HAZARDS"],
        "ibp": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "landscape-dynamics": ["EARTH SCIENCE", "LAND SURFACE", "LANDSCAPE"],
        "lwf": ["EARTH SCIENCE", "CLIMATE INDICATORS", "ATMOSPHERIC/OCEAN INDICATORS"],
        "mountain-ecosystems": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "TERRESTRIAL ECOSYSTEMS",
        ],
        "nfi": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "TERRESTRIAL ECOSYSTEMS",
            "FORESTS",
        ],
        "plant-animal-interactions": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOLOGICAL DYNAMICS",
            "SPECIES/POPULATION INTERACTIONS",
        ],
        "remote-sensing": [
            "EARTH SCIENCE",
            "CLIMATE INDICATORS",
            "ATMOSPHERIC/OCEAN INDICATORS",
        ],
        "resource-analysis": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "FOREST SCIENCE",
            "FOREST CONSERVATION",
        ],
        "slf": ["EARTH SCIENCE", "CRYOSPHERE", "SNOW/ICE"],
        "stand-dynamics-and-silviculture": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "SILVICULTURE",
        ],
        "swissforestlab-swissfl": [
            "EARTH SCIENCE",
            "BIOSPHERE",
            "ECOSYSTEMS",
            "TERRESTRIAL ECOSYSTEMS",
            "FORESTS",
        ],
        "vaw": ["EARTH SCIENCE", "TERRESTRIAL HYDROSPHERE", "GLACIERS/ICE SHEETS"],
        "wsl": [
            "EARTH SCIENCE",
            "CLIMATE INDICATORS",
            "LAND SURFACE/AGRICULTURE INDICATORS",
        ],
    }

    science_keywords = organizations_keywords_dict.get(
        dataset_organization, default_keywords
    )

    return science_keywords


def get_ignore_case(data_dict, tag, ignore_blanks=True):
    """Get value, case agnostic."""
    tag_lower = tag.lower()
    if ignore_blanks:
        tag_lower = tag_lower.replace(" ", "")
    tag_key = ""
    for key in data_dict.keys():
        key_lower = key.lower()
        if ignore_blanks:
            key_lower = key_lower.replace(" ", "")
        if key_lower == tag_lower:
            tag_key = key
            break
    return data_dict.get(tag_key, "")


def extras_as_dict(extras):
    """Extract API 'extras' field as a simple dictionary."""
    extras_dict = {}
    for extra in extras:
        extras_dict[extra.get("key")] = extra.get("value")
    return extras_dict


def get_resource_formats(dataset_dict):
    """Get resource formats."""
    resource_formats = []
    for resource in dataset_dict.get("resources", []):
        resource_format = resource.get(
            "format", resource.get("mimetype", resource.get("mimetype_inner", ""))
        )
        if resource_format:
            resource_format = resource_format.lower()
            if resource_format not in resource_formats:
                resource_formats += [resource_format]
    return resource_formats


def get_resource_restrictions(dataset_dict):
    """Get resource restrictions."""
    resource_restrictions = []
    for resource in dataset_dict.get("resources", []):
        try:
            restricted = json.loads(resource.get("restricted"))
        except ValueError:
            restricted = {}
        resource_restriction = restricted.get("level", "")
        if resource_restriction:
            resource_restriction = resource_restriction.lower()
            if resource_restriction not in resource_restrictions:
                resource_restrictions += [resource_restriction]
    return resource_restrictions


def get_dif_language_code(code):
    """Translate codes to language full word.

    https://gcmd.nasa.gov/DocumentBuilder/defaultDif10/guide/data_set_language.html

    Options: English; Afrikaans; Arabic; Bosnia; Bulgarian; Chinese; Croation; Czech;
    Danish; Dutch; Estonian; Finnish; French; German; Hebrew; Hungarian; Indonesian;
    Italian; Japanese; Korean; Latvian; Lithuanian; Norwegian; Polish; Portuguese;
    Romanian; Russian; Slovak; Spanish; Ukrainian; Vietnamese
    """
    lang_code = code.lower()[:2]
    lookup_dict = {
        "en": "English",
        "de": "German",
        "it": "Italian",
        "fr": "French",
    }  # , 'ro':'roh'}
    return lookup_dict.get(lang_code, "English").title()


def get_bounding_rectangle(coordinates: list) -> list:
    """Geometry bounding rectangle as coordinate list."""
    flatten_coordinates = coordinates
    while type(flatten_coordinates[0]) is list:
        flatten_coordinates = [
            item for sublist in flatten_coordinates for item in sublist
        ]
    longitude_coords = flatten_coordinates[0:][::2]
    latitude_coords = flatten_coordinates[1:][::2]
    return [
        min(longitude_coords),
        max(longitude_coords),
        min(latitude_coords),
        max(latitude_coords),
    ]


def get_bounding_rectangle_dict(spatial_dict: dict) -> dict:
    """Geometry bounding rectangle as value dictionary."""
    bound_box_coordinates = get_bounding_rectangle(spatial_dict.get("coordinates", []))

    bounding_rectangle = OrderedDict()
    bounding_rectangle["Center_Point"] = OrderedDict()
    bounding_rectangle["Center_Point"]["Point_Longitude"] = str(
        (bound_box_coordinates[1] + bound_box_coordinates[0]) / 2.0
    )
    bounding_rectangle["Center_Point"]["Point_Latitude"] = str(
        (bound_box_coordinates[3] + bound_box_coordinates[2]) / 2.0
    )
    bounding_rectangle["Southernmost_Latitude"] = str(
        max(bound_box_coordinates[2], -90)
    )
    bounding_rectangle["Northernmost_Latitude"] = str(min(bound_box_coordinates[3], 90))
    bounding_rectangle["Westernmost_Longitude"] = str(max(bound_box_coordinates[0], 0))
    bounding_rectangle["Easternmost_Longitude"] = str(
        min(bound_box_coordinates[1], 180)
    )

    return bounding_rectangle


def is_counter_clockwise(points):
    """Check if polygon is counterclockwise / valid."""
    if len(points) < 3:
        return False

    try:
        akku = 0

        for i in range(len(points)):
            p1 = points[i]
            p2 = points[0]

            if i + 1 < len(points):
                p2 = points[i + 1]

            akku += (float(p2["Point_Longitude"]) - float(p1["Point_Longitude"])) * (
                float(p2["Point_Latitude"]) + float(p1["Point_Latitude"])
            )

        if akku >= 0:
            return False
        else:
            return True
    except Exception as e:
        log.error(
            "Unexpected error converting to float (is_counter_clockwise):",
            sys.exc_info()[0],
        )
        log.error(e)

    return False
