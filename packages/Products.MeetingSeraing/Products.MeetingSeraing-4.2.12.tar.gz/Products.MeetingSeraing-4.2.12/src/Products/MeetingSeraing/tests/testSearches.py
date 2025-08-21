# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# GNU General Public License (GPL)
#

from collective.compoundcriterion.interfaces import ICompoundCriterionFilter
from Products.MeetingCommunes.tests.testSearches import testSearches as mcts
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger
from zope.component import getAdapter


class testSearches(MeetingSeraingTestCase, mcts):
    """Test searches."""

    def test_pm_SearchItemsToCorrectToValidateOfHighestHierarchicLevel(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_SearchItemsToCorrectToValidateOfEveryReviewerGroups(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_SearchItemsToValidateOfHighestHierarchicLevelReturnsEveryLevels(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_SearchItemsToValidateOfHighestHierarchicLevel(self):
        '''Not used yet...'''
        pm_logger.info("Bypassing , {0} not used in MeetingSeraing".format(
            self._testMethodName))

    def test_pm_SearchMyItemsTakenOver(self):
        '''Test the 'search-my-items-taken-over' method.  This should return
           a list of items a user has taken over.'''
        self.changeUser('admin')
        # specify that copyGroups can see the item when it is proposed
        cfg = self.meetingConfig
        self._enableField('copyGroups')
        cfg.setItemCopyGroupsStates((self._stateMappingFor('proposed'), 'validated', ))
        cfg.setTransitionsReinitializingTakenOverBy(["validate"])

        # first test the generated query
        adapter = getAdapter(cfg,
                             ICompoundCriterionFilter,
                             name='my-items-taken-over')
        # query is correct
        self.changeUser('pmManager')
        self.assertEqual(adapter.query,
                         {'portal_type': {'query': cfg.getItemTypeName()},
                          'getTakenOverBy': {'query': 'pmManager'}})

        # now do the query
        # this adapter is used by the "searchmyitemstakenover"
        collection = cfg.searches.searches_items.searchmyitemstakenover
        item = self.create('MeetingItem')
        # by default nothing is returned
        self.failIf(collection.results())
        # now take item over
        item.setTakenOverBy(self.member.getId())
        item.reindexObject(idxs=['getTakenOverBy', ])
        # now it is returned
        self.failUnless(collection.results())
        for transition in self.TRANSITIONS_FOR_PROPOSING_ITEM_1:
            self._do_transition_with_request(item, transition)
        self.assertEqual(self.member.getId(), item.getTakenOverBy())
        self.failUnless(collection.results())
        for transition in self.TRANSITIONS_FOR_VALIDATING_ITEM_1:
            self._do_transition_with_request(item, transition)
        self.failIf(collection.results())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSearches, prefix='test_pm_'))
    return suite
