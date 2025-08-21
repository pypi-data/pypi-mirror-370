Products.MeetingSeraing Changelog
=================================

4.2.12 (2025-08-20)
-------------------

- Fix an issue in `SeraingInsertBarcodeView.may_insert_barcode`.
  [aduchene]


4.2.11 (2025-08-19)
-------------------

- Fix `meetingitem_view.pt`.
  [aduchene]
- Fix an issue in `SeraingInsertBarcodeView.may_insert_barcode` when context was an Annex.
  [aduchene]

4.2.10 (2025-05-26)
-------------------

- Adapted `adapters.CUSTOM_RETURN_TO_PROPOSING_GROUP_MAPPINGS`.
  [aduchene]
- Add new helper methods used in pod templates.
  [aduchene]
- Fixed various things related to a new validation level 'proposed to director'.
  [aduchene]

4.2.9 (2024-06-21)
------------------

- Fixed `meetingitem_view.pt`.
  [aduchene]

4.2.8 (2024-03-29)
------------------

- Add missing import in adapters.py.
  [aduchene]

4.2.7 (2024-03-27)
------------------

- Fixed issue with dgNote and pvNote field.
  [aduchene]
- Fixed POD templates `deliberation.odt`, `MeetingItem.getCertifiedSignatures`
  is no more an adaptable method (removed `.adapted()`).
  [gbastien]
- Adapted test regarding removal of `MeetingConfig.listWorkflowAdaptations`.
  [aduchene]
- Move inAndOutMoves field to collapsible assembly zone.
  [aduchene]
- Adapted mayDelete for MeetingManager.
  [aduchene]

4.2.6 (2024-01-09)
------------------

- Fixed issue if 'propose' transition doesn't exist - SUP-33869.
  [aduchene]

4.2.5 (2024-01-09)
------------------

- Fixed typo in translation file.
  [aduchene]
- Adapt meetingitem_edit.pt to handle committees.
  [aduchene]

4.2.4 (2024-01-09)
------------------

- Delayed item is now duplicated in 'proposed' state - SUP-33869.
  [aduchene]

4.2.3 (2023-12-21)
------------------

- Removed unnecessary leading icons.
  [aduchene]
- Add missing translations.
  [aduchene]
- Fixed a bad import in `SeraingInsertBarcodeView.may_insert_barcode`.
  [aduchene]
- Add a simple view to the meeting to ease copy and paste.
  [aduchene]

4.2.2 (2023-09-14)
------------------

- `update_item_references` is now usable by powereditors.
  [aduchene]
- Adapted code as field `MeetingConfig.useCopies` was removed.
  [gbastien]
- Keep WFA `meeting_remove_global_access` that is required to use functionnality
  `MeetingConfig.usingGroups`.
  [gbastien]
- MeetingManager may now edit MeetingManager fields in 'accepted', 'accepted_but_modified', 'delayed' states.
  [aduchene]
- MeetingManager may delete every not decided items, ignoring the WFA 'only_creators_may_delete'.
  [aduchene]

4.2.1 (2023-08-23)
------------------

- Fixed bad import.
  [aduchene]

4.2.0 (2023-07-06)
------------------

- `MeetingConfig.listEveryItemTransitions` was renamed to `MeetingConfig.listItemTransitions`.
  [gbastien]
- Fixed translation of `Data that will be used on new item` on `meetingitem_view.pt`.
  [gbastien]
- `MeetingItemWorkflowActions._latePresentedItem` was renamed to
  `MeetingItemWorkflowActions._latePresentedItemTransitions` and only needs to
  return a tuple of transitions to trigger on the item.
  [gbastien]

4.2.0b5 (2023-04-26)
--------------------

- Restore mayBackToMeeting and adapt it to use CUSTOM_RETURN_TO_PROPOSING_GROUP_MAPPINGS.
  [aduchene]

4.2.0b4 (2023-04-26)
--------------------

