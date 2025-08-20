# -*- coding: utf-8 -*-
#
# File: testCustomMeetingItem.py
#
# Copyright (c) 2007-2012 by CommunesPlone.org
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
from datetime import datetime
from DateTime import DateTime
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from Products.CMFCore.permissions import ModifyPortalContent
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from Products.PloneMeeting.config import ITEM_SCAN_ID_NAME
from Products.PloneMeeting.utils import cleanMemoize
from Products.PloneMeeting.utils import get_annexes
from Products.statusmessages.interfaces import IStatusMessage
from zope.annotation import IAnnotations
from zope.i18n import translate


class testCustomMeetingItem(MeetingSeraingTestCase, mctcmi):
    """
    Tests the MeetingItem adapted methods
    """

    def test_onDuplicated(self):
        """
        When a college item is duplicated to the council meetingConfig,
        some fields must be cleaning (fields linked to the real meeting)
        """
        # by default, college items are sendable to council
        destMeetingConfigId = self.meetingConfig2.getId()
        self.assertTrue(
            self.meetingConfig.getMeetingConfigsToCloneTo()
            == (
                {
                    'meeting_config': '%s' % destMeetingConfigId,
                    'trigger_workflow_transitions_until': '__nothing__',
                },
            )
        )
        # create an item in college, set a motivation, send it to council and check
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        item.setDecision('<p>A decision</p>')
        item.setDescription(
            '<p>Lorem ipsum dolor sit amet <span class="highlight-purple">consectetur adipiscing '
            'elit</span>. Nulla fermentum diam vel justo tincidunt aliquam.</p>'
        )
        item.setPvNote('<p>A PV Note</p>')
        item.setDgNote('<p>A DG Note</p>')
        item.setObservations('<p>An intervention during meeting</p>')
        item.setOtherMeetingConfigsClonableTo((destMeetingConfigId,))
        meeting = self.create('Meeting', date=DateTime('2013/05/05').asdatetime())
        self.presentItem(item)
        # now close the meeting so the item is automatically accepted and sent to meetingConfig2
        self.closeMeeting(meeting)
        cfg = self.meetingConfig

        self.assertTrue(item.query_state() in cfg.getItemAutoSentToOtherMCStates())
        self.assertTrue(item._checkAlreadyClonedToOtherMC(destMeetingConfigId))
        # get the item that was sent to meetingConfig2 and check his motivation field
        annotation_key = item._getSentToOtherMCAnnotationKey(destMeetingConfigId)
        newItem = self.portal.uid_catalog(UID=IAnnotations(item)[annotation_key])[
            0
        ].getObject()
        self.assertTrue(newItem.getPvNote() == '')
        self.assertTrue(newItem.getDgNote() == '')
        self.assertTrue(newItem.getObservations() == '')
        self.assertTrue(
            newItem.Description()
            == '<p>Lorem ipsum dolor sit amet . Nulla fermentum diam vel '
               'justo tincidunt aliquam.</p>'
        )

    def test_powerEditor(self):
        """
        The power editor can modified frozen items
        """
        # create an item and a meeting and check locals roles
        self._setup_seraing_validated_by_DG(self.meetingConfig)
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.changeUser('powerEditor1')
        self.failIf(self.hasPermission('Modify portal content', item))
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2013/05/05').asdatetime())
        self.presentItem(item)
        self.failUnless(self.hasPermission('Modify portal content', item))
        self.do(meeting, 'validateByDG')
        self.changeUser('powerEditor1')
        self.failUnless(self.hasPermission('Modify portal content', item))
        self.changeUser('pmManager')
        self.do(meeting, 'freeze')
        self.changeUser('powerEditor1')
        self.failUnless(self.hasPermission('Modify portal content', item))
        self.closeMeeting(meeting)

    def test_PowerEditorMayStoreItemsPodTemplateAsAnnexBatchAction(self):
        """This will store a POD template selected in
           MeetingConfig.meetingItemTemplatesToStoreAsAnnex as an annex
           for every selected items."""

        # define correct config
        cfg = self.meetingConfig
        annex_type_uid = cfg.annexes_types.item_decision_annexes.get('decision-annex').UID()
        cfg.podtemplates.itemTemplate.store_as_annex = annex_type_uid
        cfg.setMeetingItemTemplatesToStoreAsAnnex('itemTemplate__output_format__odt')
        cfg.powerObservers[0]['item_states'] = ['itemcreated', 'itemfrozen', 'presented', 'accepted', 'delayed']
        self._addPrincipalToGroup('powerEditor1', self.cfg1_id+"_powerobservers")
        self._addPrincipalToGroup('powerEditor1', self.cfg2_id+"_powerobservers")
        self._activate_wfas(
            "seraing_powereditors",
            keep_existing=True
        )
        # create meeting with items
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        self.freezeMeeting(meeting)

        # store annex for 3 first items as powerEditor1
        self.changeUser('powerEditor1')
        form = meeting.restrictedTraverse('@@store-items-template-as-annex-batch-action')
        first_3_item_uids = [item.UID for item in meeting.get_items(ordered=True, the_objects=False)[0:3]]
        self.request.form['form.widgets.uids'] = u','.join(first_3_item_uids)
        self.request.form['form.widgets.pod_template'] = 'itemTemplate__output_format__odt'
        form.update()
        form.handleApply(form, None)
        itemTemplateId = cfg.podtemplates.itemTemplate.getId()
        items = meeting.get_items(ordered=True, unrestricted=True)
        # 3 first item have the stored annex
        for i in range(0, 3):
            annexes = get_annexes(items[i])
            self.assertEqual(len(annexes), 1)
            self.assertTrue(annexes[0].used_pod_template_id, itemTemplateId)
        # but not the others
        for i in range(3, 6):
            annexes = get_annexes(items[i])
            self.assertFalse(annexes)

        # call again with next 3 uids
        form = meeting.restrictedTraverse('@@store-items-template-as-annex-batch-action')
        next_3_item_uids = [item.UID for item in meeting.get_items(ordered=True, the_objects=False)[3:6]]
        self.request.form['form.widgets.uids'] = u','.join(next_3_item_uids)
        form.brains = None
        form.update()
        form.handleApply(form, None)
        for i in range(0, 5):
            annexes = get_annexes(items[i])
            self.assertEqual(len(annexes), 1)
            self.assertTrue(annexes[0].used_pod_template_id, itemTemplateId)
        # last element does not have annex
        annexes = get_annexes(items[6])
        self.assertFalse(annexes)

        # call again, last is stored and it does not fail when no items left
        form = meeting.restrictedTraverse('@@store-items-template-as-annex-batch-action')
        last_item_uid = meeting.get_items(ordered=True, the_objects=False)[-1].UID
        self.request.form['form.widgets.uids'] = last_item_uid
        form.brains = None
        form.update()
        form.handleApply(form, None)
        for i in range(0, 6):
            annexes = get_annexes(items[i])
            self.assertEqual(len(annexes), 1)
            self.assertTrue(annexes[0].used_pod_template_id, itemTemplateId)

        # call a last time, when nothing to do, nothing is done
        form = meeting.restrictedTraverse('@@store-items-template-as-annex-batch-action')
        item_uids = [item.UID for item in meeting.get_items(ordered=True, the_objects=False)]
        self.request.form['form.widgets.uids'] = item_uids
        form.update()
        form.handleApply(form, None)
        for i in range(0, 6):
            annexes = get_annexes(items[i])
            self.assertEqual(len(annexes), 1)
            self.assertTrue(annexes[0].used_pod_template_id, itemTemplateId)

    def test_PowerEditorMayStorePodTemplateAsAnnex(self):
        """Power editor may store a Pod template as an annex."""
        # define correct config
        cfg = self.meetingConfig
        cfg.powerObservers[0]['item_states'] = ['itemcreated', 'itemfrozen', 'presented', 'accepted', 'delayed']
        self._addPrincipalToGroup('powerEditor1', self.cfg1_id+"_powerobservers")
        self._addPrincipalToGroup('powerEditor1', self.cfg2_id+"_powerobservers")
        self._activate_wfas(
            "seraing_powereditors",
            keep_existing=True
        )
        self.changeUser('pmCreator1')
        pod_template, annex_type, item = self._setupStorePodAsAnnex()
        # remove defined store_as_annex for now
        pod_template.store_as_annex = annex_type.UID()

        # the document-generation view
        self.request.set('HTTP_REFERER', item.absolute_url())
        view = item.restrictedTraverse('@@document-generation')

        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=datetime(2022, 8, 19))
        self.presentItem(item)
        self.freezeMeeting(meeting)

        self.changeUser('powerEditor1')
        # Try to store
        self.assertEqual(get_annexes(item), [])
        url = view()
        # after call to view(), user is redirected to the item view
        self.assertEqual(url, item.absolute_url())
        # now we have an annex
        annex = get_annexes(item)[0]
        self.assertEqual(annex.used_pod_template_id, pod_template.getId())
        messages = IStatusMessage(self.request).show()
        self.assertEqual(messages[-1].message, "The annex was stored.")
        # we can not store an annex using a POD template several times, we get a status message
        view()
        # no extra annex
        self.assertEqual(get_annexes(item), [annex])
        messages = IStatusMessage(self.request).show()
        last_msg = messages[-1].message
        can_not_store_several_times_msg = translate(
            u'store_podtemplate_as_annex_can_not_store_several_times',
            domain='PloneMeeting',
            context=self.request)
        self.assertEqual(last_msg, can_not_store_several_times_msg)

        # scan_id : if found in the REQUEST during storage, it is set
        self.assertIsNone(annex.scan_id)
        self.request.set(ITEM_SCAN_ID_NAME, DEFAULT_SCAN_ID)
        self.deleteAsManager(annex.UID())
        view()
        annex = get_annexes(item)[0]
        self.assertEqual(annex.scan_id, DEFAULT_SCAN_ID)

    def test_PowerEditorMayAddBarcodeOnAnnexes(self):
        """Power editor may add barcodes on annexes."""
        self.portal.portal_plonemeeting.setEnableScanDocs(True)
        cfg = self.meetingConfig
        cfg.powerObservers[0]['item_states'] = ['itemcreated', 'itemfrozen', 'presented', 'accepted', 'delayed']
        self._addPrincipalToGroup('powerEditor1', self.cfg1_id+"_powerobservers")
        self._addPrincipalToGroup('powerEditor1', self.cfg2_id+"_powerobservers")
        self._activate_wfas(
            "seraing_powereditors",
            keep_existing=True
        )
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        annex_txt = self.addAnnex(item)
        annex_pdf = self.addAnnex(item, annexFile=self.annexFilePDF)
        view = annex_pdf.restrictedTraverse('@@insert-barcode')

        # as normal user, able to edit but not able to insert barcode
        self.changeUser('pmCreator1')
        self.assertTrue(self.member.has_permission(ModifyPortalContent, view.context))
        self.assertFalse(view.may_insert_barcode())

        # now as MeetingManager
        self.changeUser('pmManager')
        view.context.manage_setLocalRoles(self.member.getId(), ('MeetingManager', 'Editor'))
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        self.assertTrue(self.member.has_permission(ModifyPortalContent, view.context))
        self.assertTrue(view.may_insert_barcode())

        # now as powerEditor
        annex_pdf = self.addAnnex(item, annexFile=self.annexFilePDF)
        view = annex_pdf.restrictedTraverse('@@insert-barcode')
        self.changeUser('powerEditor1')
        view.context.manage_setLocalRoles(self.member.getId(), ('Contributor', 'Editor'))
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        # item is in itemcreated state, powerEditor1 cannot add barcode at this point
        self.assertFalse(view.may_insert_barcode())

        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=datetime(2022, 8, 19))
        self.presentItem(item)
        self.freezeMeeting(meeting)
        self.changeUser('powerEditor1')
        view.context.manage_setLocalRoles(self.member.getId(), ('Contributor', 'Editor'))
        view = annex_pdf.restrictedTraverse('@@insert-barcode')
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        # item is in frozen state, powerEditor1 can add barcode at this point
        self.assertTrue(view.may_insert_barcode())

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
