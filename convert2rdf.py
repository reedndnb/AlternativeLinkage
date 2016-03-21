import csv
import re

COMPANY_URI = 'http://duns.com/%s/'
OBJECTS = ['CASE_GLOB_ULT', 'FRANCHISE_TYPE1', 'OP_DUNS1', 'OP_DUNS_GLOB_ULT1', 'FRANCHISE_TYPE2', 'OP_DUNS2', 'OP_DUNS_GLOB_ULT2',
           'OP_DUNS3', 'OP_DUNS_GLOB_ULT3', 'FRANCHISE_TYPE3', 'OP_DUNS4', 'FRANCHISE_TYPE4', 'OP_DUNS_GLOB_ULT4', 'FRANCHISE_TYPE5',
           'OP_DUNS5', 'OP_DUNS_GLOB_ULT5', 'FRANCHISE_TYPE6', 'OPERATIONAL_DUNS6', 'OP_DUNS_GLOB_ULT6', 'MIN_JOINT_VENT_DUNS1']

def triple_object(subject, predicate, object):
    return "<%s>, <%s>, <%s>" % (subject, predicate, object)

def triple_literal(subject, predicate, object):
    return "<%s>, <%s>, '%s'" % (subject, predicate, object)

def set_company_uri(val, context):
    context['company_uri'] = COMPANY_URI % val

def generic_triple_literal(key, val, context):
    print(triple_literal(context['company_uri'], 'http://dnb.com/%s' % key.lower(), val))

def generic_triple_company_object(key, val, context):
    print(triple_object(context['company_uri'], 'http://dnb.com/%s' % key.lower(), COMPANY_URI % val))

mapping = {'CASE_GLOB_ULT' : set_company_uri}

def map_to_triples(row):
    context = {}

    # First pass - set context
    for key in row.keys():
        f = mapping.get(key)
        if f and re.match('set_', f.__name__):
            f(row[key], context)

    for key in row.keys():
        f = mapping.get(key)
        if f:
            f(row[key], context)
        else:
            if key in OBJECTS:
                generic_triple_company_object(key, row[key], context)
            else:
                generic_triple_literal(key, row[key], context)

with open("CPARDO_parsed.csv", "r") as csv_in:
    reader = csv.DictReader(csv_in)
    for row in reader:
        print("--- Line ---")
        map_to_triples(row)