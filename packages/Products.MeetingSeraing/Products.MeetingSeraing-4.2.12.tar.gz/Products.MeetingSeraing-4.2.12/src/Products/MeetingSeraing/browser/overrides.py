# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#
from imio.annex.content.annex import IAnnex
from imio.zamqp.pm.browser.views import InsertBarcodeView
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission


class SeraingInsertBarcodeView(InsertBarcodeView):
    """ """

    def may_insert_barcode(self):
        """By default, must be (Meeting)Manager to include barcode and
           barcode must not be already inserted."""
        res = False
        if self.tool.isManager(realManagers=True):
            res = True
        if self.tool.getEnableScanDocs():
            cfg = self.tool.getMeetingConfig(self.context)
            # Special for MeetingSeraing: allow power editors to insert barcode
            isPowerEditorEditable = hasattr(self.context.adapted(), "powerEditorEditable") and self.context.adapted().powerEditorEditable()
            isManagerOrPowerEditor = self.tool.isManager(cfg) or isPowerEditorEditable
            # is manager and no barcode already inserted and element still editable
            if (isManagerOrPowerEditor or cfg.getAnnexEditorMayInsertBarcode()) and \
               not self.context.scan_id and \
               _checkPermission(ModifyPortalContent, self.context):
                res = True
        return res