- Remove mayBackToMeeting as it is now useless.
  [aduchene]

4.2.0b3 (2023-03-30)
--------------------

- Updated `meetingitem_view` regarding changes in `PloneMeeting`
  (votesResult after motivation or after decision).
  [gbastien]
- Adapted code regarding removal of `MeetingConfig.useGroupsAsCategories`.
  [gbastien]

4.2.0b2 (2022-12-14)
--------------------

- Fixed condition on interventions field.
  [aduchene]

4.2.0b1 (2022-12-14)
--------------------

- Removed unnecessary files.
  [aduchene]
- Power editors are Contributor on return_to* states and changed may_store_podtemplate_as_annex accordingly.
  [aduchene]
- Restore interventions field in meetingitem_view.
  [aduchene]

4.2.0a9 (2022-12-09)
--------------------

- Fixed an issue where MeetingManager may edit closed state variants.
  [aduchene]
- Apply correct local roles for MeetingManager when seraing_add_item_closed_states is enabled.
  [aduchene]
- Renamed `seraing_add_item_closed_state` to `seraing_add_item_closed_states`.
  [aduchene]
- Migrate sections to committees.
  [aduchene]

4.2.0a8 (2022-09-16)
--------------------

- Take into account batch action transition when setting takenOverBy.
  [aduchene]
- Fixed WFA `seraing_powereditors` as wrong permission_roles was applied (again).
  [aduchene]

4.2.0a7 (2022-09-15)
--------------------

- Fixed WFA `seraing_powereditors` as wrong permission_roles was applied.
  [aduchene]

4.2.0a6 (2022-09-15)
--------------------

- Power editors may now add decision_annexe on closed item states.
  [aduchene]
- Refactored `POWEREDITORS_EDITABLE_STATES` to `POWEREDITORS_LOCALROLE_STATES`
  to have a mapping of local roles to apply at a given state.
  [aduchene]


4.2.0a5 (2022-09-02)
--------------------

- Power editors may edit presented state.
  [aduchene]
- Power editors may edit marginalNotes when item is in closed state.
  [aduchene]
- Removed `ecolesanit.py`.
  [aduchene]


4.2.0a4 (2022-08-30)
--------------------

- Power editors may now add a barcode to annexes.
  [aduchene]
- Fixed an issue where power editors saw 'store podtemplate as annex' in the wrong states.
  [aduchene]


4.2.0a3 (2022-08-23)
--------------------

- Fixed a bug when an item was late (`_latePresentedItem`).
  [aduchene]
- Fixed broken tests as PowerEditors is now a WFA.
  [aduchene]

4.2.0a2 (2022-08-19)
--------------------

- Fixed issues with back transitions for WFA seraing_validated_by_DG.
  [aduchene]
- Add missing WFA translations.
  [aduchene]
- Refactored PowerEditors feature. Now it's a WFA's and PowerEditors may store item podtemplate as annex (SUP-16787).
  [aduchene]
- marginalNotes are now highlighted and displayed at the top when completed (SUP-16802).
  [aduchene]
- Renamed `returned_to_advise` to `seraing_returned_to_advise`.
  [aduchene]
- Improved demo import_data to ease testing.
  [aduchene]
- Add missing icons back.
  [aduchene]

4.2.0a1 (2022-08-11)
--------------------

- Compatible for PloneMeeting 4.2.
  [aduchene]
- meetingseraing_workflow and meetingitemseraing_workflow are now deprecated.
  Use PloneMeeting's default WF with itemWFValidationLevels set accordingly.
  [aduchene]
- Add two new WFA to have feature parity between old seraing_workflow and PloneMeeting's default WF.
  [aduchene]
- Adapted PowerEditors feature to use local roles correctly.
  [aduchene]
- Fixed broken tests.
  [aduchene]

4.1.6 (2022-04-01)
------------------

- Fixed typo getMeetingStatesAcceptingItem -> getMeetingStatesAcceptingItems.
  [aduchene]
