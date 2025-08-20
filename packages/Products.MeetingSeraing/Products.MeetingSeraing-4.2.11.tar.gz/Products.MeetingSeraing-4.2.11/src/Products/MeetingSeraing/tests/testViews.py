# -*- coding: utf-8 -*-
#
# File: testViews.py
#
# Copyright (c) 2007-2015 by Imio.be
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
from AccessControl import Unauthorized
from Products.CMFCore.permissions import View
from Products.MeetingCommunes.tests.testViews import testViews as mctv
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from datetime import datetime


class testViews(MeetingSeraingTestCase, mctv):
    ''' '''
    def test_pm_MeetingUpdateItemReferences(self):
        """Test call to @@update-item-references from the meeting that will update
           every references of items of a meeting."""

        self._activate_wfas((
            'seraing_powereditors',
        ), keep_existing=True)

        cfg = self.meetingConfig
        # remove recurring items in self.meetingConfig
        self._removeConfigObjectsFor(cfg)
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        meeting = self.create('Meeting', date=datetime(2017, 3, 3))
        self.presentItem(item)
        self.freezeMeeting(meeting)
        self.assertEqual(item.getItemReference(), 'Ref. 20170303/1')
        # change itemReferenceFormat to include an item data (Title)
        cfg.setItemReferenceFormat(
            "python: here.getMeeting().date.strftime('%Y%m%d') + '/' + "
            "here.getItemNumber(for_display=True)")

        # XXX MeetingSeraing
        meetingTypeName = cfg.getMeetingTypeName()
        fti = cfg.portal_types[meetingTypeName]
        action = fti.getActionObject("object_buttons/update_item_references")
        self.assertIn("object.adapted().may_update_item_references()", action.condition.text)

        self.assertTrue(meeting.adapted().may_update_item_references())
        view = meeting.restrictedTraverse('@@update-item-references')
        view()
        self.assertEqual(item.getItemReference(), '20170303/1')

        self.changeUser('powerEditor1')
        self.assertTrue(meeting.adapted().may_update_item_references())

        # the view is not available to other users
        self.changeUser('pmCreator1')
        self.assertFalse(meeting.adapted().may_update_item_references())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testViews, prefix='test_pm_'))
    return suite
