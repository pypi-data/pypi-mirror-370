#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.event` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import os
import unittest
from unittest.mock import MagicMock, Mock, call

from ransack import get_values

import mentat.const
import mentat.idea.internal
import mentat.reports.event
import mentat.reports.utils
import mentat.services.eventstorage
import mentat.services.sqlstorage
from mentat.datatype.sqldb import (
    DetectorModel,
    EventClassModel,
    EventClassState,
    EventReportModel,
    FilterModel,
    GroupModel,
    NetworkModel,
    SettingsReportingModel,
)
from mentat.reports.data import ReportingProperties

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------

REPORTS_DIR = "/var/tmp"


class TestMentatReportsEvent(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.event` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    ideas_raw = [
        {
            "Format": "IDEA0",
            "ID": "msg01",
            "DetectTime": "2018-01-01T12:00:00Z",
            "Category": ["Fraud.Phishing"],
            "Description": "Synthetic example 01",
            "Source": [
                {
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25", "10.0.0.1"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                    "Proto": ["ssh"],
                }
            ],
            "Target": [
                {
                    "IP4": ["10.2.2.0/24"],
                    "IP6": ["2001:ffff::ff00:42:0/112"],
                    "Proto": ["https"],
                }
            ],
            "Node": [{"Name": "org.example.kippo_honey", "SW": ["Kippo"]}],
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "EventClass": "fraud-phishing",
                "EventSeverity": "low",
                "TargetClass": "fraud-phishing-target",
                "TargetSeverity": "medium",
                "TargetAbuses": ["abuse@cesnet.cz"],
            },
        },
        {
            "Format": "IDEA0",
            "ID": "msg02",
            "DetectTime": "2018-01-01T13:00:00Z",
            "Category": ["Recon.Scanning"],
            "Description": "Synthetic example 02",
            "ConnCount": 42,
            "Source": [
                {
                    "IP4": [
                        "10.0.1.2-10.0.1.5",
                        "10.0.0.0/25",
                        "10.0.0.0/22",
                        "10.0.2.1",
                    ],
                    "IP6": ["2002:db8::ff00:42:0/112"],
                    "Port": [22],
                }
            ],
            "Target": [{"IP4": ["11.2.2.0/24"], "IP6": ["2004:ffff::ff00:42:0/112"]}],
            "Node": [{"Name": "org.example.dionaea", "SW": ["Dionaea"]}],
            "Note": "Test note containing ; CSV delimiter.",
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "EventClass": "recon-scanning",
                "EventSeverity": "low",
                "TargetClass": "recon-scanning-target",
                "TargetSeverity": "low",
                "TargetAbuses": ["abuse@cesnet.cz"],
            },
        },
    ]

    ideas_obj = list(map(mentat.idea.internal.Idea, ideas_raw))

    template_vars = {
        "report_access_url": "https://URL/view=",
        "contact_email": "EMAIL1",
        "admin_email": "EMAIL2",
    }

    def setUp(self):
        """
        Perform test case setup.
        """
        self.sqlstorage = mentat.services.sqlstorage.StorageService(
            url="postgresql://mentat:mentat@localhost/mentat_utest", echo=False
        )
        self.sqlstorage.database_drop()
        self.sqlstorage.database_create()

        self.eventstorage = mentat.services.eventstorage.EventStorageService(
            dbname="mentat_utest",
            user="mentat",
            password="mentat",
            host="localhost",
            port=5432,
        )
        self.eventstorage.database_drop()
        self.eventstorage.database_create()
        for event in self.ideas_obj:
            event["_Mentat"]["StorageTime"] = datetime.datetime.utcnow()
            self.eventstorage.insert_event(event)

        group = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")
        groups_dict = {"abuse@cesnet.cz": group}

        FilterModel(
            group=group,
            name="FLT1",
            source_based=True,
            type="basic",
            filter='Node.Name contains "org.example.kippo_honey"',
            description="DESC1",
            enabled=True,
        )
        FilterModel(
            group=group,
            name="FLT2",
            source_based=True,
            type="basic",
            filter="Source.IP4 in [10.0.0.0/24]",
            description="DESC2",
            enabled=True,
        )
        FilterModel(
            group=group,
            name="FLT3",
            source_based=True,
            type="basic",
            filter="Source.IP4 IN [10.0.1.0/28]",
            description="DESC3",
            enabled=True,
        )
        NetworkModel(group=group, netname="UNET1", source="manual", network="10.0.0.0/8")
        SettingsReportingModel(group=group)

        det1 = DetectorModel(name="org.example.kippo_honey", source="manual", credibility=0.72, hits=12)
        det2 = DetectorModel(name="org.example.dionaea", source="manual", credibility=0.36, hits=121)

        ec1 = EventClassModel(
            name="recon-scanning",
            source_based=True,
            label_en="The machine performed some type of active scanning.",
            label_cz="Stroj se pokoušel o nějakou formu aktivního skenování.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning",
            displayed_main=["ConnCount", "FlowCount", "protocols", "Ref"],
            displayed_source=["Port"],
            displayed_target=["Port", "ips", "Hostname"],
            rule="Category in ['Recon.Scanning']",
            severity="low",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        ec2 = EventClassModel(
            name="fraud-phishing",
            source_based=True,
            label_en="Phishing attempt.",
            label_cz="Pokus o phishing.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/fraud-phishing",
            displayed_main=[],
            displayed_source=[],
            displayed_target=[],
            rule="Category in ['Fraud.Phishing']",
            severity="medium",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        ec3 = EventClassModel(
            name="recon-scanning-target",
            source_based=False,
            label_en="Your IP range was scanned.",
            label_cz="Váš IP rozsah byl skenován.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning-target",
            displayed_main=["ConnCount", "FlowCount", "protocols", "Ref"],
            displayed_source=["ips", "Port"],
            displayed_target=["Port", "ips", "Hostname"],
            rule="Category in ['Recon.Scanning']",
            severity="low",
            subclassing="",
            state=EventClassState.ENABLED,
        )

        for obj in [group, det1, det2, ec1, ec2, ec3]:
            self.sqlstorage.session.add(obj)
        self.sqlstorage.session.commit()

        self.reporting_settings = mentat.reports.utils.ReportingSettings(group, self.sqlstorage)
        settings_dict = {"abuse@cesnet.cz": self.reporting_settings}

        def lookup_mock(src, getall=False):
            if str(src).startswith("10."):
                return [{"abuse_group": "abuse@cesnet.cz", "is_base": False}]
            return []

        whoismodule_mock = mentat.services.whois.WhoisModule()
        whoismodule_mock.lookup = MagicMock(side_effect=lookup_mock)

        self.reporter = mentat.reports.event.EventReporter(
            Mock(),
            REPORTS_DIR,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../conf/templates/reporter")),
            [],
            "en",
            "UTC",
            self.eventstorage,
            self.sqlstorage,
            mailer=None,
            groups_dict=groups_dict,
            settings_dict=settings_dict,
            whoismodule=whoismodule_mock,
        )

    def tearDown(self):
        self.sqlstorage.session.close()
        self.sqlstorage.database_drop()
        self.eventstorage.database_drop()

    def test_01_save_to_json_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_json_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = "utest-security-report.json"
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_json_files(  # pylint: disable=locally-disabled,protected-access
                self.ideas_obj, report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

        # Test saving file with timestamp information.
        report_file = "utest-security-report-M20180726SL-HT9TC.json"
        report_path = os.path.join(REPORTS_DIR, "20180726", report_file)

        self.assertEqual(
            self.reporter._save_to_json_files(  # pylint: disable=locally-disabled,protected-access
                self.ideas_obj, report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

    def test_02_save_to_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = "utest-security-report.txt"
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_files(  # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT", report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

        # Test saving file with timestamp information.
        report_file = "utest-security-report-M20180726SL-HT9TC.txt"
        report_path = os.path.join(REPORTS_DIR, "20180726", report_file)

        self.assertEqual(
            self.reporter._save_to_files(  # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT", report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

    def test_03_filter_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.filter_events` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.sqlstorage.session.commit()
        reporting_properties = ReportingProperties(
            abuse_group, "low", datetime.datetime.now(), datetime.datetime.now(), is_target=False
        )

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, self.ideas_obj)
        self.assertEqual(fltlog, {"FLT1": 1, "FLT2": 1, "FLT3": 1})
        self.assertEqual(flt_cnt, 1)
        for events in aggr.values():
            self.assertEqual(len(events), 2)
        self.reporter.logger.assert_has_calls(
            [
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT1",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg01"),
                call.debug("Event matched filtering rules, all sources filtered"),
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT2",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg02"),
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT3",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg02"),
            ]
        )
        self.sqlstorage.session.commit()

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, self.ideas_obj)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == "FLT1").one()
        self.assertEqual(flt1.hits, 2)

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, self.ideas_obj)
        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, self.ideas_obj)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == "FLT1").one()
        self.assertEqual(flt1.hits, 4)

        self.assertEqual(len(list(aggr.values())), 1)
        aggr_value = list(aggr.values())[0]
        aggr_result = self.reporter.aggregate_events(aggr_value, False)
        self.assertEqual(sorted(aggr_result.keys()), ["recon-scanning"])
        self.assertEqual(list(aggr_result["recon-scanning"].keys()), ["10.0.2.1", "10.0.0.0/22"])

    def test_04_fetch_severity_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.fetch_severity_events` function.
        """
        self.maxDiff = None

        group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.sqlstorage.session.commit()

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg01", "msg02"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "medium",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg02"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "medium",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg01"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "high",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

    def test_06_render_report_summary(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_summary` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()

        report_txt = self.reporter.render_report(
            self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_SUMMARY),
            self.reporting_settings,
            self.template_vars,
            ["file1.json"],
        )
        if self.verbose:
            print("\n---\nSUMMARY REPORT IN EN:\n---\n")
            print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split("\n")[0], "Dear colleagues,")

        self.reporting_settings.locale = "cs"
        self.reporting_settings.timezone = "Europe/Prague"

        report_txt = self.reporter.render_report(
            self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_SUMMARY),
            self.reporting_settings,
            self.template_vars,
            ["file1.json"],
        )
        if self.verbose:
            print("\n---\nSUMMARY REPORT IN CS:\n---\n")
            print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split("\n")[0], "Vážení kolegové,")

    def test_07_render_report_extra(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_extra` function.
        """

        def render_extra_report(events, locale="en", timezone="UTC"):
            if locale:
                self.reporting_settings.locale = locale
            if timezone:
                self.reporting_settings.timezone = timezone

            mock_report = self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_EXTRA, events)
            self.sqlstorage.session.add(mock_report)
            report_txt = self.reporter.render_report(
                mock_report, self.reporting_settings, self.template_vars, "192.168.1.1"
            )
            if self.verbose:
                print(f"\n---\nEXTRA REPORT IN {locale or 'en'}:\n---\n")
                print(report_txt)
            return report_txt

        self.maxDiff = None
        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()

        report_txt_phishing_en = render_extra_report(self.ideas_obj[0:1])
        self.assertTrue(report_txt_phishing_en)
        self.assertEqual(report_txt_phishing_en.split("\n")[0], "Dear colleagues,")
        self.assertNotIn("Details from detector", report_txt_phishing_en)
        self.assertIn("[1] Phishing attempt.", report_txt_phishing_en)
        self.assertIn(
            "https://csirt.cesnet.cz/cs/services/eventclass/fraud-phishing",
            report_txt_phishing_en,
        )
        self.assertIn("First event:", report_txt_phishing_en)
        self.assertIn("2018-01-01 12:00:00 Z", report_txt_phishing_en)
        self.assertIn("10.0.0.1", report_txt_phishing_en)

        report_txt_phishing_cz = render_extra_report(self.ideas_obj[0:1], "cs", "Europe/Prague")
        self.assertTrue(report_txt_phishing_cz)
        self.assertEqual(report_txt_phishing_cz.split("\n")[0], "Vážení kolegové,")
        self.assertNotIn("Detaily z detektoru", report_txt_phishing_cz)
        self.assertIn("[1] Pokus o phishing.", report_txt_phishing_cz)
        self.assertIn(
            "https://csirt.cesnet.cz/cs/services/eventclass/fraud-phishing",
            report_txt_phishing_cz,
        )
        self.assertIn("První událost:", report_txt_phishing_cz)
        self.assertIn("2018-01-01 13:00:00 +01:00 (2018-01-01 12:00:00 Z)", report_txt_phishing_cz)
        self.assertIn("10.0.0.1", report_txt_phishing_cz)

        report_txt_scanning_en = render_extra_report(self.ideas_obj[1:2])
        self.assertTrue(report_txt_scanning_en)
        self.assertEqual(report_txt_scanning_en.split("\n")[0], "Dear colleagues,")
        self.assertIn(
            "[1] The machine performed some type of active scanning.",
            report_txt_scanning_en,
        )
        self.assertIn(
            "https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning",
            report_txt_scanning_en,
        )
        self.assertIn("First event:", report_txt_scanning_en)
        self.assertIn("2018-01-01 13:00:00 Z", report_txt_scanning_en)
        self.assertIn("10.0.2.1", report_txt_scanning_en)
        self.assertIn("Target IP addresses", report_txt_scanning_en)
        self.assertIn("11.2.2.0/24, 2004:ffff::ff00:42:0/112", report_txt_scanning_en)
        self.assertIn("Details from detector org.example.dionaea:", report_txt_scanning_en)
        self.assertIn("------------------------------------------------", report_txt_scanning_en)

        report_txt_scanning_cz = render_extra_report(self.ideas_obj[1:2], "cs", "Europe/Prague")
        self.assertTrue(report_txt_scanning_cz)
        self.assertEqual(report_txt_scanning_cz.split("\n")[0], "Vážení kolegové,")
        self.assertIn(
            "[1] Stroj se pokoušel o nějakou formu aktivního skenování.",
            report_txt_scanning_cz,
        )
        self.assertIn(
            "https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning",
            report_txt_scanning_cz,
        )
        self.assertIn("První událost:", report_txt_scanning_cz)
        self.assertIn("2018-01-01 13:00:00 Z", report_txt_scanning_cz)
        self.assertIn("10.0.2.1", report_txt_scanning_cz)
        self.assertIn("Cílové IP adresy", report_txt_scanning_cz)
        self.assertIn("11.2.2.0/24, 2004:ffff::ff00:42:0/112", report_txt_scanning_cz)
        self.assertIn("Detaily z detektoru org.example.dionaea:", report_txt_scanning_cz)
        self.assertIn("------------------------------------------------", report_txt_scanning_cz)

    def test_08_render_report_target(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_target` function.
        """
        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        mock_report = self._generate_mock_report(
            abuse_group,
            "low",
            mentat.const.REPORT_TYPE_TARGET,
            self.ideas_obj[1:2],
            True,
        )
        self.sqlstorage.session.add(mock_report)
        report_txt = self.reporter.render_report(
            mock_report, self.reporting_settings, self.template_vars, "192.168.1.1"
        )
        if self.verbose:
            print("\n---\nTARGET REPORT (en):\n---\n")
            print(report_txt)

        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split("\n")[0], "Dear colleagues,")
        self.assertIn("[1] Your IP range was scanned.", report_txt)
        self.assertIn(
            "https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning-target",
            report_txt,
        )
        self.assertIn("First event:", report_txt)
        self.assertIn("2018-01-01 13:00:00 Z", report_txt)
        self.assertIn("Target IP addresses", report_txt)
        self.assertIn("Source IP addresses", report_txt)
        self.assertIn("10.0.2.1", report_txt)
        self.assertIn("11.2.2.0/24, 2004:ffff::ff00:42:0/112", report_txt)
        self.assertIn("Details from detector org.example.dionaea:", report_txt)
        self.assertIn("------------------------------------------------", report_txt)

    def test_09_filter_events_by_credibility(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.filter_events_by_credibility` function.
        """
        self.maxDiff = None

        ev1 = Mock(mentat.idea.internal.Idea)
        ev1.get_detectors = Mock(return_value=["org.example.kippo_honey"])
        ev1.get_id = Mock(return_value="idea_event1")
        ev2 = Mock(mentat.idea.internal.Idea)
        ev2.get_detectors = Mock(return_value=["org.example.dionaea"])
        ev2.get_id = Mock(return_value="idea_event2")
        ev3 = Mock(mentat.idea.internal.Idea)
        ev3.get_detectors = Mock(return_value=["org.example.new_detector"])
        ev3.get_id = Mock(return_value="idea_event3")

        events = {"10.3.12.13": [ev1, ev2], "133.13.42.13": [ev2], "64.24.35.24": [ev3]}

        _events_aggr, blocked_cnt = self.reporter.filter_events_by_credibility(events)

        self.assertEqual(blocked_cnt, 1)
        self.assertEqual(_events_aggr, {"10.3.12.13": [ev1], "64.24.35.24": [ev3]})
        self.reporter.logger.assert_has_calls(
            [
                call.info("Discarding event with ID '%s'.", "idea_event2"),
                call.info(
                    "Event with ID '%s' contains unknown detector '%s'. Assuming full credibility.",
                    "idea_event3",
                    "org.example.new_detector",
                ),
            ]
        )

        _events_aggr, _ = self.reporter.filter_events_by_credibility({"133.13.42.13": [ev2]})
        self.assertFalse(_events_aggr)

        detectors = {det.name: det for det in self.sqlstorage.session.query(DetectorModel).all()}
        self.assertEqual(detectors["org.example.kippo_honey"].hits, 12)
        self.assertEqual(detectors["org.example.dionaea"].hits, 123)

    # ---------------------------------------------------------------------------

    def _generate_mock_report(self, abuse_group, severity, rtype, events=None, is_target=False):
        if not events:
            events = self.ideas_obj

        report = EventReportModel(
            groups=[abuse_group],
            severity=severity,
            type=rtype,
            dt_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
            dt_to=datetime.datetime.utcnow(),
            evcount_rep=len(events),
            evcount_all=len(events),
            evcount_flt=len(events),
            evcount_flt_blk=1,
            evcount_thr=len(events),
            evcount_thr_blk=0,
            evcount_rlp=0,
            filtering={"FLT01": 1},
        )
        report.generate_label()
        report.calculate_delta()

        if rtype == mentat.const.REPORTING_MODE_EXTRA:
            report.parent = EventReportModel(
                groups=[abuse_group],
                severity=severity,
                type=mentat.const.REPORTING_MODE_SUMMARY,
                dt_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                dt_to=datetime.datetime.utcnow(),
                evcount_rep=len(events),
                evcount_all=len(events),
                evcount_flt=len(events),
                evcount_flt_blk=1,
                evcount_thr=len(events),
                evcount_thr_blk=0,
                evcount_rlp=0,
                filtering={"FLT01": 1},
            )
            report.parent.generate_label()
            report.parent.calculate_delta()

        report.statistics = mentat.stats.idea.truncate_evaluations(mentat.stats.idea.evaluate_events(events, is_target))

        events_aggr = {}
        for obj in events:
            for src in get_values(obj, "Source.IP4") + get_values(obj, "Source.IP6"):
                events_aggr[src] = [obj]
        report.structured_data = self.reporter.prepare_structured_data(
            events_aggr, events_aggr, self.reporting_settings, is_target
        )
        return report


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
