"""
Complete pytest test suite for compassheadinglib
Combines original tests with additional coverage for untested functionality
"""

import pytest
from compassheadinglib import Compass
from compassheadinglib.common import Heading, _instanceTypeCheck
from random import uniform
from json import load
from pathlib import Path
from itertools import chain
from collections import Counter


class TestBasicFunctionality:
    """Test basic compass functionality and data integrity"""
    
    def test_wrap_around(self):
        """Test that first and last compass entries wrap around correctly"""
        assert Compass[0].name == Compass[-1].name
        assert Compass[0].abbr == Compass[-1].abbr
        assert Compass[0].order == Compass[-1].order
        assert Compass[0].azimuth < Compass[-1].azimuth

    def test_monotonic_range_increase(self):
        """Test that azimuth values increase monotonically"""
        last = -1
        items_monotonicity = []
        for i in Compass:
            items_monotonicity.append(last < i.azimuth)
            last = i.azimuth
        assert all(items_monotonicity)

    def test_heading_orders(self):
        """Test that data contains only order 1-4 and correct counts"""
        number_of_heading_levels = 4
        assert set(range(1, number_of_heading_levels + 1)) == set([i.order for i in Compass])
        
        # Count entries for each order
        # Order 1 has 5 values because 'North' gets repeated as first and last elements
        assert len([i for i in Compass if i.order == 1]) == 5
        assert len([i for i in Compass if i.order == 2]) == 4
        assert len([i for i in Compass if i.order == 3]) == 8
        assert len([i for i in Compass if i.order == 4]) == 16

