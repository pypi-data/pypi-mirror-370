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
        if self.tool.getEnableScanDocs():
            # bypass for 'Manager'
            if self.tool.isManager(realManagers=True):
                res = True
            else:
                cfg = self.tool.getMeetingConfig(self.context)
                ctx = self.context
                if IAnnex.providedBy(self.ctx):
                    ctx = ctx.aq_parent
                isManagerOrPowerEditor = self.tool.isManager(cfg) or ctx.adapted().powerEditorEditable()
                barcode_inserted = getattr(self.context, "scan_id", False)
                if isManagerOrPowerEditor and \
                   not barcode_inserted and \
                   _checkPermission(ModifyPortalContent, self.context):
                    res = True
        return res
