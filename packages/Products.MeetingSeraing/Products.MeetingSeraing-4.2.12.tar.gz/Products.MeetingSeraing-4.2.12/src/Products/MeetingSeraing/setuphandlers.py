# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre NUYENS <andre.nuyens@imio.be>"""
__docformat__ = 'plaintext'


from plone import api
from Products.MeetingSeraing.config import PROJECTNAME
from Products.PloneMeeting.exportimport.content import ToolInitializer

import logging
import os


logger = logging.getLogger('MeetingSeraing: setuphandlers')


def isNotMeetingSeraingProfile(context):
    return context.readDataFile("MeetingSeraing_marker.txt") is None


def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingSeraingProfile(context):
        return
    wft = api.portal.get_tool('portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingSeraingProfile(context):
        return
    site = context.getSite()
    # need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    showHomeTab(context, site)
    reorderSkinsLayers(context, site)


def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" % (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isMeetingSeraingConfigureProfile(context):
    return context.readDataFile("MeetingSeraing_seraing_marker.txt") or \
        context.readDataFile("MeetingSeraing_codir_marker.txt") or \
        context.readDataFile("MeetingSeraing_zones_marker.txt")


def installMeetingSeraing(context):
    """ Run the default profile before bing able to run the Seraing profile"""
    if not isMeetingSeraingConfigureProfile(context):
        return

    logStep("installMeetingSeraing", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingSeraing:default')


def reinstallPloneMeeting(context, site):
    """Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example."""

    if isNotMeetingSeraingProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)
    # launch skins step for MeetingSeraing so MeetingSeraing skin layers are before PM ones
    site.portal_setup.runImportStepFromProfile('profile-Products.MeetingSeraing:default', 'skins')


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def initializeTool(context):
    """Initialises the PloneMeeting tool based on information from the current
       profile."""
    if not isMeetingSeraingConfigureProfile(context):
        return

    logStep("initializeTool", context)
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingSeraingProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reinstallPloneMeetingSkin(context, site):
    """
       Reinstall Products.plonemeetingskin as the reinstallation of MeetingSeraing
       change the portal_skins layers order
    """
    if isNotMeetingSeraingProfile(context):
        return

    logStep("reinstallPloneMeetingSkin", context)
    try:
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:default')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin')
    except KeyError:
        # if the Products.plonemeetingskin profile is not available
        # (not using plonemeetingskin or in testing?) we pass...
        pass


def reorderSkinsLayers(context, site):
    """
       Reinstall Products.plonemeetingskin and re-apply MeetingSeraing skins.xml step
       as the reinstallation of MeetingSeraing and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingSeraingProfile(context) and isMeetingSeraingConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    try:
        site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingSeraing:default', 'skins')
    except KeyError:
        # if the Products.plonemeetingskin profile is not available
        # (not using plonemeetingskin or in testing?) we pass...
        pass


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingSeraingProfile(context) and isMeetingSeraingConfigureProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)
    portal_css = site.portal_css
    css = ['imio.dashboard.css',
           'plonemeeting.css',
           'meetingseraing.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']

    for resource in css:
        portal_css.moveResourceToBottom(resource)
