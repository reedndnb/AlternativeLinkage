import csv
import re

COMPANY_URI = 'http://dnb.com/duns/%s'

COMPANY_OBJECTS = ['CASE_GLOB_ULT', 'FRANCHISE_TYPE1', 'OP_DUNS1', 'OP_DUNS_GLOB_ULT1', 'FRANCHISE_TYPE2', 'OP_DUNS2', 'OP_DUNS_GLOB_ULT2',
           'OP_DUNS3', 'OP_DUNS_GLOB_ULT3', 'FRANCHISE_TYPE3', 'OP_DUNS4', 'FRANCHISE_TYPE4', 'OP_DUNS_GLOB_ULT4', 'FRANCHISE_TYPE5',
           'OP_DUNS5', 'OP_DUNS_GLOB_ULT5', 'FRANCHISE_TYPE6', 'OPERATIONAL_DUNS6', 'OP_DUNS_GLOB_ULT6']
JV_OBJECTS = ['MIN_JOINT_VENT_DUNS' + str(i) for i in range(1, 7)]
JV_ATTRS = ['PCT_OWNERSHIP_' + str(i) for i in range(1, 7)]
EXCLUDED_ATTRS = ['CASE_DUNS']

def triple_object(subject, predicate, object):
    return "<%s> <%s> <%s> ." % (subject, predicate, object)

def triple_literal(subject, predicate, object):
    return "<%s> <%s> \"%s\" ." % (subject, predicate, object)

def set_company_uri(key, val, context):
    context['company_uri'] = COMPANY_URI % val

def set_investment_duns(key, val, context):
    context[key] = val

def generic_triple_literal(key, val, context):
    if key in EXCLUDED_ATTRS:
        return

    print(triple_literal(context['company_uri'], 'http://dnb.com/%s' % key.lower(), val))

def generic_triple_company_object(key, val, context):
    print(triple_object(context['company_uri'], 'http://dnb.com/%s' % key.lower(), COMPANY_URI % val))

def investment_uri(company_uri, investment_duns):
    return company_uri + 'investment/' + investment_duns

def joint_venture_object(key, val, context):
    investment_duns = context[key] # duns number of MIN_JOINT_VENT_DUNS{i}
    print(triple_object(context['company_uri'], 'http://dnb.com/company/invests-in', investment_uri(context['company_uri'], investment_duns)))

def joint_venture_attribute(key, val, context):
    m = re.search(r'([0-9]+)$', key)
    if m:
        index = m.group(1)
    else:
        # Ignore
        return

    company_uri = context['company_uri']
    # investment_uri
    # key is something like PCT_OWNERSHIP_{i}
    percent_ownership = val
    investment_duns = context['MIN_JOINT_VENT_DUNS' + index]
    print(triple_literal(investment_uri(company_uri, investment_duns),
                         'http://dnb.com/company/investment/percent_ownership/', percent_ownership))

# Setup mappings of keys to functions for setting context variables
mapping = {'CASE_DUNS' : set_company_uri}
for i in range(1,7):
    mapping['MIN_JOINT_VENT_DUNS' + str(i)] = set_investment_duns

def map_to_triples(row):
    context = {}

    # First pass - set context
    for key in row.keys():
        f = mapping.get(key)
        if f:
            f(key, row[key], context)

    # 2nd pass - output objects
    for key in row.keys():
        val = row[key].strip()
        if not val:
            continue

        row[key] = val
        if key in COMPANY_OBJECTS:
            generic_triple_company_object(key, row[key], context)
        elif key in JV_OBJECTS:
            joint_venture_object(key, row[key], context)
        elif key in JV_ATTRS:
            joint_venture_attribute(key, row[key], context)
        else:
            generic_triple_literal(key, row[key], context)

with open("CPARDO_parsed.csv", "r") as csv_in:
    reader = csv.DictReader(csv_in)
    for row in reader:
        map_to_triples(row)
