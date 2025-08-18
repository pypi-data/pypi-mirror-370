from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import URIRef
from typing import List
import json

"""
Author: Fabian Cretton - HEVS

The goal of this file is to become a tool for developers to find a useful shared dimension,
then get the URLs of the terms in order to configure the mapping for a cube's dimension.

It is not yet a class with methods, and contains code that could be more generic.
For instance, query_lindas could be a very generic function as the one found in /lindas/query.py
But existing query_lindas() is specific for ASK queries (returns a bool value)

See an example usage in example_sd.py

This is a first implementation of:
- Basic queries to request shared dimensions information from LINDAS
- Display the results, line by line
"""

def query_lindas(query: str, environment: str):
    """
    Send a SPARQL query to a LINDAS end-point and return the JSON result
    Note: the values of the different environments URL should come from a config file/environment variables 
    """
    match environment:
        case "PROD":
            endpoint = "https://lindas.admin.ch/query"
        case "INT":
            endpoint = "https://int.lindas.admin.ch/query"
        case _:
            endpoint = "https://test.lindas.admin.ch/query"

    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query=query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def list_shared_dimensions(environment: str, name_lng: str="en", offset: int=0, limit: int=0, search_word: str=""):
    """
    List existing Shared Dimensions in a specific environment 
        Returns the JSON object of the SPARQL query result

    Args:
        limit: no limit if 0

    If a SD has a validThrough date, it could be deprecated (depending on the current date)
    """
    query = f"""
        PREFIX meta: <https://cube.link/meta/>
        PREFIX schema: <http://schema.org/>
        SELECT * WHERE {{
            ?sd a meta:SharedDimension .
            OPTIONAL{{ ?sd schema:name ?name .}}
            FILTER(lang(?name) = \"{name_lng}\") 
            OPTIONAL{{?sd schema:validFrom ?validFrom}}
            OPTIONAL{{?sd schema:validThrough ?validThrough}}
        """

    if search_word != "":
        query += f"FILTER contains(?name,\"{search_word}\")"

    query += f"""
        }} 
        ORDER BY ?name 
        OFFSET {offset}
        """
    if limit != 0:
        query += f"LIMIT {limit}"
    
    #print(query)
    return query_lindas(query, environment=environment)

def list_shared_dimensions_print(result: json, environment_for_terms: str=""):
    """
    Print the result of the list_shared_dimensions() query
        To the console, in a friendly manner, one sd per line with its URL, label, validFrom and validThrough values

    Args:
        environment_for_terms: if an environment is passed, for each shared dimension 2 terms will be queried and displayed
            This possibility to display 2 terms by querying LINDAS is just a POC, should be better refined
    """
    # Pretty print the JSON - for debuging purpose
    #print(json.dumps(result, indent=4))
    
    # Loop through the "bindings" and display dimensions name and URL (sd)
    if 'results' in result and 'bindings' in result['results'] and result['results']['bindings']:
        for item in result['results']['bindings']:
            # Extract the 'sd' and 'name' values
            sd = item['sd']['value']
            
            if 'name' in item:
                name = item['name']['value']
            else:
                name = "(no name in that language)"
            
            if 'validFrom' in item:
                validFrom = "- validFrom " + item['validFrom']['value']
            else:
                validFrom = ""

            if 'validThrough' in item:
                validThrough = "- validThrough " + item['validThrough']['value']
            else:
                validThrough = ""

            print(f"{name} <{sd}> {validFrom} {validThrough}")

            # if <parameter to define> -> list 2 terms for that sd
            if environment_for_terms != "":
                termsResult = list_shared_dimension_terms(environment_for_terms, sd, "en", 0, 2)
                print("{ Terms sample:")
                print_sparql_result(termsResult, ["name", "sdTerm"])
                print("}")

    else:
        print("No result binding found in that JSON result") 

def list_shared_dimension_terms(environment: str, sd_URL: URIRef, name_lng: str="en", offset: int=0, limit: int=0):
    """
    List the terms URL of a Shared Dimensions in a specific environment 
        Returns the JSON object of the SPARQL query result

    Args:
        limit: no limit if 0
    """
    query = f"""
        PREFIX schema: <http://schema.org/>
        SELECT * WHERE {{
            ?sdTerm  schema:inDefinedTermSet <{sd_URL}> .
            OPTIONAL{{?sdTerm schema:name ?name .}}
            FILTER(lang(?name) = \"{name_lng}\") 
        }} 
        ORDER BY ?name 
        OFFSET {offset}
        """
    
    if limit != 0:
        query += f"LIMIT {limit}"
    
    #print(query)
    return  query_lindas(query, environment=environment)

def print_sparql_result(result: json, fields: List[str]):
    """
    Print line by line the result of a sparql query, according to the fields in the list parameter
    - Each field is tested for existance (this function do not know about the mandatory/OPTIONAL field in the original query)
    - If a value starts with "http" -> it is displayed inbetween <>
    """

    if 'results' in result and 'bindings' in result['results'] and result['results']['bindings']:
        for item in result['results']['bindings']:
            line = ""
            for field in fields:
                if field in item:
                    fieldValue = item[field]['value']
                    if fieldValue.lower().startswith("http"):
                        fieldValue = "<" + fieldValue + ">"
                else:
                    fieldValue = ""
            
                line += fieldValue + " "

            print(line)
    else:
        print("No result binding found in that JSON result") 