import pytest

from bear_utils.extras._zapper import zap, zap_get, zap_as, zap_as_multi, Zapper


class TestZap:
    def test_zap(self):
        """Test the zap function for symbol removal and replacement."""
        assert zap("!?", "Hello!? World") == "Hello World"
        assert zap("!", "Hello! World! Test!") == "Hello World Test"
        assert zap("-+", "1.2.3-alpha+build", ".") == "1.2.3.alpha.build"

        test_version = "v2.1.4-beta.3+build-2024.01.15_hotfix!urgent"
        expected = "v2.1.4.beta.3.build.2024.01.15.hotfix.urgent"
        assert zap("-+._!", test_version, ".") == expected

        assert zap("!@#", "test!@#data@#!end", "_") == "test___data___end"
        assert zap("123", "a1b2c3d") == "abcd"

    def test_zap_edge_cases(self):
        """Test edge cases and special scenarios."""
        assert zap("!@", "test!!@@data", "_") == "test____data"
        assert zap(".", "1.2.3", ".") == "1.2.3"
        assert zap("★☆", "Hello★World☆Test", "-") == "Hello-World-Test"
        assert zap("123", "version1.2.3", ".") == "version....."
        assert zap("xyz", "Hello World") == "Hello World"  # No symbols found
        assert zap("!?", "") == ""  # Empty string
        assert zap("Hello", "Hello") == ""  # Remove entire string


class TestZapGet:
    def test_zap_get(self):
        """Test the zap_get function for version string parsing."""
        assert zap_get("-+", "1.2.3-alpha", 3, ".") == ("1", "2", "3")
        assert zap_get("-+", "1.2.3+build", 3, ".") == ("1", "2", "3")
        assert zap_get("-+", "1.2.3-alpha", 2, ".") == ("1", "2")
        assert zap_get("-+", "1.2.3-alpha", 4, ".") == ("1", "2", "3", "alpha")

        # Complex version strings
        assert zap_get("-+._", "v1.2.3-beta.4+build_123", 4, ".") == ("v1", "2", "3", "beta")

        # Edge cases
        assert zap_get("", "1.2.3", 3) == ("1", "2", "3")
        assert zap_get("-", "1-2-3", 3, ".") == ("1", "2", "3")

        with pytest.raises(ValueError):
            zap_get("-+", "invalid", 3, ".")

        with pytest.raises(ValueError):
            zap_get("-+", "", 3, ".")  # Empty string

    def test_version_parsing_scenarios(self):
        """Test realistic version string scenarios."""
        assert zap_get("-+", "1.0.0", 3, ".") == ("1", "0", "0")
        assert zap_get("-+", "2.1.4-beta", 3, ".") == ("2", "1", "4")
        assert zap_get("-+", "1.2.3+20240115", 3, ".") == ("1", "2", "3")
        assert zap_get("-+", "1.0.0-alpha.1+build.123", 3, ".") == ("1", "0", "0")
        assert zap_get(".-+", "1.2.3.post1", 3, ".") == ("1", "2", "3")
        assert zap_get(".-+", "2.0.0.dev1+build", 3, ".") == ("2", "0", "0")
        assert zap_get("-+", "v1.2.3-rc1", 4, ".") == ("v1", "2", "3", "rc1")


class TestZapAs:
    def test_zap_as_int(self):
        """Test the zap_as function for type conversion."""

        result = zap_as("-+", "1.2.3-alpha", 3, ".", ".", int)
        assert result == (1, 2, 3)
        assert all(isinstance(x, int) for x in result)

    def test_zap_as_float(self):
        """Test float conversion with coordinate data."""
        result = zap_as(sym=",;", src="1.5,2.7;3.9", unpack_val=3, replace="|", sep="|", func=float)
        assert result == (1.5, 2.7, 3.9)
        assert all(isinstance(x, float) for x in result)

    def test_zap_as_str(self):
        result = zap_as(sym="-+", src="hello-world.test", unpack_val=3, replace=".", sep=".", func=str)
        assert result == ("hello", "world", "test")
        assert all(isinstance(x, str) for x in result)

    def test_zap_as_custom_types(self):
        def to_upper(s: str) -> str:
            return s.upper()

        result = zap_as("-_", "hello-world_test", 3, replace=".", sep=".", func=to_upper)
        assert result == ("HELLO", "WORLD", "TEST")

        result = zap_as("!", "1!2!3", 3, ".", ".", lambda x: int(x) * 2)
        assert result == (2, 4, 6)

    def test_zap_as_path(self):
        from pathlib import Path

        sym = ";"
        result = zap_as(sym, "/home;/tmp;/var", 3, sym, sym, Path)
        assert all(isinstance(x, Path) for x in result)
        assert result[0] == Path("/home")

    def test_zap_as_bool(self):
        result = zap_as(",", "True,False,1", 3, "|", "|", bool)
        assert result == (True, True, True)  # bool("False") is True!

    def test_zap_as_custom_converter(self):
        def safe_int(s: str) -> int:
            try:
                return int(s)
            except ValueError:
                return 0

        result = zap_as("-", "1-bad-3", 3, ".", func=safe_int)
        assert result == (1, 0, 3)

    def test_zap_str_as_number(self):
        with pytest.raises(ValueError):
            zap_as("-", "1-two-3", 3, ".", func=int)  # "two" can't convert to int

    def test_zap_as_invalid_input(self):
        with pytest.raises(ValueError):
            zap_as("-", "1-2", 3, ".", "-", int, strict=True)  # Only 2 items, need 3

    def test_zap_as_empty_string(self):
        with pytest.raises(ValueError):
            zap_as("-", "", 3, ".", "-", int, strict=True)

    def test_zap_as_custom_converter_with_length(self):
        def custom_converter(s: str) -> dict:
            return {"value": s, "length": len(s)}

        result = zap_as("-", "a-bb-ccc", 3, ".", func=custom_converter)
        expected = ({"value": "a", "length": 1}, {"value": "bb", "length": 2}, {"value": "ccc", "length": 3})
        assert result == expected

    def test_zap_as_version_parsing(self):
        major, minor, patch = zap_as("-+", "1.2.3-beta+build", 3, ".", ".", int)
        assert (major, minor, patch) == (1, 2, 3)
        assert all(isinstance(x, int) for x in (major, minor, patch))


