# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from plone import api
from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200
from Products.MeetingSeraing.config import SERAING_ITEM_WF_VALIDATION_LEVELS

import logging


logger = logging.getLogger('MeetingSeraing')


class Migrate_To_4200(MCMigrate_To_4200):

    def _hook_custom_meeting_to_dx(self, old, new):
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(new)
        new_committees = []
        for section in old.sections:
            label = old.adapted().listSections().getValue(section['name_section'])
            if not any(c['label'] == label for c in cfg.getCommittees()):
                cfg.setCommittees(
                    cfg.getCommittees() +
                    ({
                         'acronym': '',
                         'auto_from': [],
                         'default_assembly': '',
                         'default_attendees': [],
                         'default_place': '',
                         'default_signatories': [],
                         'default_signatures': '',
                         'enabled': '1',
                         'label': label,
                         'supplements': '0',
                         'using_groups': []
                     },))

            row_id = [c['row_id'] for c in cfg.getCommittees() if c['label'] == label][0]
            try:
                date = datetime.strptime(section['date_section'], "%d/%m/%Y")
            except ValueError:
                date = datetime.fromtimestamp(0)
            new_committees.append({
                'assembly': None,
                'attendees': [],
                'committee_observations': None,
                'convocation_date': None,
                'date': date,
                'place': u'',
                'row_id': row_id,
                'signatories': [],
                'signatures': None})
        new.committees = new_committees

    def _fixUsedWFs(self):
        """meetingseraing_workflow/meetingitemseraing_workflow do not exist anymore,
           we use meeting_workflow/meetingitem_workflow."""
        logger.info("Adapting 'meetingWorkflow/meetingItemWorkflow' for every MeetingConfigs...")
        for cfg in self.tool.objectValues('MeetingConfig'):
            if cfg.getMeetingWorkflow() == 'meetingseraing_workflow':
                cfg.setMeetingWorkflow('meeting_workflow')
            if cfg.getItemWorkflow() == 'meetingitemseraing_workflow':
                cfg.setItemWorkflow('meetingitem_workflow')
        # delete old unused workflows
        wfs_to_delete = [wfId for wfId in self.wfTool.listWorkflows()
                         if any(x in wfId for x in (
                            'meetingseraing_workflow',
                            'meetingitemseraing_workflow',))]
        if wfs_to_delete:
            self.wfTool.manage_delObjects(wfs_to_delete)
        logger.info('Done.')

    def _get_wh_key(self, itemOrMeeting):
        """Get workflow_history key to use, in case there are several keys, we take the one
           having the last event."""
        keys = itemOrMeeting.workflow_history.keys()
        if len(keys) == 1:
            return keys[0]
        else:
            lastEventDate = DateTime('1950/01/01')
            keyToUse = None
            for key in keys:
                if itemOrMeeting.workflow_history[key][-1]['time'] > lastEventDate:
                    lastEventDate = itemOrMeeting.workflow_history[key][-1]['time']
                    keyToUse = key
            return keyToUse

    def _adaptWFHistoryForItemsAndMeetings(self):
        """We use PM default WFs, no more meeting(item)Seraing_workflow..."""
        logger.info('Updating WF history items and meetings to use new WF id...')
        catalog = api.portal.get_tool('portal_catalog')
        for cfg in self.tool.objectValues('MeetingConfig'):
            # this will call especially part where we duplicate WF and apply WFAdaptations
            cfg.registerPortalTypes()
            for brain in catalog(portal_type=(cfg.getItemTypeName(), cfg.getMeetingTypeName())):
                itemOrMeeting = brain.getObject()
                itemOrMeetingWFId = self.wfTool.getWorkflowsFor(itemOrMeeting)[0].getId()
                if itemOrMeetingWFId not in itemOrMeeting.workflow_history:
                    wf_history_key = self._get_wh_key(itemOrMeeting)
                    itemOrMeeting.workflow_history[itemOrMeetingWFId] = \
                        tuple(itemOrMeeting.workflow_history[wf_history_key])
                    del itemOrMeeting.workflow_history[wf_history_key]
                    # do this so change is persisted
                    itemOrMeeting.workflow_history = itemOrMeeting.workflow_history
                else:
                    # already migrated
                    break
        logger.info('Done.')

    def _doConfigureItemWFValidationLevels(self, cfg):
        """Apply correct itemWFValidationLevels and fix WFAs."""
        stored_itemWFValidationLevels = getattr(cfg, 'itemWFValidationLevels', [])
        if not stored_itemWFValidationLevels:
            cfg.setItemWFValidationLevels(SERAING_ITEM_WF_VALIDATION_LEVELS)

        # returned_to_advise has been renamed to seraing_returned_to_advise
        if 'returned_to_advise' in cfg.getWorkflowAdaptations():
            cfg.setWorkflowAdaptations(tuple(
                wfa for wfa in cfg.getWorkflowAdaptations() if wfa != "returned_to_advise"
            ) + ("seraing_returned_to_advise",))


        if 'patch_return_to_proposing_group_with_last_validation' in cfg.getWorkflowAdaptations():
            workflowAdaptations = list(cfg.getWorkflowAdaptations())
            workflowAdaptations.remove('patch_return_to_proposing_group_with_last_validation')
            cfg.setWorkflowAdaptations(
                tuple(workflowAdaptations)
            )

        if 'seraing_add_item_closed_states' not in cfg.getWorkflowAdaptations():
            cfg.setWorkflowAdaptations(tuple(("seraing_add_item_closed_states",) + cfg.getWorkflowAdaptations()))
        if 'seraing_validated_by_DG' not in cfg.getWorkflowAdaptations():
            cfg.setWorkflowAdaptations(tuple(("seraing_validated_by_DG",) + cfg.getWorkflowAdaptations()))

    def run(self,
            profile_name=u'profile-Products.MeetingSeraing:default',
            extra_omitted=[]):
        self._fixUsedWFs()
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)
        self._adaptWFHistoryForItemsAndMeetings()

        logger.info('Done migrating to MeetingSeraing 4200...')


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Change MeetingConfig workflows to use meeting_workflow/meetingitem_workflow;
       2) Call PloneMeeting migration to 4200 and 4201;
       3) In _after_reinstall hook, adapt items and meetings workflow_history
          to reflect new defined workflow done in 1);
       4) Add new searches.
    '''
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
