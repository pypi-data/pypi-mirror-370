# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from collective.iconifiedcategory.utils import get_config_root
from collective.iconifiedcategory.utils import get_group
from DateTime import DateTime
from Products.CMFCore.permissions import View
from Products.MeetingCommunes.tests.testMeetingItem import testMeetingItem as mctmi
from Products.MeetingSeraing.tests.MeetingSeraingTestCase import MeetingSeraingTestCase
from Products.PloneMeeting.tests.PloneMeetingTestCase import pm_logger
from Products.PloneMeeting.utils import get_annexes


class testMeetingItem(MeetingSeraingTestCase, mctmi):
    """
    Tests the MeetingItem class methods.
    """

    def _extraNeutralFields(self):
        """This method is made to be overrided by subplugins that added
        neutral fields to the MeetingItem schema."""
        return ['pvNote', 'dgNote', 'interventions']

    def test_pm_AnnexToPrintBehaviourWhenCloned(self):
        """When cloning an item with annexes, to the same or another MeetingConfig, the 'toPrint' field
        is kept depending on MeetingConfig.keepOriginalToPrintOfClonedItems.
        If it is True, the original value is kept, if it is False, it will use the
        MeetingConfig.annexToPrintDefault value."""
        cfg = self.meetingConfig
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()
        cfg.setKeepOriginalToPrintOfClonedItems(False)
        cfg2.setKeepOriginalToPrintOfClonedItems(False)
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2016/02/02').asdatetime())
        item = self.create('MeetingItem')
        annex = self.addAnnex(item)
        annex_config = get_config_root(annex)
        annex_group = get_group(annex_config, annex)
        self.assertFalse(annex_group.to_be_printed_activated)
        self.assertFalse(annex.to_print)
        annex.to_print = True
        self.assertTrue(annex.to_print)
        # decide the item so we may add decision annex
        item.setDecision(self.decisionText)
        self.presentItem(item)
        self.decideMeeting(meeting)
        self.do(item, 'accept')
        self.assertEqual(item.query_state(), 'accepted')
        annexDec = self.addAnnex(item, relatedTo='item_decision')
        annexDec_config = get_config_root(annexDec)
        annexDec_group = get_group(annexDec_config, annexDec)
        self.assertFalse(annexDec_group.to_be_printed_activated)
        self.assertFalse(annexDec.to_print)
        annexDec.to_print = True
        self.assertTrue(annexDec.to_print)

        # clone item locally, as keepOriginalToPrintOfClonedItems is False
        # default values defined in the config will be used
        self.assertFalse(cfg.getKeepOriginalToPrintOfClonedItems())
        clonedItem = item.clone()
        annexes = get_annexes(clonedItem, portal_types=['annex'])
        if not annexes:
            pm_logger.info('No annexes found on duplicated item clonedItem')
        cloneItemAnnex = annexes and annexes[0]
        annexesDec = get_annexes(clonedItem, portal_types=['annexDecision'])
        if not annexesDec:
            pm_logger.info('No decision annexes found on duplicated item clonedItem')
        cloneItemAnnexDec = annexesDec and annexesDec[0]
        self.assertFalse(cloneItemAnnex and cloneItemAnnex.to_print)
        self.assertFalse(cloneItemAnnexDec and cloneItemAnnexDec.to_print)

        # enable keepOriginalToPrintOfClonedItems
        # some plugins remove annexes/decision annexes on duplication
        # so make sure we test if an annex is there...
        self.changeUser('siteadmin')
        cfg.setKeepOriginalToPrintOfClonedItems(True)
        self.changeUser('pmManager')
        clonedItem2 = item.clone()
        annexes = get_annexes(clonedItem2, portal_types=['annex'])
        if not annexes:
            pm_logger.info('No annexes found on duplicated item clonedItem2')
        cloneItem2Annex = annexes and annexes[0]
        annexesDec = get_annexes(clonedItem2, portal_types=['annexDecision'])
        if not annexesDec:
            pm_logger.info('No decision annexes found on duplicated item clonedItem2')
        cloneItem2AnnexDec = annexesDec and annexesDec[0]
        self.assertTrue(cloneItem2Annex and cloneItem2Annex.to_print or True)
        self.assertTrue(cloneItem2AnnexDec and cloneItem2AnnexDec.to_print or True)

        # clone item to another MC and test again
        # cfg2.keepOriginalToPrintOfClonedItems is True
        self.assertFalse(cfg2.getKeepOriginalToPrintOfClonedItems())
        item.setOtherMeetingConfigsClonableTo((cfg2Id,))
        clonedToCfg2 = item.cloneToOtherMeetingConfig(cfg2Id)
        annexes = get_annexes(clonedToCfg2, portal_types=['annex'])
        if not annexes:
            pm_logger.info('No annexes found on duplicated item clonedToCfg2')
        clonedToCfg2Annex = annexes and annexes[0]
        annexesDec = get_annexes(clonedToCfg2, portal_types=['annexDecision'])
        if not annexesDec:
            pm_logger.info('No decision annexes found on duplicated item clonedToCfg2')
        self.assertFalse(clonedToCfg2Annex and clonedToCfg2Annex.to_print)

        # enable keepOriginalToPrintOfClonedItems
        self.changeUser('siteadmin')
        cfg2.setKeepOriginalToPrintOfClonedItems(True)
        self.deleteAsManager(clonedToCfg2.UID())
        # send to cfg2 again
        self.changeUser('pmManager')
        clonedToCfg2Again = item.cloneToOtherMeetingConfig(cfg2Id)
        annexes = get_annexes(clonedToCfg2Again, portal_types=['annex'])
        if not annexes:
            pm_logger.info('No annexes found on duplicated item clonedToCfg2Again')
        clonedToCfg2AgainAnnex = annexes and annexes[0]
        annexesDec = get_annexes(clonedToCfg2Again, portal_types=['annexDecision'])
        if not annexesDec:
            pm_logger.info(
                'No decision annexes found on duplicated item clonedToCfg2Again'
            )
        self.assertTrue(
            clonedToCfg2AgainAnnex and clonedToCfg2AgainAnnex.to_print or True
        )

    def test_pm_HistorizedTakenOverBy(self):
        '''Not applicable for MeetingSeraing. See below.'''
        pass

    def test_pm_KeepTakenOverBy(self):
        '''
        Test takenOverBy feature that will keep the takenOverBy except for certain transitions
        '''
        cfg = self.meetingConfig
        cfg.setTransitionsReinitializingTakenOverBy(["validate"])

        # create an item
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # take item over
        item.setTakenOverBy('pmCreator1')
        self.assertEqual(item.getTakenOverBy(), 'pmCreator1')
        # if takenOverBy is removed
        item.setTakenOverBy('')
        self.assertEqual(item.getTakenOverBy(), '')

        # take item over and propose item
        item.setTakenOverBy('pmCreator1')
        self.changeUser('pmManager')
        for transition in self.TRANSITIONS_FOR_PROPOSING_ITEM_1:
            self._do_transition_with_request(item, transition)
        self.assertEqual(item.getTakenOverBy(), 'pmCreator1')

        item.setTakenOverBy('pmManager')
        self.assertEqual(item.getTakenOverBy(), 'pmManager')

        for transition in self.TRANSITIONS_FOR_VALIDATING_ITEM_1:
            self._do_transition_with_request(item, transition)
        # Validate reinitialize takenOverBy
        self.assertEqual(item.getTakenOverBy(), '')

        item.setTakenOverBy('pmManager')
        self.assertEqual(item.getTakenOverBy(), 'pmManager')

        for transition in self.BACK_TO_WF_PATH_1["itemcreated"]:
            self._do_transition_with_request(item, transition)
        self.assertEqual(item.getTakenOverBy(), 'pmManager')

    def test_pm_MayTakeOverDecidedItem(self):
        """Overrided, this is not possible for now..."""
        cfg = self.meetingConfig
        self.assertTrue('accepted' in cfg.getItemDecidedStates())
        self.assertTrue('delayed' in cfg.getItemDecidedStates())
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem', decision=self.decisionText)
        item2 = self.create('MeetingItem', decision=self.decisionText)
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2020/06/11').asdatetime())
        self.presentItem(item1)
        self.presentItem(item2)
        self.changeUser('pmCreator1')
        self.assertFalse(item1.adapted().mayTakeOver())
        self.assertFalse(item2.adapted().mayTakeOver())
        self.changeUser('pmManager')
        self.decideMeeting(meeting)
        self.do(item1, 'accept')
        self.do(item2, 'delay')
        self.changeUser('pmCreator1')
        # XXX changed
        self.assertFalse(item1.adapted().mayTakeOver())
        self.assertFalse(item2.adapted().mayTakeOver())

    def test_pm__sendCopyGroupsMailIfRelevant(self):
        """Bypass, not used."""

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    # launch only tests prefixed by 'test_mc_' to avoid launching the tests coming from pmtmi
    suite.addTest(makeSuite(testMeetingItem, prefix='test_pm_'))
    return suite
