from Products.Five import BrowserView


class MeetingSimpleView(BrowserView):
    """Simple view of a meeting."""

    def get_grouped_items(self):
        view = self.context.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        items = self.context.get_items(ordered=True)
        itemUids = [anItem.UID() for anItem in items]
        return helper.get_grouped_items(itemUids, list_types=[], group_by=["proposingGroup"])
