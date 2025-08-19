from typing import List, Dict, Any
from sys import stderr
from os.path import abspath, dirname, sep
from copy import deepcopy

from bmt import Toolkit

from reasoner_validator.trapi import (
    TRAPI_1_5_0,
    TRAPI_1_6_0_BETA,
    LATEST_TRAPI_RELEASE,
    LATEST_TRAPI_MAJOR_MINOR_RELEASE,
    LATEST_TRAPI_MAJOR_MINOR_PATCH_RELEASE
)

TESTS_DIRECTORY = abspath(dirname(__file__))
print(f"Test Directory: {TESTS_DIRECTORY}", file=stderr)

LOCAL_SCHEMA_VERSION = "v1.5.0"
LOCAL_TRAPI_150_SCHEMA_FILEPATH = f"{TESTS_DIRECTORY}{sep}test_data{sep}trapi_schema_v1.5.0.yaml"
BROKEN_SCHEMA_FILEPATH = f"broken-{LOCAL_SCHEMA_VERSION}.yaml"

TRAPI_1_5_TEST_VERSIONS: List = ["1.5", TRAPI_1_5_0]
PRE_1_6_0_TEST_VERSIONS: List = TRAPI_1_5_TEST_VERSIONS
TRAPI_1_6_TEST_VERSIONS: List = ["1.6", TRAPI_1_6_0_BETA]

LATEST_TEST_RELEASES: List = [
    "1",
    LATEST_TRAPI_MAJOR_MINOR_RELEASE,
    LATEST_TRAPI_MAJOR_MINOR_PATCH_RELEASE,
    LATEST_TRAPI_RELEASE
]

ALL_TEST_VERSIONS: List[str] = PRE_1_6_0_TEST_VERSIONS + LATEST_TEST_RELEASES

LATEST_BIOLINK_MODEL_VERSION = Toolkit().get_model_version()

SIMPLE_SAMPLE_NODES = {
    "NCBIGene:29974": {
        "name": "APOBEC1 complementation factor",
        "categories": [
           "biolink:Gene"
        ],
        "attributes": []
    },
    "PUBCHEM.COMPOUND:597": {
        "name": "cytosine",
        "categories": [
            "biolink:SmallMolecule"
        ],
        "attributes": []
    }
}
SAMPLE_NODES_WITH_ATTRIBUTES = deepcopy(SIMPLE_SAMPLE_NODES)
SAMPLE_NODES_WITH_ATTRIBUTES["PUBCHEM.COMPOUND:597"]["attributes"] = [
    {
        "attribute_source": "infores:chembl",
        "attribute_type_id": "biolink:highest_FDA_approval_status",
        "attributes": [],
        "original_attribute_name": "max_phase",
        "value": "FDA Clinical Research Phase 2",
        "value_type_id": "biolink:FDA_approval_status_enum"
    }
]

DEFAULT_KL = {
    "attribute_type_id": "biolink:knowledge_level",
    "value": "not_provided"
}


DEFAULT_AT = {
    "attribute_type_id": "biolink:agent_type",
    "value": "not_provided"
}

DEFAULT_KL_AND_AT_ATTRIBUTES = [DEFAULT_KL, DEFAULT_AT]

# complete edge dereferencing SAMPLE_NODES_WITH_ATTRIBUTES
SAMPLE_EDGE_WITH_ATTRIBUTES_AND_SOURCES = {
    "edge_1": {
        "subject": "NCBIGene:29974",
        "predicate": "biolink:physically_interacts_with",
        "object": "PUBCHEM.COMPOUND:597",
        "attributes": [
            {
                "attribute_source": "infores:hmdb",
                "attribute_type_id": "biolink:stoichiometry",
                "value": 2,
                "attributes": [],
            }
        ] + DEFAULT_KL_AND_AT_ATTRIBUTES,
        "sources": [
            {
                "resource_id": "infores:molepro",
                "resource_role": "primary_knowledge_source"
            }
        ]
    }
}

SAMPLE_NODES_WITH_UNUSED_NODE = deepcopy(SIMPLE_SAMPLE_NODES)
SAMPLE_NODES_WITH_UNUSED_NODE["NCBITaxon:9606"] = {
    "name": "Homo sapiens",
    "categories": [
       "biolink:OrganismTaxon"
    ],
    "attributes": []
}

SAMPLE_EDGE_WITH_WITHOUT_ATTRIBUTES = {
    "edge_1": {
        "subject": "NCBIGene:29974",
        "predicate": "biolink:physically_interacts_with",
        "object": "PUBCHEM.COMPOUND:597",
        "attributes": [],
        "sources": [
            {
                "resource_id": "infores:molepro",
                "resource_role": "primary_knowledge_source"
            }
        ]
    }
}


def sample_edge_with_attributes(attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
    sample_edge = deepcopy(SAMPLE_EDGE_WITH_WITHOUT_ATTRIBUTES)
    sample_edge["edge_1"]["attributes"] = attributes
    return sample_edge
