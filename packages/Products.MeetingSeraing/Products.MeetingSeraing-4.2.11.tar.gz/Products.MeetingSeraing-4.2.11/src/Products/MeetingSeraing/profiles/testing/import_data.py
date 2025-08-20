# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.MeetingSeraing.config import SERAING_ITEM_WF_VALIDATION_LEVELS
# TODO from Products.PloneMeeting.config import MEETINGREVIEWERS
from Products.PloneMeeting.profiles import PloneGroupDescriptor
from Products.PloneMeeting.profiles import UserDescriptor
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.PloneMeeting.profiles.testing.import_data import cfg1_powerobservers
from Products.PloneMeeting.profiles.testing.import_data import cfg2_powerobservers


data = deepcopy(mc_import_data.data)

# Users and groups -------------------------------------------------------------4
pmServiceHead1 = UserDescriptor("pmServiceHead1", [])
pmOfficeManager1 = UserDescriptor("pmOfficeManager1", [])
pmDivisionHead1 = UserDescriptor("pmDivisionHead1", [])

collegePowerEditors = PloneGroupDescriptor(
    "meeting-config-college_powereditors", "meeting-config-college_powereditors", []
)
powerEditor1 = UserDescriptor("powerEditor1", [])
powerEditor1.ploneGroups = [
    collegePowerEditors,
]

# Inherited users
pmReviewer1 = deepcopy(pm_import_data.pmReviewer1)
pmReviewer2 = deepcopy(pm_import_data.pmReviewer2)
pmReviewerLevel1 = deepcopy(pm_import_data.pmReviewerLevel1)
pmReviewerLevel2 = deepcopy(pm_import_data.pmReviewerLevel2)
pmManager = deepcopy(pm_import_data.pmManager)

# Groups

developers = data.orgs[0]
#developers.serviceheads.append(pmReviewer1)
developers.serviceheads.append(pmServiceHead1)
developers.serviceheads.append(pmReviewerLevel1)
developers.serviceheads.append(pmManager)
developers.officemanagers.append(pmOfficeManager1)
developers.officemanagers.append(pmReviewerLevel2)
#developers.officemanagers.append(pmReviewer1)
developers.officemanagers.append(pmManager)
developers.divisionheads.append(pmDivisionHead1)
#developers.divisionheads.append(pmReviewer1)
developers.divisionheads.append(pmManager)

# to serviceheads that is first reviewer level
developers.prereviewers = [
    descr for descr in developers.prereviewers if descr.id != "pmReviewerLevel1"
]
# TODO getattr(developers, MEETINGREVIEWERS['meetingitemseraing_workflow'].keys()[-1]).append(pmReviewerLevel1)

vendors = data.orgs[1]
vendors.serviceheads.append(pmReviewer2)
vendors.officemanagers.append(pmReviewer2)
vendors.divisionheads.append(pmReviewer2)

# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = deepcopy(mc_import_data.collegeMeeting)
collegeMeeting.workflowAdaptations = ['no_publication', 'pre_accepted', 'accepted_but_modified', 'delayed', 'refused']
collegeMeeting.itemWFValidationLevels = deepcopy(SERAING_ITEM_WF_VALIDATION_LEVELS)
collegeMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "propose",
    "validate",
    "present",
)
collegeMeeting.itemConditionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingItemSeraingCollegeWorkflowConditions"
)
collegeMeeting.itemActionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingItemSeraingCollegeWorkflowActions"
)
collegeMeeting.meetingConditionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingSeraingCollegeWorkflowConditions"
)
collegeMeeting.meetingActionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingSeraingCollegeWorkflowActions"
)



# Conseil communal
councilMeeting = deepcopy(mc_import_data.councilMeeting)
councilMeeting.workflowAdaptations = ['delayed', 'no_publication']
councilMeeting.itemWFValidationLevels = deepcopy(SERAING_ITEM_WF_VALIDATION_LEVELS)
councilMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "propose",
    "validate",
    "present",
)
councilMeeting.itemConditionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingItemSeraingCouncilWorkflowConditions"
)
councilMeeting.itemActionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingItemSeraingCouncilWorkflowActions"
)
councilMeeting.meetingConditionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingSeraingCouncilWorkflowConditions"
)
councilMeeting.meetingActionsInterface = (
    "Products.MeetingSeraing.interfaces.IMeetingSeraingCouncilWorkflowActions"
)
councilMeeting.itemCopyGroupsStates = []

data.meetingConfigs = (collegeMeeting, councilMeeting)
data.usersOutsideGroups += [
    powerEditor1,
    pmServiceHead1,
    pmOfficeManager1,
    pmDivisionHead1,
]