class TestRandomizedRangeSelection:
    """Test randomized range selection with fuzzing"""
    
    def test_randomized_range_selection(self):
        """Test randomized range selection against expected results"""
        number_of_random_range_selections = 1000  # Reduced for faster testing
        slice_angle = 11.25
        
        _compass = Compass.asList()
        angle_list = [uniform(0.0, 360.0) for _ in range(number_of_random_range_selections)]
        
        for angle in angle_list:
            res = int(angle // slice_angle)
            # Test can be off by one since it's simpler than the real logic
            expected_heading = Heading(**_compass[res])
            expected_heading_plus_one = Heading(**_compass[res + 1]) if res + 1 < len(_compass) else Heading(**_compass[0])
            actual_heading = Compass.findHeading(angle, 4)
            
            assert (expected_heading.name == actual_heading.name or 
                   expected_heading_plus_one.name == actual_heading.name)


class TestRelativityOperators:
    """Test heading comparison operators"""
    
    def test_manual_relativity_tests(self):
        """Test manual spot tests of relativity operators"""
        assert Compass(0, 1).name == Compass.findHeading(12, 1).name
        assert Compass(0, 1).name == Compass.findHeading(12, 2).name
        assert Compass(0, 1).name < Compass.findHeading(12, 3).name
        assert Compass(0, 1).name < Compass.findHeading(12, 4).name
        assert Compass(12, 3).name > Compass.findHeading(0, 1).name
        assert Compass(12, 4).name > Compass.findHeading(0, 1).name

    def test_randomized_relativity_tests(self):
        """Test randomized relativity comparisons"""
        number_of_random_relativity_tests = 1000  # Reduced for faster testing
        slice_angle = 11.25
        
        for relative_a, relative_b in [(uniform(0, 360), uniform(0, 360)) 
                                      for _ in range(number_of_random_relativity_tests)]:
            
            if (relative_a // slice_angle) == (relative_b // slice_angle):
                try:
                    assert Compass.findHeading(relative_a, order=3).name == Compass.findHeading(relative_b, order=3).name
                except Exception as e1:
                    try:
                        assert Compass.findHeading(relative_a, order=2).name == Compass.findHeading(relative_b, order=2).name
                    except Exception as e2:
                        assert Compass.findHeading(relative_a, order=1).name == Compass.findHeading(relative_b, order=1).name  

            
            elif ((relative_a // slice_angle) < (relative_b // slice_angle)) and abs(relative_a - relative_b) < slice_angle:
                assert Compass.findHeading(relative_a, order=4) <= Compass.findHeading(relative_b, order=4)
            elif ((relative_a // slice_angle) > (relative_b // slice_angle)) and abs(relative_a - relative_b) < slice_angle:
                assert Compass.findHeading(relative_a, order=4) >= Compass.findHeading(relative_b, order=4)
            
            elif (relative_a // slice_angle) < (relative_b // slice_angle):
                assert Compass.findHeading(relative_a, order=4) < Compass.findHeading(relative_b, order=4)
            elif (relative_a // slice_angle) > (relative_b // slice_angle):
                assert Compass.findHeading(relative_a, order=4) > Compass.findHeading(relative_b, order=4)


class TestArithmeticOperations:
    """Test arithmetic operations on headings"""
    
    def test_heading_addition(self):
        """Test Heading + Heading and Heading + number"""
        north = Compass.findHeading(0, 1)  # North
        east = Compass.findHeading(90, 1)  # East
        
        # Test Heading + Heading
        result = north + east
        assert result.azimuth == 90.0
        
        # Test Heading + number
        result = north + 45
        assert result.azimuth == 45.0

    def test_reverse_addition(self):
        """Test number + Heading (__radd__)"""
        north = Compass.findHeading(0, 1)
        result = 45 + north
        assert result.azimuth == 45.0

    def test_heading_subtraction(self):
        """Test Heading - Heading and Heading - number"""
        north = Compass.findHeading(0, 1)
        east = Compass.findHeading(90, 1)
        
        # Test Heading - Heading
        result = east - north
        assert result.azimuth == 90.0
        
        # Test Heading - number
        result = east - 45
        assert result.azimuth == 45.0

    def test_reverse_subtraction(self):
        """Test number - Heading (__rsub__)"""
        north = Compass.findHeading(0, 1)
        result = 180 - north
        assert result.azimuth == 180.0

    def test_arithmetic_wraparound(self):
        """Test wraparound in arithmetic operations"""
        north = Compass.findHeading(0, 1)
        
        # Test negative wraparound
        result = north - 45  # 0 - 45 should wrap to 315
        assert result.azimuth == 315.0
        
        # Test positive wraparound
        result = Compass.findHeading(350, 1) + 20  # 350 + 20 should wrap to 10
        assert result.azimuth == 10.0

    def test_random_arithmetic_operations(self):
        """Test random arithmetic operations for consistency"""
        number_of_tests = 100  # Reduced for faster testing
        
        for _ in range(number_of_tests):
            bearing1 = uniform(0, 360)
            operation_value = uniform(-720, 720)
            
            heading1 = Compass.findHeading(bearing1, 4)
            
            # Test addition with modulo consistency
            add_result = heading1 + operation_value
            expected_add = (bearing1 + operation_value) % 360
            assert abs(add_result.azimuth - expected_add) < 0.001
            
            # Test subtraction with modulo consistency
            sub_result = heading1 - operation_value
            expected_sub = (bearing1 - operation_value) % 360
            assert abs(sub_result.azimuth - expected_sub) < 0.001


class TestNavigationMethods:
    """Test navigation methods (port, starboard, left, right, rotate)"""
    
    def test_port_starboard(self):
        """Test port (left turn) and starboard (right turn)"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        # Test port (left turn)
        port_result = heading_90.port(30)
        assert port_result.azimuth == 60.0
        
        # Test starboard (right turn)
        starboard_result = heading_90.starboard(30)
        assert starboard_result.azimuth == 120.0

    def test_left_right_aliases(self):
        """Test left and right as aliases for port and starboard"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        # Test left (alias for port)
        left_result = heading_90.left(30)
        assert left_result.azimuth == 60.0
        
        # Test right (alias for starboard)
        right_result = heading_90.right(30)
        assert right_result.azimuth == 120.0

    def test_rotate(self):
        """Test rotate method (positive and negative)"""
        heading_90 = Compass.findHeading(90, 1)  # East
        
        rotate_result = heading_90.rotate(45)
        assert rotate_result.azimuth == 135.0
        
        rotate_result = heading_90.rotate(-45)
        assert rotate_result.azimuth == 45.0

    def test_navigation_wraparound(self):
        """Test wraparound in navigation methods"""
        heading_10 = Compass.findHeading(10, 1)
        port_wrap = heading_10.port(20)  # 10 - 20 should wrap to 350
        assert port_wrap.azimuth == 350.0
        
        heading_350 = Compass.findHeading(350, 1)
        starboard_wrap = heading_350.starboard(20)  # 350 + 20 should wrap to 10
        assert starboard_wrap.azimuth == 10.0

    def test_negative_degrees_assertion(self):
        """Test assertion in port and starboard methods for negative degrees"""
        heading_90 = Compass.findHeading(90, 1)
        
        with pytest.raises(AssertionError):
            heading_90.port(-10)
        
        with pytest.raises(AssertionError):
            heading_90.starboard(-10)


class TestMagicMethods:
    """Test magic methods (__abs__, __float__, __str__, __repr__)"""
    
    def test_abs_float_methods(self):
        """Test __abs__ and __float__ methods"""
        heading = Compass.findHeading(270, 1)
        
        # Test __abs__
        abs_result = abs(heading)
        assert abs_result == 270.0
        
        # Test __float__
        float_result = float(heading)
        assert float_result == 270.0

    def test_str_repr_methods(self):
        """Test __str__ and __repr__ methods"""
        heading = Compass.findHeading(270, 1)
        
        # Test __str__
        str_result = str(heading)
        assert isinstance(str_result, str)
        assert str_result == heading.name
        
        # Test __repr__
        repr_result = repr(heading)
        assert isinstance(repr_result, str)
        assert repr_result == heading.name


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_as_dict_method(self):
        """Test asDict method"""
        heading = Compass.findHeading(45, 4)
        dict_result = heading.asDict()
        
        assert isinstance(dict_result, dict)
        assert 'name' in dict_result
        assert 'abbr' in dict_result
        assert 'azimuth' in dict_result
        assert 'order' in dict_result
        
        # Ensure langs and parent are excluded
        assert 'langs' not in dict_result
        assert 'parent' not in dict_result

    def test_withBearing_method(self):
        """Test withBearing method"""
        original_heading = Compass.findHeading(45, 3)
        new_bearing_heading = original_heading.withBearing__(120)
        
        # Should have same name, abbr, order, but different azimuth
        assert new_bearing_heading.name == original_heading.name
        assert new_bearing_heading.abbr == original_heading.abbr
        assert new_bearing_heading.order == original_heading.order
        assert new_bearing_heading.azimuth == 120.0


class TestHeadingsClass:
    """Test _Headings class methods"""
    
    def test_getattr_method(self):
        """Test __getattr__ method for attribute-style access"""
        north_attr = Compass.north
        assert north_attr.name == "North"

    def test_setattr_delattr_methods(self):
        """Test __setattr__ and __delattr__ methods"""
        # Create a test heading
        test_heading = Heading("Test", "T", 999, 5, {}, Compass)
        
        # Test setting attribute
        Compass.test_heading = test_heading
        assert Compass.test_heading == test_heading
        
        # Test deleting attribute
        del Compass.test_heading
        with pytest.raises((KeyError, AttributeError)):
            _ = Compass.test_heading


class TestErrorHandling:
    """Test error handling"""
    
    def test_instance_type_check(self):
        """Test _instanceTypeCheck error handling"""
        # Test with correct type
        _instanceTypeCheck("test", str)  # Should not raise
        
        # Test with list of types
        _instanceTypeCheck(5, [int, float])  # Should not raise
        
        # Test with incorrect type
        with pytest.raises(TypeError) as excinfo:
            _instanceTypeCheck("test", int)
        assert "Variable type must be" in str(excinfo.value)
        
        # Test with list of incorrect types
        with pytest.raises(TypeError) as excinfo:
            _instanceTypeCheck("test", [int, float])
        assert "Variable type must be one of" in str(excinfo.value)


class TestEdgeCases:
    """Test edge cases"""
    
    def test_exact_360_operations(self):
        """Test exact 360-degree operations"""
        heading_0 = Compass.findHeading(0, 1)
        
        result_360 = heading_0 + 360
        assert result_360.azimuth == 0.0
        
        result_720 = heading_0 + 720
        assert result_720.azimuth == 0.0
        
        # Test negative wraparound
        result_neg = heading_0 - 90
        assert result_neg.azimuth == 270.0


class TestMultiLanguageSupport:
    """Test multi-language support functionality"""
    
    @pytest.fixture(scope="class")
    def compass_data(self):
        """Load compass data from JSON file"""
        try:
            # Try to find the data file relative to the test
            data_file_path = Path(__file__).parent / '../compassheadinglib/compass_data.json'
            if not data_file_path.exists():
                # Alternative path
                data_file_path = Path('compassheadinglib/compass_data.json')
            
            if data_file_path.exists():
                with open(data_file_path, 'rt') as f:
                    return load(f)
            else:
                pytest.skip("compass_data.json not found - skipping multilanguage tests")
        except Exception as e:
            pytest.skip(f"Could not load compass data: {e}")

    def flatten(self, x):
        """Helper function to flatten nested lists"""
        return list(chain.from_iterable(x))

    def test_language_structure(self, compass_data):
        """Test that all languages have proper structure"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        # Get all unique language codes in the dataset
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for heading in compass_data:
            for lang in all_langs:
                # All languages must be present in all headings
                assert lang in heading['Lang'], f'{lang} missing from {heading["Azimuth"]}'
                
                # Check that structure is well formed
                assert 'Heading' in heading['Lang'][lang]
                assert 'Abbreviation' in heading['Lang'][lang]

    def test_unique_translations(self, compass_data):
        """Test that translations are unique within each language"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for lang in all_langs:
            lang_compass = [i['Lang'][lang] | i for i in compass_data]
            
            # No duplicate heading names (except for North wraparound)
            heading_names = [i['Heading'] for i in lang_compass]
            heading_counter = Counter(heading_names)
            
            for name, count in heading_counter.items():
                if count > 1:
                    # Check if this is the expected North wraparound
                    azimuths = [i['Azimuth'] for i in lang_compass if i['Heading'] == name]
                    if not (len(azimuths) == 2 and 0 in azimuths and 360 in azimuths):
                        pytest.fail(f"Duplicate heading name '{name}' in language '{lang}' at azimuths {azimuths}")
            
            # No duplicate abbreviations (except for North wraparound)
            abbr_names = [i['Abbreviation'] for i in lang_compass]
            abbr_counter = Counter(abbr_names)
            
            for abbr, count in abbr_counter.items():
                if count > 1:
                    # Check if this is the expected North wraparound
                    azimuths = [i['Azimuth'] for i in lang_compass if i['Abbreviation'] == abbr]
                    if not (len(azimuths) == 2 and 0 in azimuths and 360 in azimuths):
                        pytest.fail(f"Duplicate abbreviation '{abbr}' in language '{lang}' at azimuths {azimuths}")

    def test_language_wraparound(self, compass_data):
        """Test wraparound for each language"""
        if not compass_data:
            pytest.skip("No compass data available")
            
        all_langs = list(sorted(set(self.flatten([i['Lang'].keys() for i in compass_data]))))
        
        for lang in all_langs:
            lang_compass = [i['Lang'][lang] | i for i in compass_data]
            
            # Wrap around test, per language
            assert lang_compass[0]['Heading'] == lang_compass[-1]['Heading'], f'Wrap around test fail: Heading for {lang}'
            assert lang_compass[0]['Abbreviation'] == lang_compass[-1]['Abbreviation'], f'Wrap around test fail: Abbreviation for {lang}'
            assert lang_compass[0]['Order'] == lang_compass[-1]['Order'], f'Wrap around test fail: Order for {lang}'
            assert lang_compass[0]['Azimuth'] < lang_compass[-1]['Azimuth'], f'Wrap around test fail: Azimuth for {lang}'


if __name__ == "__main__":
    # Run tests with pytest when script is executed directly
    pytest.main([__file__, "-v"])