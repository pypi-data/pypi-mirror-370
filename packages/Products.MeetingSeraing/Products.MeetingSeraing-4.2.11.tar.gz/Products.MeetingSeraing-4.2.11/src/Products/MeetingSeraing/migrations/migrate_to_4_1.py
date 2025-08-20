# -*- coding: utf-8 -*-

from Products.GenericSetup.tool import DEPENDENCY_STRATEGY_NEW
from Products.MeetingCommunes.migrations.migrate_to_4_1 import Migrate_To_4_1 as MCMigrate_to_4_1


class Migrate_To_4_1(MCMigrate_to_4_1):

    def run(self):
        # reapply the actions.xml of collective.iconifiedcategory
        self.ps.runImportStepFromProfile('profile-collective.iconifiedcategory:default', 'actions')
        super(Migrate_To_4_1, self).run(extra_omitted=['Products.MeetingSeraing:default'])
        self.reinstall(profiles=[u'profile-Products.MeetingSeraing:default'],
                       ignore_dependencies=True,
                       dependency_strategy=DEPENDENCY_STRATEGY_NEW)


# The migration function -------------------------------------------------------
def migrate(context):
    """This migration function:

       1) Execute Products.MeetingCommunes migration.
    """
    migrator = Migrate_To_4_1(context)
    migrator.run()
    migrator.finish()
