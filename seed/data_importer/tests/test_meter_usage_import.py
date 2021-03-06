# !/usr/bin/env python
# encoding: utf-8

import json
import os

from config.settings.common import TIME_ZONE

from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import (
    get_current_timezone,
    make_aware,  # make_aware is used because inconsistencies exist in creating datetime with tzinfo
)

from pytz import timezone

from quantityfield import ureg

from seed.data_importer.models import ImportFile, ImportRecord
from seed.landing.models import SEEDUser as User
from seed.models import (
    Meter,
    MeterReading,
    Property,
    PropertyState,
    PropertyView,
)
from seed.test_helpers.fake import (
    FakeCycleFactory,
    FakePropertyFactory,
    FakePropertyStateFactory,
)
from seed.utils.organizations import create_organization


class MeterUsageImportTest(TestCase):
    def setUp(self):
        self.user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
        }
        self.user = User.objects.create_superuser(
            email='test_user@demo.com', **self.user_details
        )
        self.org, _, _ = create_organization(self.user)
        self.client.login(**self.user_details)

        self.property_state_factory = FakePropertyStateFactory(organization=self.org)
        property_details = self.property_state_factory.get_details()
        property_details['organization_id'] = self.org.id

        # pm_property_ids must match those within example-monthly-meter-usage.xlsx
        self.pm_property_id_1 = '5766973'
        self.pm_property_id_2 = '5766975'

        property_details['pm_property_id'] = self.pm_property_id_1
        state_1 = PropertyState(**property_details)
        state_1.save()
        self.state_1 = PropertyState.objects.get(pk=state_1.id)

        property_details['pm_property_id'] = self.pm_property_id_2
        state_2 = PropertyState(**property_details)
        state_2.save()
        self.state_2 = PropertyState.objects.get(pk=state_2.id)

        self.cycle_factory = FakeCycleFactory(organization=self.org, user=self.user)
        self.cycle = self.cycle_factory.get_cycle(start=datetime(2010, 10, 10, tzinfo=get_current_timezone()))

        self.property_factory = FakePropertyFactory(organization=self.org)
        self.property_1 = self.property_factory.get_property()
        self.property_2 = self.property_factory.get_property()

        self.property_view_1 = PropertyView.objects.create(property=self.property_1, cycle=self.cycle, state=self.state_1)
        self.property_view_2 = PropertyView.objects.create(property=self.property_2, cycle=self.cycle, state=self.state_2)

        import_record = ImportRecord.objects.create(owner=self.user, last_modified_by=self.user, super_organization=self.org)

        filename = "example-pm-monthly-meter-usage.xlsx"
        filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename

        self.import_file = ImportFile.objects.create(
            import_record=import_record,
            source_type="PM Meter Usage",
            uploaded_filename=filename,
            file=SimpleUploadedFile(name=filename, content=open(filepath, 'rb').read()),
            cycle=self.cycle
        )

        self.tz_obj = timezone(TIME_ZONE)

    def test_import_meter_usage_file_base_case(self):
        """
        Expect to have 4 meters - 2 for each property - 1 for gas and 1 for electricity.
        Each meter will have 2 readings, for a total of 8 readings.
        These come from 4 meter usage rows in the .xlsx file, each with 2 meter readings.
        """
        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        self.client.post(url, post_params)

        refreshed_property_1 = Property.objects.get(pk=self.property_1.id)
        self.assertEqual(refreshed_property_1.meters.all().count(), 2)

        meter_1 = refreshed_property_1.meters.get(type=Meter.ELECTRICITY)
        self.assertEqual(meter_1.source, Meter.PORTFOLIO_MANAGER)
        self.assertEqual(meter_1.source_id, '5766973')
        self.assertEqual(meter_1.is_virtual, False)
        self.assertEqual(meter_1.meter_readings.all().count(), 2)

        meter_reading_10, meter_reading_11 = list(meter_1.meter_readings.order_by('start_time').all())

        self.assertEqual(meter_reading_10.start_time, make_aware(datetime(2016, 1, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_10.end_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_10.reading, 597478.9 * ureg('kBtu'))
        self.assertEqual(meter_reading_10.source_unit, "kBtu")  # spot check
        self.assertEqual(meter_reading_10.conversion_factor, 1)  # spot check

        self.assertEqual(meter_reading_11.start_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_11.end_time, make_aware(datetime(2016, 3, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_11.reading, 548603.7 * ureg('kBtu'))

        meter_2 = refreshed_property_1.meters.get(type=Meter.NATURAL_GAS)
        self.assertEqual(meter_2.source, Meter.PORTFOLIO_MANAGER)
        self.assertEqual(meter_2.source_id, '5766973')
        self.assertEqual(meter_2.meter_readings.all().count(), 2)

        meter_reading_20, meter_reading_21 = list(meter_2.meter_readings.order_by('start_time').all())

        self.assertEqual(meter_reading_20.start_time, make_aware(datetime(2016, 1, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_20.end_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_20.reading, 576000.2 * ureg('kBtu'))

        self.assertEqual(meter_reading_21.start_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_21.end_time, make_aware(datetime(2016, 3, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_21.reading, 488000.1 * ureg('kBtu'))

        refreshed_property_2 = Property.objects.get(pk=self.property_2.id)
        self.assertEqual(refreshed_property_2.meters.all().count(), 2)

        meter_3 = refreshed_property_2.meters.get(type=Meter.ELECTRICITY)
        self.assertEqual(meter_3.source, Meter.PORTFOLIO_MANAGER)
        self.assertEqual(meter_3.source_id, '5766975')
        self.assertEqual(meter_3.meter_readings.all().count(), 2)

        meter_reading_30, meter_reading_40 = list(meter_3.meter_readings.order_by('start_time').all())

        self.assertEqual(meter_reading_30.start_time, make_aware(datetime(2016, 1, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_30.end_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_30.reading, 154572.2 * ureg('kBtu'))
        self.assertEqual(meter_reading_30.source_unit, "kBtu")  # spot check
        self.assertEqual(meter_reading_30.conversion_factor, 1)  # spot check

        self.assertEqual(meter_reading_40.start_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_40.end_time, make_aware(datetime(2016, 3, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_40.reading, 141437.5 * ureg('kBtu'))

        meter_4 = refreshed_property_2.meters.get(type=Meter.NATURAL_GAS)
        self.assertEqual(meter_4.source, Meter.PORTFOLIO_MANAGER)
        self.assertEqual(meter_4.source_id, '5766975')
        self.assertEqual(meter_4.meter_readings.all().count(), 2)

        meter_reading_40, meter_reading_41 = list(meter_4.meter_readings.order_by('start_time').all())

        self.assertEqual(meter_reading_40.start_time, make_aware(datetime(2016, 1, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_40.end_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_40.reading, 299915 * ureg('kBtu'))

        self.assertEqual(meter_reading_41.start_time, make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_41.end_time, make_aware(datetime(2016, 3, 1, 0, 0, 0), timezone=self.tz_obj))
        self.assertEqual(meter_reading_41.reading, 496310.9 * ureg('kBtu'))

        # file should be disassociated from cycle too
        refreshed_import_file = ImportFile.objects.get(pk=self.import_file.id)
        self.assertEqual(refreshed_import_file.cycle_id, None)

    def test_existing_meter_is_found_and_used_if_import_file_should_reference_it(self):
        property = Property.objects.get(pk=self.property_1.id)

        # Create a meter with the same details of one meter in the import file
        unsaved_meter = Meter(
            property=property,
            source=Meter.PORTFOLIO_MANAGER,
            source_id='5766973',
            type=Meter.ELECTRICITY,
        )
        unsaved_meter.save()
        existing_meter = Meter.objects.get(pk=unsaved_meter.id)

        # Create a reading with a different date from those in the import file
        unsaved_meter_reading = MeterReading(
            meter=existing_meter,
            start_time=make_aware(datetime(2018, 1, 1, 0, 0, 0), timezone=self.tz_obj),
            end_time=make_aware(datetime(2018, 2, 1, 0, 0, 0), timezone=self.tz_obj),
            reading=12345,
        )
        unsaved_meter_reading.save()
        existing_meter_reading = MeterReading.objects.get(reading=12345)

        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        self.client.post(url, post_params)

        refreshed_property_1 = Property.objects.get(pk=self.property_1.id)
        self.assertEqual(refreshed_property_1.meters.all().count(), 2)

        refreshed_meter = refreshed_property_1.meters.get(type=Meter.ELECTRICITY)

        meter_reading_10, meter_reading_11, meter_reading_12 = list(refreshed_meter.meter_readings.order_by('start_time').all())
        self.assertEqual(meter_reading_10.reading, 597478.9 * ureg('kBtu'))
        self.assertEqual(meter_reading_11.reading, 548603.7 * ureg('kBtu'))

        # Sanity check to be sure, nothing was changed with existing meter reading
        self.assertEqual(meter_reading_12, existing_meter_reading)

    def test_existing_meter_reading_has_reading_source_unit_and_conversion_factor_updated_if_import_file_references_previous_entry(self):
        property = Property.objects.get(pk=self.property_1.id)

        # Create a meter with the same details of one meter in the import file
        unsaved_meter = Meter(
            property=property,
            source=Meter.PORTFOLIO_MANAGER,
            source_id='5766973',
            type=Meter.ELECTRICITY,
        )
        unsaved_meter.save()
        existing_meter = Meter.objects.get(pk=unsaved_meter.id)

        # Create a reading with the same date as one from the import file but different reading
        start_time = make_aware(datetime(2016, 1, 1, 0, 0, 0), timezone=self.tz_obj)
        end_time = make_aware(datetime(2016, 2, 1, 0, 0, 0), timezone=self.tz_obj)

        unsaved_meter_reading = MeterReading(
            meter=existing_meter,
            start_time=start_time,
            end_time=end_time,
            reading=12345,
            source_unit="GJ",
            conversion_factor=947.817
        )
        unsaved_meter_reading.save()

        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        self.client.post(url, post_params)

        # Just as in the first test, 8 meter readings should exist
        self.assertEqual(MeterReading.objects.all().count(), 8)

        refreshed_property = Property.objects.get(pk=self.property_1.id)
        refreshed_meter = refreshed_property.meters.get(type=Meter.ELECTRICITY)
        meter_reading = refreshed_meter.meter_readings.get(start_time=start_time)

        self.assertEqual(meter_reading.end_time, end_time)
        self.assertEqual(meter_reading.reading, 597478.9 * ureg('kBtu'))
        self.assertEqual(meter_reading.source_unit, "kBtu")
        self.assertEqual(meter_reading.conversion_factor, 1)

    def test_property_existing_in_multiple_cycles_can_have_meters_and_readings_associated_to_it(self):
        property_details = FakePropertyStateFactory(organization=self.org).get_details()
        property_details['organization_id'] = self.org.id

        # new state to be associated to new cycle using the same pm_property_id as state in old cycle
        property_details['pm_property_id'] = self.state_1.pm_property_id
        state = PropertyState(**property_details)
        state.save()
        new_property_state = PropertyState.objects.get(pk=state.id)

        new_cycle_factory = FakeCycleFactory(organization=self.org, user=self.user)
        new_cycle = new_cycle_factory.get_cycle(start=datetime(2010, 10, 10, tzinfo=get_current_timezone()))

        # new state and cycle associated to old property
        PropertyView.objects.create(property=self.property_1, cycle=new_cycle, state=new_property_state)

        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        self.client.post(url, post_params)

        refreshed_property_1 = Property.objects.get(pk=self.property_1.id)
        self.assertEqual(refreshed_property_1.meters.all().count(), 2)

    def test_pm_property_id_existing_across_two_different_orgs_wont_lead_to_misassociated_meters(self):
        new_org, _, _ = create_organization(self.user)

        property_details = FakePropertyStateFactory(organization=new_org).get_details()
        property_details['organization_id'] = new_org.id

        # new state to be associated to property of different organization but has the same pm_property_id
        property_details['pm_property_id'] = self.state_1.pm_property_id
        state = PropertyState(**property_details)
        state.save()
        new_property_state = PropertyState.objects.get(pk=state.id)

        new_cycle_factory = FakeCycleFactory(organization=new_org, user=self.user)
        new_cycle = new_cycle_factory.get_cycle(start=datetime(2010, 10, 10, tzinfo=get_current_timezone()))

        new_property = self.property_factory.get_property()

        PropertyView.objects.create(property=new_property, cycle=new_cycle, state=new_property_state)

        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        self.client.post(url, post_params)

        # self.property_1 is associated to self.org, so according to post request, it should have 2 meters
        refreshed_property_1 = Property.objects.get(pk=self.property_1.id, organization_id__exact=self.org.pk)
        self.assertEqual(refreshed_property_1.meters.all().count(), 2)

        refreshed_new_property = Property.objects.get(pk=new_property.id)
        self.assertEqual(refreshed_new_property.meters.count(), 0)

    def test_the_response_contains_expected_and_actual_reading_counts_for_pm_ids(self):
        url = reverse("api:v2:import_files-save-raw-data", args=[self.import_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        response = self.client.post(url, post_params)

        result = json.loads(response.content)

        expectation = [
            {
                "source_id": "5766973",
                "incoming": 4,
                "successfully_imported": 4,
            },
            {
                "source_id": "5766975",
                "incoming": 4,
                "successfully_imported": 4,
            },
        ]

        self.assertEqual(result['message'], expectation)

    def test_error_noted_in_response_if_meter_has_overlapping_readings(self):
        """
        If a meter has overlapping readings, the process of upserting a reading
        will encounter the issue of not knowing which reading should take
        precedence over the other.

        In this case, neither the meter (if applicable) nor any of its readings
        are created.
        """
        dup_import_record = ImportRecord.objects.create(owner=self.user, last_modified_by=self.user, super_organization=self.org)
        dup_filename = "example-pm-monthly-meter-usage-1-dup.xlsx"
        dup_filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/" + dup_filename

        dup_file = ImportFile.objects.create(
            import_record=dup_import_record,
            source_type="PM Meter Usage",
            uploaded_filename=dup_filename,
            file=SimpleUploadedFile(name=dup_filename, content=open(dup_filepath, 'rb').read()),
            cycle=self.cycle
        )

        url = reverse("api:v2:import_files-save-raw-data", args=[dup_file.id])
        post_params = {
            'cycle_id': self.cycle.pk,
            'organization_id': self.org.pk,
        }
        response = self.client.post(url, post_params)

        total_meters_count = Meter.objects.count()

        result_summary = json.loads(response.content)

        expected_import_summary = [
            {
                "source_id": "5766973",
                "incoming": 4,
                "successfully_imported": 4,
                "errors": "",
            },
            {
                "source_id": "5766975",
                "incoming": 8,
                "successfully_imported": 0,
                "errors": "Overlapping readings.",
            },
        ]

        self.assertEqual(result_summary['message'], expected_import_summary)
        self.assertEqual(total_meters_count, 2)
