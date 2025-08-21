import unittest

from mb_cruise_migration.models.intermediary.mb_cargo import MbSurveyCrate
from mb_cruise_migration.models.mb.mb_survey import MbSurvey
from mb_cruise_migration.models.mb.mb_survey_reference import SurveyReference


class TestProviderFromSource(unittest.TestCase):
    def test_standard(self):

        source1 = "University of Rhode Island (URI)"
        source2 = "Rolling Deck to Repository (R2R)"

        result1 = self.get_derived_provider(source1)
        result2 = self.get_derived_provider(source2)

        expectation1 = "URI"
        expectation2 = "R2R"

        self.assertEqual(result1, expectation1)
        self.assertEqual(result2, expectation2)

    def test_standard_with_slashes(self):

        source1 = "California State University Monterey Bay, Seafloor Mapping Lab (CSUMB/SFML)"
        source2 = "University of California San Diego, Scripps Institution of Oceanography (UCSD/SIO)"

        result1 = self.get_derived_provider(source1)
        result2 = self.get_derived_provider(source2)

        expectation1 = "CSUMB-SFML"
        expectation2 = "UCSD-SIO"

        self.assertEqual(result1, expectation1)
        self.assertEqual(result2, expectation2)

    def test_no_provider(self):

        source1 = "United States Navy"
        source2 = "Rolling Deck to Repository"

        result1 = self.get_derived_provider(source1)
        result2 = self.get_derived_provider(source2)

        expectation1 = "UNITED-STATES-NAVY"
        expectation2 = "ROLLING-DECK-TO-REPOSITORY"

        self.assertEqual(result1, expectation1)
        self.assertEqual(result2, expectation2)

    def test_multiple_with_provider(self):

        source1 = "United States Navy; Rolling Deck to Repository (USN/R2R)"

        result1 = self.get_derived_provider(source1)

        expectation1 = "USN-R2R"

        self.assertEqual(result1, expectation1)

    def test_multiple_no_provider(self):

        source1 = "United States Navy; Rolling Deck to Repository"

        result1 = self.get_derived_provider(source1)

        expectation1 = "UNITED-STATES-NAVY-ROLLING-DECK-TO-REPOSITORY"

        self.assertEqual(result1, expectation1)

    def test_no_provider_with_commas(self):

        source1 = "Max Planck Institute for Marine Microbiology, Breman, Germany"

        result1 = self.get_derived_provider(source1)

        expectation1 = "MAX-PLANCK-INSTITUTE-FOR-MARINE-MICROBIOLOGY-BREMAN-GERMANY"

        self.assertEqual(result1, expectation1)

    def test_provider_with_special_chars(self):

        source1 = "Rolling Deck to Repository (R2R!@#$,%^&*)"

        result1 = self.get_derived_provider(source1)

        expectation1 = "R2R"

        self.assertEqual(result1, expectation1)

    def test_no_provider_with_special_chars(self):

        source1 = "Rol!@ling #$ Deck to,% ^&Repository *"

        result1 = self.get_derived_provider(source1)

        expectation1 = "ROLLING-DECK-TO-REPOSITORY"

        self.assertEqual(expectation1, result1)

    def get_derived_provider(self, source):
        return self.create_dummy_mb_crate(source).provider

    @staticmethod
    def create_dummy_mb_crate(source):
        return MbSurveyCrate(
            MbSurvey(amp_beams="amp_beams", arrival_port="arrival_port", bathy_beams="bathy_beams", chief_sci_organization="chief_sci_organization",
                     comments="comments", contact_id="contact_id", end_time="end_time", entered_date="entered_date", extract_metadata="extract_metadata",
                     file_count="file_count", horizontal_datum="horizontal_datum", instrument="instrument", modify_date_data="modify_date_data",
                     modify_date_metadata="modify_date_metadata", nav1="nav1", nav2="nav2", previous_state="previous_state", project_name="project_name",
                     proprietary="proprietary", publish="publish", ship_name="ship_name", ship_owner="ship_owner", sidescans="sidescans",
                     sound_velocity="sound_velocity", source=source, start_time="start_time", survey_name="survey_name", survey_size="survey_size",
                     tide_correction="tide_correction", total_time="total_time", track_length="track_length", vertical_datum="vertical_datum",
                     chief_scientist="chief_scientist", departure_port="departure_port", ngdc_id="ngdc_id"),
            SurveyReference("abstract", "create_date", "created_by", "doi", "download_url", "last_update_date", "last_updated_by",
                            "ngdc_id", "project_url", "purpose"),
            "shape")
