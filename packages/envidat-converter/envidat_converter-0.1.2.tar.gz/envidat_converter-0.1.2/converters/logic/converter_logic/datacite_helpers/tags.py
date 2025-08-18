"""
Class to define all the tags and strings.
"""


class Tags:
    xml_lang_tag = "@xml:lang"
    english_lang_tag = "en"
    schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
    namespace = "http://datacite.org/schema/kernel-4"
    schema = "http://schema.datacite.org/meta/kernel-4/metadata.xsd"
    doi_tag = "DOI"
    dataset_lowercase = "dataset"
    dataset_uppercase = "Dataset"
    contact_person = "ContactPerson"
    url_uppercase = "URL"
    url_lowercase = "url"
    is_required_by = "IsRequiredBy"
    other = "Other"
    references = "References"
    envidat = "EnviDat"
    default_rights_scheme_uri = "https://spdx.org/licenses/"
    dc_rights_identifier_scheme = "rightsIdentifierScheme"
    default_rights_identifier = "SPDX"
    default_publisher_identifier = "https://www.re3data.org/repository/r3d100012587"
    default_publisher_identifier_scheme = "re3data"
    default_publisher_identifier_uri = "https://re3data.org/"
    resources = "resources"
    organizational = "Organizational"
    research_group = "ResearchGroup"
    organization_tag = "organization"
    envidat_metadata_base_url = "https://www.envidat.ch/#/metadata/"
    envidat_dataset_url = "https://www.envidat.ch/dataset/"
    related_datasets_tag = "related_datasets"
    related_publications_tag = "related_publications"
    orcid_url = "https://orcid.org/"
    orcid_uppercase = "ORCID"
    orcid_lowercase = "orcid"
    mimetype = "mimetype"
    no_info = "No Info"
    abstract = "Abstract"

    resource_tag = "resource"
    xmlns_xsi_tag = "@xmlns:xsi"
    xmlns_tag = "@xmlns"
    xsi_schemaLocation_tag = "@xsi:schemaLocation"
    identifier_tag = "identifier"
    text_tag = "#text"
    identifierType_tag = "@identifierType"
    creators_tag = "creators"
    creator_tag = "creator"
    affiliation_identifier_tag = "@affiliationIdentifier"
    affiliation_identifier_scheme_tag = "@affiliationIdentifierScheme"
    family_name_tag = "familyName"
    given_name_tag = "givenName"
    creator_name_tag = "creatorName"
    name_identifier_tag = "nameIdentifier"
    nameIdentifierScheme_tag = "@nameIdentifierScheme"
    schemeURI_tag = "@schemeURI"
    affiliation_tag = "affiliation"
    titles_tag = "titles"
    title_tag = "title"
    publication_tag = "publication"
    publisher_tag = "publisher"
    publisher_identifier_tag = "@publisherIdentifier"
    publisher_identifier_scheme_tag = "@publisherIdentifierScheme"
    publication_year_tag = "publicationYear"
    resource_type_tag = "resourceType"
    resource_type_general_tag = "@resourceTypeGeneral"
    subjects_tag = "subjects"
    subject_tag = "subject"
    contributors_tag = "contributors"
    contributor_tag = "contributor"
    contributor_type_tag = "@contributorType"
    contributor_name_tag = "contributorName"
    name_type_tag = "@nameType"
    dates_tag = "dates"
    date_tag = "date"
    date_type_tag = "@dateType"
    enddate_tag = "enddate"
    language_tag = "language"
    alternate_identifiers_tag = "alternateIdentifiers"
    alternate_identifier_tag = "alternateIdentifier"
    alternate_identifier_type_tag = "@alternateIdentifierType"
    id_tag = "id"
    name_tag = "name"
    related_identifiers_tag = "relatedIdentifiers"
    related_identifier_tag = "relatedIdentifier"
    related_identifier_type_tag = "@relatedIdentifierType"
    url_tag = "url"
    relation_type_tag = "@relationType"
    related_items_tag = "relatedItems"
    related_item_tag = "relatedItem"
    related_item_type_tag = "@relatedItemType"
    related_item_identifier_type_tag = "@relatedItemIdentifierType"
    related_item_identifier_tag = "relatedItemIdentifier"
    formats_tag = "formats"
    format_tag = "format"
    sizes_tag = "sizes"
    size_tag = "size"
    version_tag = "version"
    rights_list_tag = "rightsList"
    rights_tag = "rights"
    rights_uri_tag = "@rightsURI"
    rights_identifier_scheme_tag = "@rightsIdentifierScheme"
    rights_identifier_tag = "@rightsIdentifier"
    descriptions_tag = "descriptions"
    description_tag = "description"
    description_type_tag = "@descriptionType"
    geolocations_tag = "geoLocations"
    geolocation_tag = "geoLocation"
    geolocation_polygon_tag = "geoLocationPolygon"
    polygon_point_tag = "geoLocationPoint"
    point_longitude_tag = "pointLongitude"
    point_latitude_tag = "pointLatitude"
    geolocation_place_tag = "geoLocationPlace"
    funding_references_tag = "fundingReferences"
    funding_reference_tag = "fundingReference"
    funder_name_tag = "funderName"
    award_number_tag = "awardNumber"
    award_uri_tag = "@awardURI"

    geometries = "geometries"
    type_tag = "type"
    coordinates = "coordinates"
    polygon = "polygon"
    point = "point"
    multipoint = "multipoint"
    polygon_point = "polygonPoint"
    geometry_collection = "geometrycollection"

    aff_keys = {
        "WSL": "wsl",
        "Swiss Federal Institute for Forest, Snow and Landscape Research WSL": "wsl",
        "WSL Swiss Federal Research Institute, Birmensdorf, Switzerland": "wsl",
        "SLF": "slf",
        "WSL Institute for Snow and Avalanche Research SLF, Davos Dorf, Switzerland": "slf",
        "WSL Institute for Snow and Avalanche Research SLF": "slf",
        "ETH": "eth",
        "ETHZ": "eth",
        "UZH": "uzh",
        "University of Zurich": "uzh",
        "University of Zürich": "uzh",
        "EPFL": "epfl",
        "EPFL, Lausanne Swiss Federal Institute of Technology, Lausanne and Sion": "epfl",
        "PSI": "psi",
        "PSI, Paul Scherrer Institute, Villigen": "psi",
        "IAP": "iap",
        "TROPOS": "tropos",
        "UNIL": "unil",
    }

    config = {
        "identifier": "doi",
        "creators": "author",
        "creator": {
            "givenName": "given_name",
            "familyName": "name",
            "nameIdentifier": "identifier",
            "affiliation": "affiliation",
        },
        "title": "title",
        "publisher": "publisher",
        "publicationYear": "publication_year",
        "resourceType": "resource_type",
        "resourceTypeGeneral": "resource_type_general",
        "subjects": "tags",
        "subject": "display_name",
        "contributors": "maintainer",
        "contributor": {
            "givenName": "given_name",
            "familyName": "name",
            "nameIdentifier": "identifier",
            "affiliation": "affiliation",
        },
        "dates": "date",
        "date": "date",
        "enddate": "end_date",
        "@dateType": "date_type",
        "language": "language",
        "version": "version",
        "rights": {
            "#text": "license_title",
            "@rightsURI": "license_url",
            "@rightsIdentifier": "license_id",
        },
        "description": "notes",
        "geoLocations": "spatial",
        "geoLocationPlace": "spatial_info",
        "fundingReferences": "funding",
        "fundingReference": {
            "funderName": "institution",
            "awardNumber": "grant_number",
            "@awardURI": "institution_url",
        },
        "affiliation": {
            "wsl": {
                "#text": "Swiss Federal Institute for Forest, Snow and Landscape Research WSL",
                "@affiliationIdentifier": "https://ror.org/04bs5yc70",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "slf": {
                "#text": "WSL Institute for Snow and Avalanche Research SLF",
                "@affiliationIdentifier": "https://ror.org/04bs5yc70",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "eth": {
                "#text": "ETH Zurich",
                "@affiliationIdentifier": "https://ror.org/05a28rw58",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "uzh": {
                "#text": "University of Zurich",
                "@affiliationIdentifier": "https://ror.org/02crff812",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "epfl": {
                "#text": "École Polytechnique Fédérale de Lausanne",
                "@affiliationIdentifier": "https://ror.org/02s376052",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "psi": {
                "#text": "Paul Scherrer Institute",
                "@affiliationIdentifier": "https://ror.org/03eh3y714",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "iap": {"#text": "Institute for Applied Plant Biology"},
            "tropos": {
                "#text": "Leibniz Institute for Tropospheric Research",
                "@affiliationIdentifier": "https://ror.org/03a5xsc56",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
            "unil": {
                "#text": "University of Lausanne",
                "@affiliationIdentifier": "https://ror.org/019whta54",
                "@affiliationIdentifierScheme": "ROR",
                "@schemeURI": "https://ror.org/",
            },
        },
        "relatedItems": "resources",
        "relatedItem": {"url": "url", "title": "name"},
        "odc-odbl": "ODbL-1.0",
        "cc-by-sa": "CC-BY-SA-4.0",
        "cc-by-nc": "CC-BY-NC-4.0",
        "cc-by": "CC-BY-4.0",
        "CC0-1.0": "CC0-1.0",
    }