class TestZapAsMulti:
    """Testing passing in multiple strings as automatic replacement values."""

    def test_zap_as_url(self):
        starting_string = "https://example.com/path"
        protocol, domain, path = zap_as_multi("://", "/", src=starting_string, unpack_val=3, replace=",", func=str)
        assert (protocol, domain, path) == ("https", "example.com", "path")

    def test_zap_as_multi_with_custom_func(self):
        def custom_func(s: str) -> str:
            return s.upper()

        result = zap_as_multi("-", "/", ".", src="a-b/c.d", unpack_val=4, replace=",", func=custom_func)
        assert result == ("A", "B", "C", "D")
        assert all(isinstance(x, str) for x in result)

    def test_zap_as_multi_order_matters(self):
        """Test that replacement order affects results."""
        # Order matters: replace "abc" first vs "ab" first
        result1 = zap_as_multi("abc", "ab", src="abcdef", unpack_val=2, replace=",", sorting="order")
        result2 = zap_as_multi("ab", "abc", src="abcdef", unpack_val=2, replace=",", sorting="order")
        assert result1 != result2

        # if we do it by length, they should be the same
        result1 = zap_as_multi("abc", "ab", src="abcdef", unpack_val=2, replace=",", sorting="length")
        result2 = zap_as_multi("ab", "abc", src="abcdef", unpack_val=2, replace=",", sorting="length")
        assert result1 == result2

    def test_zap_as_multi_overlapping_patterns(self):
        """Test overlapping patterns don't interfere."""
        result = zap_as_multi("//", "/", src="https://example.com//path", unpack_val=3, replace=",")
        assert len(result) == 3

    def test_zap_as_multi_empty_patterns(self):
        """Test behavior with empty patterns."""
        result = zap_as_multi("", "//", src="https://example.com", unpack_val=2, replace="|")
        assert result == ("https:", "example.com")

    def test_zap_as_multi_complex_separators(self):
        """Test with complex multi-character separators."""
        data = "item1::sep::item2::sep::item3"
        result = zap_as_multi("::sep::", ".", src=data, unpack_val=3, replace=",")
        assert result == ("item1", "item2", "item3")

    def test_zap_as_multi_nested_patterns(self):
        """Test patterns that contain other patterns."""
        result = zap_as_multi("()", "(", ")", src="(a)(b)(c)", unpack_val=3, replace=",", filter_start=True)
        assert result == ("a", "b", "c")

    def test_zap_as_multi_int_conversion(self):
        """Test multi-pattern with int conversion."""
        version_string = "v1.2.3-beta+build"
        result_string = zap("v", version_string, replace="")
        major, minor, patch = zap_as_multi("-", "+", src=result_string, unpack_val=3, replace=".", func=int)
        assert (major, minor, patch) == (1, 2, 3)

    def test_zap_as_multi_regex_mode(self):
        """Test multi-pattern with regex enabled."""
        result = zap_as_multi(r"\d+", r"[a-z]+", src="123abc456def", unpack_val=2, replace="|", regex=True)
        # Should handle regex patterns

    def test_zap_as_multi_no_matches(self):
        """Test when patterns don't exist in source."""
        result = zap_as_multi("xyz", "123", src="hello world", unpack_val=1, replace="|")
        assert result == ("hello world",)

    def test_zap_as_multi_case_sensitivity(self):
        """Test case-sensitive pattern matching."""
        result = zap_as_multi("HTTP", "://", src="https://example.com", unpack_val=2, replace="|")
        assert result == ("https", "example.com")
