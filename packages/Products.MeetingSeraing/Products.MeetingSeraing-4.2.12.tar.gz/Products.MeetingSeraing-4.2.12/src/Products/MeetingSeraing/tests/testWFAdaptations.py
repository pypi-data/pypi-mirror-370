# -*- coding: utf-8 -*-
#
# File: testWFAdaptations.py
#
# GNU General Public License (GPL)
#

from DateTime import DateTime
from Products.CMFCore.permissions import ModifyPortalContent, DeleteObjects
from Products.CMFCore.permissions import ReviewPortalContent
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from Products.PloneMeeting.config import MEETING_REMOVE_MOG_WFA
from Products.PloneMeeting.model.adaptations import RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger
from imio.helpers.content import get_vocab_values

import datetime as dt


class testWFAdaptations(MeetingSeraingTestCase, mctwfa):
    '''Tests various aspects of votes management.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Most of wfAdaptations makes no sense, just make sure most are disabled.'''
        self.assertSetEqual(
            set(get_vocab_values(self.meetingConfig, 'WorkflowAdaptations')),
            {
                'item_validation_shortcuts',
                'item_validation_no_validate_shortcuts',
                'only_creator_may_delete',
                'no_freeze',
                'no_publication',
                'no_decide',
                'accepted_but_modified',
                'postpone_next_meeting',
                'mark_not_applicable',
                'removed',
                'removed_and_duplicated',
                'refused',
                'delayed',
                'pre_accepted',
                "seraing_add_item_closed_states",
                "seraing_validated_by_DG",
                "seraing_powereditors",
                "return_to_proposing_group",
                "return_to_proposing_group_with_last_validation",
                "seraing_return_to_proposing_group_with_last_validation_patch",
                "seraing_returned_to_advise",
                'accepted_out_of_meeting',
                'accepted_out_of_meeting_and_duplicated',
                'accepted_out_of_meeting_emergency',
                'accepted_out_of_meeting_emergency_and_duplicated',
                MEETING_REMOVE_MOG_WFA
            }
        )

    def test_pm_WFA_no_publication(self):
        '''No sense...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_WFA_pre_validation(self):
        '''No sense...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_WFA_only_creator_may_delete(self):
        '''No sense...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_WFA_return_to_proposing_group_with_hide_decisions_when_under_writing(
            self,
    ):
        '''No sense...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_WFA_return_to_proposing_group_with_all_validations(self):
        '''Not used yet...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_WFA_return_to_proposing_group_with_last_validation(self):
        super(
            testWFAdaptations, self
        ).test_pm_WFA_return_to_proposing_group_with_last_validation()

    def test_pm_WFA_hide_decisions_when_under_writing(self):
        '''No sense...'''
        pm_logger.info(
            "Bypassing , {0} not used in MeetingSeraing".format(self._testMethodName)
        )

    def test_pm_Validate_workflowAdaptations_dependencies(self):
        """Bypass as most WFA not used..."""
        pass

    def test_pm_WFA_no_validation(self):
        '''Not used yet...'''
        pass

    def _return_to_proposing_group_inactive(self):
        '''Tests while 'return_to_proposing_group' wfAdaptation is inactive.'''
        # this is active by default in MeetingSeraing council wf
        return

    def _return_to_proposing_group_active_state_to_clone(self):
        '''Helper method to test 'return_to_proposing_group' wfAdaptation regarding the
        RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE defined value.
        In our usecase, this is Nonsense as we use RETURN_TO_PROPOSING_GROUP_CUSTOM_PERMISSIONS.'''
        return

    def _return_to_proposing_group_active_wf_functionality(self):
        '''Tests the workflow functionality of using the 'return_to_proposing_group' wfAdaptation.
        Same as default test until the XXX here under.'''
        # while it is active, the creators of the item can edit the item as well as the MeetingManagers
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.validateItem(item)
        # create a Meeting and add the item to it
        self.changeUser('pmManager')
        self.create('Meeting', date=dt.datetime.now())
        self.presentItem(item)
        # now that it is presented, the pmCreator1/pmReviewer1 can not edit it anymore
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.hasPermission('Modify portal content', item))
        # the item can be send back to the proposing group by the MeetingManagers only
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.wfTool.getTransitionsFor(item))
        self.changeUser('pmManager')
        self.failUnless(
            'return_to_proposing_group'
            in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
        )
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')
        self.changeUser('pmCreator1')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # MeetingManagers can still edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # the reviewer (director) can send the item back to the meeting managers, as the meeting managers
        for userId in ('pmReviewer1', 'pmManager'):
            self.changeUser(userId)
            self.failUnless(
                'backTo_presented_from_returned_to_proposing_group'
                in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
            )
        # when the creator send the item back to the meeting, it is in the right state depending
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'backTo_presented_from_returned_to_proposing_group')
        self.assertEqual(item.query_state(), 'presented')

    def _return_to_proposing_group_with_validation_active_wf_functionality(self, all=True):
        '''Tests the workflow functionality of using the
           'return_to_proposing_group_with_last_validation' wfAdaptation.'''
        # while it is active, the creators of the item can edit the item as well as the MeetingManagers
        # after, he must be sent to reviewer the item
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.validateItem(item)
        # create a Meeting and add the item to it
        self.changeUser('pmManager')
        meeting = self.create('Meeting')
        self.presentItem(item)
        # now that it is presented, the pmCreator1/pmReviewer1 can not edit it anymore
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.hasPermission(ModifyPortalContent, item))
        # the item can be sent back to the proposing group by the MeetingManagers only
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.transitions(item))
        self.changeUser('pmManager')
        self.failUnless('return_to_proposing_group' in self.transitions(item))
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')
        self.changeUser('pmCreator1')
        self.failUnless(self.hasPermission(ModifyPortalContent, item))
        # the item creator may not be able to delete the item
        self.failIf(self.hasPermission(DeleteObjects, item))
        # MeetingManagers can still edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission(ModifyPortalContent, item))
        # Now send item to the reviewer
        self._process_transition_for_correcting_item(item, all)
        # check that pretty_link is displayed correctly
        self.assertTrue(item.getPrettyLink())
        # the item creator may not be able to modify the item
        self.changeUser('pmCreator1')
        self.failIf(self.hasPermission(ModifyPortalContent, item))
        # MeetingManagers can still edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission(ModifyPortalContent, item))
        # the reviewer can send the item back to the meeting managers, as the meeting managers
        self.changeUser('pmReviewer1')
        for userId in ('pmReviewer1', 'pmManager'):
            self.changeUser(userId)
            self.failUnless('backTo_presented_from_returned_to_proposing_group' in self.transitions(item))
        # when the creator send the item back to the meeting, it is in the right state depending
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'backTo_presented_from_returned_to_proposing_group')
        self.assertEqual(item.query_state(), 'presented')
        # send the item back to proposing group, freeze the meeting then send
        # the item back to the meeting the item should be now in the item state
        # corresponding to the meeting frozen state, so 'itemfrozen'
        self.do(item, 'return_to_proposing_group')
        self._process_transition_for_correcting_item(item, all)
        # check that pretty_link is displayed correctly
        self.assertTrue(item.getPrettyLink())
        self.changeUser('pmManager')
        self.freezeMeeting(meeting)
        self.do(item, 'backTo_itemfrozen_from_returned_to_proposing_group')
        self.assertEqual(item.query_state(), 'itemfrozen')

    def test_pm_WFA_return_to_advise(self):
        '''Test the workflowAdaptation 'return_to_advise'.'''
        # ease override by subproducts
        cfg = self.meetingConfig
        # activate the wfAdaptations and check
        self._activate_wfas(
            ('return_to_proposing_group_with_last_validation', 'seraing_returned_to_advise', 'seraing_validated_by_DG')
        )
        # test what should happen to the wf (added states and transitions)
        # self._return_to_advise_active()
        # test the functionnality of returning an item to the advise
        self._return_to_advise_active_wf_functionality()

    def _return_to_advise_active(self):
        '''Tests while 'return_to_advise' wfAdaptation is active.'''
        # we subdvise this test in 3, testing every constants, this way,
        # a subplugin can call these test separately
        # using RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES
        self._return_to_advise_active_from_item_states()

    def _return_to_advise_active_from_item_states(self):
        '''Helper method to test 'returned_to_advise' wfAdaptation regarding the
        RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES defined value.'''
        # make sure the 'return_to_proposing_group' state does not exist in the item WF
        itemWF = self.wfTool.getWorkflowsFor(self.meetingConfig.getItemTypeName())[0]
        self.failUnless('seraing_returned_to_advise' in itemWF.states)
        # check from witch state we can go to 'returned_to_item', it corresponds
        # to model.adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES
        from_states = set()
        for state in itemWF.states.values():
            if 'seraing_returned_to_advise' in state.transitions:
                from_states.add(state.id)
        # at least every states in from_states were defined in RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES
        self.failIf(
            from_states.difference(set(RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES))
        )

    def _return_to_advise_active_wf_functionality(self):
        '''Tests the workflow functionality of using the 'return_to_proposing_group' wfAdaptation.
        Same as default test until the XXX here under.'''
        # while it is active, the creators of the item can edit the item as well as the MeetingManagers
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.validateItem(item)
        # create a Meeting and add the item to it
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime("2022/07/12 12:00:00").asdatetime())
        self.presentItem(item)
        self.assertTrue('return_to_advise' in self.transitions(item))
        # now that it is presented, the pmCreator1/pmReviewer1 can not edit it anymore
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.hasPermission('Modify portal content', item))
        # the item can be send back to the proposing group by the MeetingManagers only
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.wfTool.getTransitionsFor(item))
        self.changeUser('pmManager')
        self.failUnless(
            'return_to_advise'
            in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
        )
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')

        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failUnless(self.hasPermission(ModifyPortalContent, item))
            self.failUnless(self.hasPermission(ReviewPortalContent, item))
            self.failUnless(
                'return_to_advise'
                in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
            )
            self.failUnless(
                'goTo_returned_to_proposing_group_proposed'
                in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
            )

        self.do(item, 'return_to_advise')
        for userId in ('pmCreator1', 'pmReviewer1'):
            self.changeUser(userId)
            self.failIf(self.hasPermission(ModifyPortalContent, item))
            self.failUnless(self.hasPermission(ReviewPortalContent, item))
            self.failUnless(
                'goTo_returned_to_proposing_group_proposed'
                in [tr['name'] for tr in self.wfTool.getTransitionsFor(item)]
            )

        # MeetingManagers can edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # XXX specific to MeetingSeraing
        self.assertListEqual(
            self.transitions(item),
            [
                'goTo_returned_to_proposing_group_proposed',
            ],
        )
        self.do(
            item,
            'goTo_returned_to_proposing_group_proposed',
        )
        self.do(item, 'return_to_advise')
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'goTo_returned_to_proposing_group_proposed')
        self.assertEqual(item.query_state(), 'returned_to_proposing_group_proposed')
        self.assertTrue('return_to_advise' in self.transitions(item))
        self.do(item, 'backTo_presented_from_returned_to_proposing_group')
        self.do(meeting, 'validateByDG')
        self.assertTrue('return_to_advise' in self.transitions(item))
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')
        self.do(item, 'return_to_advise')
        self.changeUser('pmCreator1')
        self.failIf(self.hasPermission('Modify portal content', item))
        # MeetingManagers can edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission('Modify portal content', item))

        # assert item may only go back to returned_to_proposing_group or to returned_to_proposing_group_proposed
        self.assertListEqual(
            self.transitions(item),
            [
                'goTo_returned_to_proposing_group_proposed',
            ],
        )
        self.do(
            item,
            'goTo_returned_to_proposing_group_proposed',
        )
        self.do(item, 'return_to_advise')
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'goTo_returned_to_proposing_group_proposed')
        self.assertEqual(item.query_state(), 'returned_to_proposing_group_proposed')
        self.assertTrue('return_to_advise' in self.transitions(item))
        self.do(item, 'backTo_validated_by_dg_from_returned_to_proposing_group')
        self.assertEqual(item.query_state(), 'validated_by_dg')
        self.do(meeting, 'freeze')
        self.assertTrue('return_to_advise' in self.transitions(item))
        # send the item back to the proposing group so the proposing group as an edit access to it
        self.do(item, 'return_to_proposing_group')
        self.do(item, 'return_to_advise')
        self.changeUser('pmCreator1')
        self.failIf(self.hasPermission('Modify portal content', item))
        # MeetingManagers can edit it also
        self.changeUser('pmManager')
        self.failUnless(self.hasPermission('Modify portal content', item))
        # on the meeting state.  Here, when meeting is 'frozen', the item is back to 'itemfrozen'
        # assert item may only go back to returned_to_proposing_group or to returned_to_proposing_group_proposed
        self.assertListEqual(
            self.transitions(item),
            [
                'goTo_returned_to_proposing_group_proposed',
            ],
        )
        self.do(
            item,
            'goTo_returned_to_proposing_group_proposed',
        )
        self.do(item, 'return_to_advise')
        # on the meeting state.  Here, when meeting is 'created', the item is back to 'presented'
        self.do(item, 'goTo_returned_to_proposing_group_proposed')
        self.assertEqual(item.query_state(), 'returned_to_proposing_group_proposed')
        self.assertTrue('return_to_advise' in self.transitions(item))
        self.do(item, 'backTo_itemfrozen_from_returned_to_proposing_group')
        self.assertEqual(item.query_state(), 'itemfrozen')

    def _all_no_active(self):
        '''Tests while all wfAdaptations are inactive.'''
        # this not available in MeetingSeraing
        return

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