- Fixed wrong permissions in `patch_return_to_proposing_group_with_last_validation`.
  [aduchene]


4.1.5 (2022-03-09)
------------------

- Fixed issue with mayPresent.
  [aduchene]
- SUP-18390: Fixed incorrect permissions in return_to_proposing_group_with_last_validation WFA
  [aduchene]


4.1.4 (2021-04-07)
------------------

- SUP-16268: refactored takenOverBy feature. Now takenOverBy is kept between transitions except for those defined in `MeetingConfig.transitionsReinitializingTakenOverBy`.
  [aduchene]


4.1.3 (2020-12-18)
------------------

- Renamed `testSearches.test_pm_SearchItemsToCorrectToValidateOfHighestHierarchicLevel`
  to `testSearches.test_pm_SearchItemsToCorrectToValidateOfHighestHierarchicLevel`
  as it was renamed in `Products.PloneMeeting` and we bypass it this way.
  [gbastien]
- Changed setTakenOverBy as it should not reinit itself
  when transitionning from itemfrozen to accepted. SUP-15933
  [aduchene]

4.1.2 (2020-10-22)
------------------

- Updated sections label to commissions label. SUP-15177
  [aduchene]


4.1.1 (2020-10-12)
------------------

- Fixed MANIFEST.in
  [aduchene]


4.1 (2020-10-12)
----------------
- Compatible for PloneMeeting 4.1
- Added two new mail's notification:
    - When item is delayed, send mail to service head;
    - When advice is added or modified, send mail to service head.
- Keep "Taken over" for severals states
- Fix sendMailIfRelevant.
  [odelaere]
- Adapted code and tests regarding DX meetingcategory.
  [gbastien]
- Adapted templates regarding last changes in Products.PloneMeeting.
  [gbastien]

4.02 (2019-05-02)
-----------------
- Change rules for keeping annexes and decision's annexes

4.0 (2017-01-01)
----------------
- Adapted workflows to define the icon to use for transitions
- Removed field MeetingConfig.cdldProposingGroup and use the 'indexAdvisers' value
  defined in the 'searchitemswithfinanceadvice' collection to determinate what are
  the finance adviser group ids
- 'getEchevinsForProposingGroup' does also return inactive MeetingGroups so when used
  as a TAL condition in a customAdviser, an inactive MeetingGroup/customAdviser does
  still behaves correctly when updating advices
- Use ToolPloneMeeting.performCustomWFAdaptations to manage our own WFAdaptation
  (override of the 'no_publication' WFAdaptation)
- Adapted tests, keep test... original PM files to overrides original PM tests and
  use testCustom... for every other tests, added a testCustomWorkflow.py
- Now that the same WF may be used in several MeetingConfig in PloneMeeting, removed the
  2 WFs meetingcollege and meetingcouncil and use only one meetingseraing where wfAdaptations
  'no_publication' and 'no_global_observation' are enabled
- Added profile 'financesadvice' to manage advanced finances advice using a particular
  workflow and a specific meetingadvicefinances portal_type
- Adapted profiles to reflect imio.annex integration
- Added new adapter method to ease financial advices management while generating documents
  printFinanceAdvice(self, case)
- Added parameter 'excludedGroupIds' to getPrintableItems and getPrintableItemsByCategory
- MeetingObserverLocal has every View-like permissions in every states

3.3 (2015-04-07)
----------------
- Updated regarding changes in PloneMeeting
- Removed profile 'examples' that loaded examples in english
- Removed dependencies already defined in PloneMeeting's setup.py
- Added parameter MeetingConfig.initItemDecisionIfEmptyOnDecide that let enable/disable
  items decision field initialization when meeting 'decide' transition is triggered
- Added MeetingConfig 'CoDir'
- Added MeetingConfig 'CA'
- Field 'MeetingGroup.signatures' was moved to PloneMeeting

3.2.0.1 (05-09-2014)
--------------------
- Original release
