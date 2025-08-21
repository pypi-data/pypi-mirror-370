# -*- coding: utf-8 -*-

from collections import OrderedDict
from Products.PloneMeeting import config as PMconfig


product_globals = globals()

PROJECTNAME = "MeetingSeraing"

POWEREDITORS_GROUP_SUFFIX = "powereditors"

# group suffixes
PMconfig.EXTRA_GROUP_SUFFIXES = [
    {
        "fct_title": u"serviceheads",
        "fct_id": u"serviceheads",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"officemanagers",
        "fct_id": u"officemanagers",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
    {
        "fct_title": u"divisionheads",
        "fct_id": u"divisionheads",
        "fct_orgs": [],
        "fct_management": False,
        "enabled": True,
    },
]

SERAING_ITEM_WF_VALIDATION_LEVELS = (
    {'state': 'itemcreated',
     'state_title': 'itemcreated',
     'leading_transition': '-',
     'leading_transition_title': '-',
     'back_transition': 'backToItemCreated',
     'back_transition_title': 'backToItemCreated',
     'suffix': 'creators',
     # only creators may manage itemcreated item
     'extra_suffixes': [],
     'enabled': '1',
     },
    {'state': 'proposed_to_servicehead',
     'state_title': 'proposed_to_servicehead',
     'leading_transition': 'proposeToServiceHead',
     'leading_transition_title': 'proposeToServiceHead',
     'back_transition': 'backToProposedToServiceHead',
     'back_transition_title': 'backToProposedToServiceHead',
     'suffix': 'serviceheads',
     'extra_suffixes': [],
     'enabled': '1',
     },
    {'state': 'proposed_to_officemanager',
     'state_title': 'proposed_to_officemanager',
     'leading_transition': 'proposeToOfficeManager',
     'leading_transition_title': 'proposeToOfficeManager',
     'back_transition': 'backToProposedToOfficeManager',
     'back_transition_title': 'backToProposedToOfficeManager',
     'suffix': 'officemanagers',
     'enabled': '1',
     'extra_suffixes': [],
     },
    {'state': 'proposed_to_divisionhead',
     'state_title': 'proposed_to_divisionhead',
     'leading_transition': 'proposeToDivisionHead',
     'leading_transition_title': 'proposeToDivisionHead',
     'back_transition': 'backToProposedToDivisionHead',
     'back_transition_title': 'backToProposedToDivisionHead',
     'suffix': 'divisionheads',
     'enabled': '1',
     'extra_suffixes': [],
     },
    {'state': 'proposed',
     'state_title': 'proposed',
     'leading_transition': 'propose',
     'leading_transition_title': 'propose',
     'back_transition': 'backToProposed',
     'back_transition_title': 'backToProposed',
     'suffix': 'reviewers',
     'extra_suffixes': [],
     'enabled': '1',
     },
)
