# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2010 by PloneGov
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase
from Products.MeetingSeraing.adapters import customWfAdaptations
from Products.MeetingSeraing.testing import MS_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingSeraing.tests.helpers import MeetingSeraingTestingHelpers
# monkey patch the MeetingConfig.wfAdaptations again because it is done in
# adapters.py but overrided by Products.PloneMeeting here in the tests...
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.model import adaptations


class MeetingSeraingTestCase(MeetingCommunesTestCase, MeetingSeraingTestingHelpers):
    """Base class for defining MeetingSeraing test cases."""

    layer = MS_TESTING_PROFILE_FUNCTIONAL

    subproductIgnoredTestFiles = ['test_robot.py', 'testPerformances.py', 'testContacts.py', 'testVotes.py']

    def _do_transition_with_request(self, obj, transition, comment=''):
        # Since the KeepTakenOverBy use the request to check if the item is transitioning
        # we have to mock the request with the transition in it
        obj.REQUEST.form = {"transition": transition}
        if transition in self.transitions(obj):
            self.do(obj, transition, comment)
        obj.REQUEST.form = {}

    def _setup_seraing_closed_states(self, meetingConfig):
        self._activate_wfas(
            ("seraing_add_item_closed_states",), cfg=meetingConfig, keep_existing=True
        )

        meetingConfig.setOnMeetingTransitionItemActionToExecute(
            meetingConfig.getOnMeetingTransitionItemActionToExecute() + (
                 {'meeting_transition': 'close',
                  'item_action': 'itemfreeze',
                  'tal_expression': ''},
                 {'meeting_transition': 'close',
                  'item_action': 'accept',
                  'tal_expression': ''},
                 {'meeting_transition': 'close',
                  'item_action': 'accept_close',
                  'tal_expression': ''},
                 {'meeting_transition': 'close',
                  'item_action': 'accept_but_modify_close',
                  'tal_expression': ''},
                 {'meeting_transition': 'close',
                  'item_action': 'delay_close',
                  'tal_expression': ''},
            )
        )

    def _setup_seraing_validated_by_DG(self, meetingConfig):
        self._activate_wfas(
            ("seraing_validated_by_DG",), cfg=meetingConfig, keep_existing=True
        )
        meetingConfig.setOnMeetingTransitionItemActionToExecute(
            (
                {'meeting_transition': 'validateByDG',
                 'item_action': 'itemValidateByDG',
                 'tal_expression': ''},
                {'meeting_transition': 'freeze',
                 'item_action': 'itemValidateByDG',
                 'tal_expression': ''},
            ) + meetingConfig.getOnMeetingTransitionItemActionToExecute()
        )

    def setUp(self):
        MeetingCommunesTestCase.setUp(self)
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        self.meetingConfig2 = getattr(self.tool, 'meeting-config-council')
