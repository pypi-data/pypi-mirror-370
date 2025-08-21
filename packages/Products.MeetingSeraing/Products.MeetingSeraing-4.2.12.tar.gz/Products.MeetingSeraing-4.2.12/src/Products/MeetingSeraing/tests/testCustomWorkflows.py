# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from DateTime import DateTime
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase

import datetime as dt


class testCustomWorkflows(MeetingSeraingTestCase):
    """Tests the default workflows implemented in MeetingSeraing."""

    def test_FreezeMeeting(self):
        """
           When we freeze a meeting, every presented items will be frozen
           too and their state will be set to 'itemfrozen'.  When the meeting
           come back to 'created', every items will be corrected and set in the
           'presented' state
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting
        meeting = self.create('Meeting', date=DateTime('2007/12/11 09:00:00').asdatetime())
        # create 2 items and present it to the meeting
        item1 = self.create('MeetingItem', title='The first item')
        self.presentItem(item1)
        item2 = self.create('MeetingItem', title='The second item')
        self.presentItem(item2)
        wftool = self.portal.portal_workflow
        # every presented items are in the 'presented' state
        self.assertEqual('presented', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('presented', wftool.getInfoFor(item2, 'review_state'))
        # every items must be in the 'itemfrozen' state if we freeze the meeting
        self.freezeMeeting(meeting)
        self.assertEqual('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('itemfrozen', wftool.getInfoFor(item2, 'review_state'))
        # when an item is 'itemfrozen' it will stay itemfrozen if nothing
        # is defined in the meetingConfig.onMeetingTransitionItemTransitionToTrigger
        self.meetingConfig.setOnMeetingTransitionItemActionToExecute([])
        self.backToState(meeting, 'created')
        self.assertEqual('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('itemfrozen', wftool.getInfoFor(item2, 'review_state'))

    def test_CloseMeeting(self):
        """
           When we close a meeting, every items are set to accepted if they are still
           not decided...
        """
        self._setup_seraing_closed_states(self.meetingConfig)
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting (with 7 items)
        meeting = self.create('Meeting', date=dt.datetime.now())
        item1 = self.create('MeetingItem')  # id=o2
        item1.setProposingGroup(self.vendors_uid)
        item1.setAssociatedGroups((self.developers_uid,))
        item2 = self.create('MeetingItem')  # id=o3
        item2.setProposingGroup(self.developers_uid)
        item3 = self.create('MeetingItem')  # id=o4
        item3.setProposingGroup(self.vendors_uid)
        item4 = self.create('MeetingItem')  # id=o5
        item4.setProposingGroup(self.developers_uid)
        item5 = self.create('MeetingItem')  # id=o7
        item5.setProposingGroup(self.vendors_uid)
        item6 = self.create('MeetingItem', title='The sixth item')
        item6.setProposingGroup(self.vendors_uid)
        item7 = self.create('MeetingItem')  # id=o8
        item7.setProposingGroup(self.vendors_uid)
        for item in (item1, item2, item3, item4, item5, item6, item7):
            self.presentItem(item)
        # we freeze the meeting
        self.freezeMeeting(meeting)
        # a MeetingManager can put the item back to presented
        self.backToState(item7, 'presented')
        # we decide the meeting
        # while deciding the meeting, every items that where presented are frozen
        self.decideMeeting(meeting)
        # change all items in all different state (except first who is in good state)
        self.backToState(item7, 'presented')
        self.do(item2, 'delay')
        self.do(item3, 'accept')
        self.do(item4, 'accept_but_modify')
        # we close the meeting
        self.do(meeting, 'close')
        # every items must be in the 'decided' state if we close the meeting
        wftool = self.portal.portal_workflow
        # itemfrozen change into accepted
        self.assertEqual('accepted_closed', wftool.getInfoFor(item1, 'review_state'))
        # delayed rest delayed (it's already a 'decide' state)
        self.assertEqual('delayed_closed', wftool.getInfoFor(item2, 'review_state'))
        # pre_accepted change into accepted
        self.assertEqual('accepted_closed', wftool.getInfoFor(item3, 'review_state'))
        # accepted_but_modified rest accepted_but_modified (it's already a 'decide' state)
        self.assertEqual('accepted_but_modified_closed', wftool.getInfoFor(item4, 'review_state'))
        # accepted rest accepted (it's already a 'decide' state)
        self.assertEqual('accepted_closed', wftool.getInfoFor(item6, 'review_state'))
        # presented change into accepted
        self.assertEqual('accepted_closed', wftool.getInfoFor(item7, 'review_state'))

    def test_getOJByCategoryDoReturnSmth(self):
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=dt.datetime.now())
        item = self.create('MeetingItem')
        item.setProposingGroup(self.vendors_uid)
        self.presentItem(item)
        self.assertIsNotNone(meeting.adapted().getOJByCategory())
