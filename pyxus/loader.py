
import fnmatch
import json
import os
import os.path
import requests
import pystache

DEFAULT_SCHEME = "http"
DEFAULT_HOST = "localhost:8080"
DEFAULT_PREFIX = "v0"
DEFAULT_API_ROOT = "{}://{}/{}".format(DEFAULT_SCHEME, DEFAULT_HOST, DEFAULT_PREFIX)
DEFAULT_API_ROOT_DICT = {
    'scheme' : DEFAULT_SCHEME,
    'host' : DEFAULT_HOST,
    'prefix' : DEFAULT_PREFIX
}
JSON_CONTENT = { "Content-type" : "application/json" }

def recursive_find_matching(root_path, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


def list_schemas(root_path):
    return recursive_find_matching(root_path, "*shacl.ttl.json")

def list_instances(root_path):
    return recursive_find_matching(root_path, "*data.json")

def upload_schemas(file_root_path, api_root = DEFAULT_API_ROOT):
    schemas = list_schemas(file_root_path)

def get_this_schema_name(json):
    path_segments = json['@context']['this'].split(os.sep)
    return '/' + os.path.join(*path_segments[5:-2])

def upload_schema(file_path, schema_path = None, api_root = DEFAULT_API_ROOT):
    """Create a new schema or revise an existing.

    Arguments:
    file_path -- path to the location of the schema.json SHACL file to upload.
    schema_path -- path of the schema to create or update. Ensure that you increase the version portion of the path in the case of an update following semantic versioning conventions. Argument takes the form '/{organization}/{domain}/{schema}/{version}'
    Keyword arguments:
    api_root -- URL for the root of the API, default = DEFAULT_API_ROOT
    """
    with open(file_path) as x: schema_str_template = x.read()

    schema_str = pystache.render(schema_str_template, DEFAULT_API_ROOT_DICT)

    schema_json = json.loads(schema_str)

    api_path = DEFAULT_API_ROOT + '/schemas{}'.format(get_this_schema_name(schema_json))

    print "uploading schema to {}".format(api_path)
    r = requests.put(api_path, schema_str, headers = JSON_CONTENT)
    if r.status_code > 201:
        print "Failure uploading schema to {}".format(api_path)
        print "Code:{} ({}) - {}".format(r.status_code, r.reason, r.text)
        print "payload:"
        print schema_str
        return False
    else:
        return True

def upload_orgs(api_root = DEFAULT_API_ROOT):
    orgs = [('hbp', 'The HBP Organization'),
            ('nexus', 'Nexus Core')
            ('bbp', 'The BBP Organization')]

    for (name, desc) in orgs:
        org_json = json.loads("""{ "description": "{}" }""".format(desc))
        requests.put( DEFAULT_API_ROOT + '/organizations/' + name, json.dumps(org_json), headers = JSON_CONTENT)

def upload_domains(api_root = DEFAULT_API_ROOT):
    domains = [('hbp','core','The HBP Core Domain'),
            ('bbp', 'core', 'The BBP Core Domain')]

    for (org, dom, desc) in domains:
        dom_json = json.loads("""{ "description": "{}" }""".format(desc))
        requests.put( DEFAULT_API_ROOT + '/organizations/{}/domain/{}'.format(org,dom) , json.dumps(dom_json), headers = JSON_CONTENT)
