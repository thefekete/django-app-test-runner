#!/usr/bin/env python

import os
import sys

from optparse import OptionParser

from django.conf import settings
from django.core.management import call_command


def main():
    """
    This main script of the django-app-test-runner package enables
    standalone testing (and thus development) of a Django app, by
    bootstrapping a Django environment around the app.  You can
    thereby work on a Django app outside the scope of any single
    particular Django site/project.

    You must have the Django package on the PYTHONPATH prior to
    running this script.  Then after installation of the
    django-app-test-runner package via setup.py or pip, this script
    should be in your (virtualenv) bin/ directory and you can use it
    at the command-line.  For example:

        app-test-runner <path-to-app>

    You can - and probably should - specify a settings file for
    testing the app, e.g. if your app has any dependencies at all
    beyond the default INSTALLED_APPS below, or varies in any way from
    the default settings of this script below.  Just run,

        app-test-runner <path-to-app> -s <path-to-app-testing-settings-file>

    By default this script will use SQLite and an in-memory
    database. If you are using Python >= 2.5 it should 'just work.'
    """
    parser = OptionParser()
    parser.add_option(
        "-s",
        action="store",
        default=None,
        dest="settings_file",
        help="Use the app settings FILE, instead of defaults.",
        metavar="FILE")
    options, args = parser.parse_args()

    # The app's location must be present in args:
    try:
        app_path = args[0]
    except IndexError:
        print "You did not provide an app path."
        raise SystemExit
    else:
        if app_path.endswith("/"):
            app_path = app_path[:-1]
        parent_dir, app_name = os.path.split(app_path)
        sys.path.insert(0, parent_dir)

    # Setup default settings to be used for testing the app. Remember,
    # for any significant settings different from the below defaults,
    # you should create a separate settings file for testing, and
    # specify it with the -s command-line parameter, per the docstring
    # above.
    test_settings_dict = {
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ""}},
        "SITE_ID": 1,
        "ROOT_URLCONF": "",
        "TEMPLATE_LOADERS": (
            "django.template.loaders.filesystem.load_template_source",
            "django.template.loaders.app_directories.load_template_source",
            ),
        "TEMPLATE_DIRS": (
            os.path.join(os.path.dirname(__file__), "templates"),
            ),
        "INSTALLED_APPS": (
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            app_name)}

    # If a settings file was specified, use that instead:
    if options.settings_file:
        import imp
        given_settings = imp.load_source(
            'foo',  # This arg not needed afterward.
            os.path.normpath(os.path.expanduser(options.settings_file)))
        for key in given_settings.__dict__.keys():
            if key[:2] != '__':
                test_settings_dict[key] = given_settings.__dict__[key]
    settings.configure(**test_settings_dict)
    call_command("test", app_name)  # Only test the app, not dependencies.

if __name__ == "__main__":
    main()
