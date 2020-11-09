# encoding: utf-8

from ckan.plugins import toolkit
import ckan.model as model
from ckan.tests import factories
import logging
from ckanext.pages import db
import pytest

log = logging.getLogger(__name__)


@pytest.fixture
def initdb():
    if db.pages_table is None:
        db.init_db(model)


@pytest.mark.ckan_config(u'ckan.plugins', u'pages')
@pytest.mark.usefixtures(u'with_plugins', u'with_request_context',
                         u'app', u'clean_db', u'initdb')
class TestPages(object):

    def test_create_page(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}

        response = app.post(
            url=toolkit.url_for('pages_edit', page='/test_page'),
            params={
                'title': 'Page Title',
                'name': 'page_name',
                'private': False,
            },
            extra_environ=env,
            follow_redirects=True
        )
        assert '<h1 class="page-heading">Page Title</h1>' in response.body

    @pytest.mark.ckan_config(u'ckanext.pages.allow_html', True)
    def test_rendering_with_html_allowed(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        response = app.post(
            url=toolkit.url_for('pages_edit', page='/test_html_page'),
            params={
                'title': 'Allowed',
                'name': 'page_html_allowed',
                'content': '<a href="/test">Test Link</a>',
                'private': False,
            },
            extra_environ=env,
            follow_redirects=True
        )
        assert '<h1 class="page-heading">Allowed</h1>' in response.body
        if toolkit.check_ckan_version(min_version='2.3'):
            assert '<a href="/test">Test Link</a>' in response.body
        else:
            assert 'Test Link' in response.body

    @pytest.mark.ckan_config(u'ckanext.pages.allow_html', False)
    def test_rendering_with_html_disallowed(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        response = app.post(
            url=toolkit.url_for('pages_edit', page='/test_html_page'),
            params={
                'title': 'Disallowed',
                'name': 'page_html_disallowed',
                'content': '<a href="/test">Test Link</a>',
                'private': False,
            },
            extra_environ=env,
            follow_redirects=True
        )
        assert '<h1 class="page-heading">Disallowed</h1>' in response.body
        assert 'Test Link' in response.body
        assert '<a href="/test">Test Link</a>' not in response.body

    def test_pages_index(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        url = toolkit.url_for('pages_index')
        response = app.get(url, status=200, extra_environ=env)
        assert '<h2>Pages</h2>' in response.body
        assert 'Add page</a>' in response.body

    def test_blog_index(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        url = toolkit.url_for('blog_index')
        response = app.get(url, status=200, extra_environ=env)
        assert '<h2>Blog</h2>' in response.body
        assert 'Add Article</a>' in response.body

    def test_organization_pages_index(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        org = factories.Organization()
        url = toolkit.url_for('organization_pages_index', id=org['id'])
        response = app.get(url, status=200, extra_environ=env)
        assert '<h2>Pages</h2>' in response.body
        assert 'Add page</a>' in response.body

    def test_group_pages_index(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        group = factories.Group()
        url = toolkit.url_for('group_pages_index', id=group['id'])
        response = app.get(url, status=200, extra_environ=env)
        assert '<h2>Pages</h2>' in response.body
        assert 'Add page</a>' in response.body

    def test_unicode(self, app):
        admin_user = factories.Sysadmin()
        env = {'REMOTE_USER': admin_user['name'].encode('ascii')}
        response = app.post(
            url=toolkit.url_for('pages_edit', page='/test_unicode_page'),
            params={
                'title': u'Tïtlé'.encode('utf-8'),
                'name': 'page_unicode',
                'content': u'Çöñtéñt'.encode('utf-8'),
                'order': 1,
                'private': False,
            },
            extra_environ=env,
            follow_redirects=True
        )
        body = response.body.decode('utf-8')

        assert u'<title>Tïtlé - CKAN</title>' in body
        assert u'<a href="/en/pages/page_unicode">Tïtlé</a>' in body
        assert u'<h1 class="page-heading">Tïtlé</h1>' in body
        assert u'<p>Çöñtéñt</p>' in body
