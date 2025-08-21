# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# GNU General Public License (GPL)
#

from AccessControl import Unauthorized
from DateTime import DateTime
from OFS.ObjectManager import BeforeDeleteException
from Products.CMFPlone.utils import safe_unicode
from Products.MeetingCommunes.tests.testMeetingConfig import testMeetingConfig as mctmc
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from Products.PloneMeeting.events import _itemAnnexTypes
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger
from zope.i18n import translate


class testMeetingConfig(MeetingSeraingTestCase, mctmc):
    '''Call testMeetingConfig tests.'''

    def test_pm_searchItemsToPrevalidate(self):
        '''No sense...'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_searchReviewableItems(self):
        '''Test the searchReviewableItems search.'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_ConfigLinkedGroupsRemovedWhenConfigDeleted(self, ):
        """When the MeetingConfig is deleted, created groups are removed too :
           - meetingmanagers group;
           - powerobservers groups;
           - budgetimpacteditors group.
           """
        self.changeUser('siteadmin')
        newCfg = self.create('MeetingConfig')
        newCfgId = newCfg.getId()
        # this created 6 groups
        created_groups = [groupId for groupId in self.portal.portal_groups.listGroupIds()
                          if groupId.startswith(newCfgId)]
        self.assertEqual(len(created_groups), 6)
        # remove the MeetingConfig, groups are removed as well
        self.tool.restrictedTraverse('@@delete_givenuid')(newCfg.UID())
        self.assertFalse(newCfgId in self.tool.objectIds())
        created_groups = [groupId for groupId in self.portal.portal_groups.listGroupIds()
                          if groupId.startswith(newCfgId)]

    def _usersToRemoveFromGroupsForUpdatePersonalLabels(self):
        """ """
        return ['pmDivisionHead1', 'pmOfficeManager1', 'pmServiceHead1', 'pmReviewerLevel1']

    def test_pm_CanNotRemoveUsedMeetingConfig(self):
        '''While removing a MeetingConfig, it should raise if it is used somewhere...'''
        # work with cfg2 where meetingConfigsToCloneTo and other_mc_correspondences are defined
        cfg = self.meetingConfig
        cfgId = cfg.getId()
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()
        cfg2.setMeetingConfigsToCloneTo(
            ({'meeting_config': cfgId,
              'trigger_workflow_transitions_until': '__nothing__'},)
        )

        # a user can not delete the MeetingConfig
        self.changeUser('pmManager')
        self.assertRaises(Unauthorized, self.tool.manage_delObjects, [cfgId, ])

        # fails if a meeting exists
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2008/06/23 15:39:00').asdatetime())
        self.changeUser('admin')
        with self.assertRaises(BeforeDeleteException) as cm:
            self.tool.manage_delObjects([cfgId, ])
        can_not_delete_meetingconfig_meeting = \
            translate('can_not_delete_meetingconfig_meeting',
                      domain="plone",
                      context=self.request)
        self.assertEqual(cm.exception.message, can_not_delete_meetingconfig_meeting)
        self.portal.restrictedTraverse('@@delete_givenuid')(meeting.UID())

        # fails if an item exists
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.changeUser('admin')
        with self.assertRaises(BeforeDeleteException) as cm:
            self.tool.manage_delObjects([cfgId, ])
        can_not_delete_meetingconfig_meetingitem = \
            translate('can_not_delete_meetingconfig_meetingitem',
                      domain="plone",
                      context=self.request)
        self.assertEqual(cm.exception.message, can_not_delete_meetingconfig_meetingitem)
        self.portal.restrictedTraverse('@@delete_givenuid')(item.UID())

        # fails if another element than searches_xxx folder exists in the pmFolders
        self.changeUser('pmManager')
        pmFolder = self.tool.getPloneMeetingFolder(cfgId)
        afileId = pmFolder.invokeFactory('File', id='afile')
        afile = getattr(pmFolder, afileId)
        self.changeUser('admin')
        with self.assertRaises(BeforeDeleteException) as cm:
            self.tool.manage_delObjects([cfgId, ])
        can_not_delete_meetingconfig_meetingfolder = \
            translate('can_not_delete_meetingconfig_meetingfolder',
                      domain="plone",
                      context=self.request)
        self.assertEqual(cm.exception.message, can_not_delete_meetingconfig_meetingfolder)
        self.portal.restrictedTraverse('@@delete_givenuid')(afile.UID())

        # fails if used in another MeetingConfig (meetingConfigsToCloneTo)
        with self.assertRaises(BeforeDeleteException) as cm:
            self.tool.manage_delObjects([cfgId, ])
        can_not_delete_meetingconfig_meetingconfig = \
            translate('can_not_delete_meetingconfig_meetingconfig',
                      mapping={'other_config_title': cfg2.Title()},
                      domain="plone",
                      context=self.request)
        self.assertEqual(cm.exception.message, can_not_delete_meetingconfig_meetingconfig)
        cfg2.setMeetingConfigsToCloneTo(())

        # fails if an annex_type is used by another MeetingConfig annex_type in other_mc_correspondences
        # here we use cfg2 where correspondences are defined
        self._removeConfigObjectsFor(cfg2)
        cfg.setMeetingConfigsToCloneTo(())
        with self.assertRaises(BeforeDeleteException) as cm:
            self.tool.manage_delObjects([cfg2Id, ])
        can_not_delete_meetingconfig_annex_types = \
            translate('can_not_delete_meetingconfig_annex_types',
                      mapping={'other_config_title': safe_unicode(cfg.Title())},
                      domain="plone",
                      context=self.request)
        self.assertEqual(cm.exception.message, can_not_delete_meetingconfig_annex_types)
        annex_types = _itemAnnexTypes(cfg)
        for annex_type in annex_types:
            annex_type.other_mc_correspondences = set()

        # items stored in MeetingConfig (recurring, itemtemplates) do not avoid removal
        self.assertTrue(cfg.recurringitems.objectIds())
        self.assertTrue(cfg.itemtemplates.objectIds())
        # everything ok, MeetingConfig may be deleted
        self.assertTrue(cfgId in self.tool.objectIds() and cfg2Id in self.tool.objectIds())
        self.tool.manage_delObjects([cfgId, cfg2Id])
        self.assertFalse(cfgId in self.tool.objectIds() or cfg2Id in self.tool.objectIds())
        # elements created by MeetingConfig were deleted (portal_types, groups, metingFolders)
        # portal_types
        all_portal_type_ids = self.portal.portal_types.listContentTypes()
        self.assertEqual([pt for pt in all_portal_type_ids if pt.endswith(cfg.getShortName())], [])
        self.assertEqual([pt for pt in all_portal_type_ids if pt.endswith(cfg2.getShortName())], [])
        # groups, cfg id is suffixed with different values
        all_group_ids = self.portal.portal_groups.listGroupIds()
        # for Seraing we have a global rôle : powereditor
        all_group_ids.remove('meeting-config-college_powereditors')
        all_group_ids.remove('meeting-config-council_powereditors')
        self.assertEqual([gr for gr in all_group_ids if gr.startswith('{0}_'.format(cfgId))], [])
        self.assertEqual([gr for gr in all_group_ids if gr.startswith('{0}_'.format(cfg2Id))], [])
        # meetingFolders
        for member_folder in self.portal.Members.objectValues():
            mymeetings = member_folder.get('mymeetings', None)
            if mymeetings:
                self.assertEqual(mymeetings.objectIds(), [])
            else:
                pm_logger.info(
                    "{0}: no 'mymeetings' folder for user '{1}'".format(
                        self._testMethodName, member_folder.id))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingConfig, prefix='test_pm_'))
    return suite
