# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest2 as unittest

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, setRoles, login

from lxml import etree

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class RSSViewTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Document',
                                  'page1', title="Collection Test Page")
        self.folder.invokeFactory('Collection',
                                  'collection1')
        self.collection = aq_inner(self.folder['collection1'])
        self.collection.query = query
        self.request.set('URL', self.collection.absolute_url())
        self.request.set('ACTUAL_URL', self.collection.absolute_url())
        # We need to enable syndication globally.
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        settings.allowed = True
        settings.default_enabled = True

    def assertIsValidRSS(self, rss):
        # XXX: We might want to validate against a DTD or RelaxNG schema here.
        #schema = etree.XMLSchema(schema_root)
        #parser = etree.XMLParser(dtd_validation=True,schema=schema)
        if isinstance(rss, unicode):
            rss = rss.encode("utf-8")
        parser = etree.XMLParser()
        return etree.fromstring(rss, parser)

    def test_view(self):
        view = self.collection.restrictedTraverse('@@RSS')
        html = view()
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue("Collection Test Page" in html)

    def test_view_is_valid(self):
        view = self.collection.restrictedTraverse('@@RSS')
        result = self.assertIsValidRSS(view())
        self.assertTrue("Collection Test Page" in etree.tostring(result))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
