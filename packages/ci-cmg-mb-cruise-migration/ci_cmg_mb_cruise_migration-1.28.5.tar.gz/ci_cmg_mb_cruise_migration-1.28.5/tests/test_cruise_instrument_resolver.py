import unittest

from mb_cruise_migration.framework.resolvers.instrument_resolver import InstrumentLookup


class TestInstrumentResolver(unittest.TestCase):

    def test_instrument_util(self):
        survey_name = "Reson SeaBat 9003"
        converted = InstrumentLookup.convert_survey_instrument_to_const_format(survey_name)
        self.assertEqual("RESONSEABAT9003", converted)

        survey_name = "Reson SeaBat T20-P"
        converted = InstrumentLookup.convert_survey_instrument_to_const_format(survey_name)
        self.assertEqual(converted, "RESONSEABATT20P")

