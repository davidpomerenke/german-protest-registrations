"""Quality assurance tests for the German Protest Registrations dataset."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

# Project root
ROOT = Path(__file__).parent.parent


class TestDataIntegrity:
    """Tests for data integrity across all datasets."""

    @pytest.fixture
    def processed_data(self):
        """Load the main processed dataset."""
        path = ROOT / "data" / "processed" / "german_protest_registrations_17_cities_unfiltered.csv"
        if not path.exists():
            pytest.skip("Processed data file not found")
        return pd.read_csv(path)

    def test_no_empty_dataset(self, processed_data):
        """Dataset should contain records."""
        assert len(processed_data) > 0, "Dataset is empty"

    def test_required_columns_exist(self, processed_data):
        """All required columns should be present."""
        required = ["region", "city", "date", "topic"]
        for col in required:
            assert col in processed_data.columns, f"Missing required column: {col}"

    def test_no_missing_cities(self, processed_data):
        """City column should have no missing values."""
        assert processed_data["city"].notna().all(), "Found missing city values"

    def test_no_missing_dates(self, processed_data):
        """Date column should have no missing values."""
        assert processed_data["date"].notna().all(), "Found missing date values"

    def test_valid_date_format(self, processed_data):
        """All dates should be parseable."""
        def is_valid_date(d):
            try:
                pd.to_datetime(d)
                return True
            except Exception:
                return False

        invalid = ~processed_data["date"].apply(is_valid_date)
        assert not invalid.any(), f"Found {invalid.sum()} invalid dates"

    def test_dates_in_expected_range(self, processed_data):
        """Dates should be within 2010-2025 range."""
        dates = pd.to_datetime(processed_data["date"])
        min_date = datetime(2010, 1, 1)
        max_date = datetime(2025, 12, 31)

        too_early = dates < min_date
        too_late = dates > max_date

        assert not too_early.any(), f"Found {too_early.sum()} dates before 2010"
        assert not too_late.any(), f"Found {too_late.sum()} dates after 2025"

    def test_cities_are_known(self, processed_data):
        """All cities should be from the known list."""
        known_cities = {
            "Berlin", "München", "Köln", "Dresden", "Bremen", "Freiburg",
            "Mainz", "Erfurt", "Kiel", "Magdeburg", "Karlsruhe", "Wiesbaden",
            "Duisburg", "Saarbrücken", "Dortmund", "Wuppertal", "Potsdam"
        }
        actual_cities = set(processed_data["city"].unique())
        unknown = actual_cities - known_cities
        assert not unknown, f"Found unknown cities: {unknown}"

    def test_regions_match_cities(self, processed_data):
        """Each city should have consistent region mapping."""
        city_regions = processed_data.groupby("city")["region"].nunique()
        inconsistent = city_regions[city_regions > 1]
        assert inconsistent.empty, f"Cities with inconsistent regions: {list(inconsistent.index)}"

    def test_exact_duplicates_warning(self, processed_data):
        """Warn about exact duplicate rows (but allow some)."""
        duplicates = processed_data.duplicated()
        dupe_count = duplicates.sum()
        dupe_rate = dupe_count / len(processed_data)
        # Allow up to 10% exact duplicates (legacy data issue)
        assert dupe_rate < 0.10, f"Too many exact duplicates: {dupe_count} ({dupe_rate:.1%})"
        if dupe_count > 0:
            import warnings
            warnings.warn(f"Found {dupe_count} exact duplicate rows ({dupe_rate:.1%})")

    def test_minimal_near_duplicates(self, processed_data):
        """Check near-duplicates (same city, date, topic)."""
        key_cols = ["city", "date", "topic"]
        duplicates = processed_data.duplicated(subset=key_cols)
        dupe_rate = duplicates.sum() / len(processed_data)
        # Allow up to 15% near-duplicates (some legitimate repeat events with different details)
        assert dupe_rate < 0.15, f"Near-duplicate rate too high: {dupe_rate:.1%}"

    def test_participant_counts_valid(self, processed_data):
        """Participant counts should be non-negative when present."""
        for col in ["participants_registered", "participants_actual"]:
            if col in processed_data.columns:
                valid = processed_data[col].isna() | (processed_data[col] >= 0)
                assert valid.all(), f"Found negative values in {col}"


class TestReaders:
    """Tests for individual city readers."""

    def _import_reader(self, name):
        """Import a specific reader module."""
        import importlib
        try:
            module = importlib.import_module(f"src.german_protest_registrations.readers.{name}")
            return module
        except ImportError:
            return None

    def test_berlin_reader(self):
        """Berlin reader should produce valid DataFrame."""
        module = self._import_reader("berlin")
        if module is None:
            pytest.skip("Berlin reader not found")
        df = module.berlin()
        assert len(df) > 0, "Berlin reader returned empty data"
        assert "event_date" in df.columns or "date" in df.columns

    def test_munich_reader(self):
        """München reader should produce valid DataFrame."""
        module = self._import_reader("muenchen")
        if module is None:
            pytest.skip("München reader not found")
        df = module.muenchen()
        assert len(df) > 0, "München reader returned empty data"

    def test_cologne_reader(self):
        """Köln reader should produce valid DataFrame."""
        module = self._import_reader("koeln")
        if module is None:
            pytest.skip("Köln reader not found")
        df = module.koeln()
        assert len(df) > 0, "Köln reader returned empty data"

    def test_all_readers_return_dataframes(self):
        """All reader functions should return DataFrames."""
        reader_names = [
            "berlin", "muenchen", "koeln", "dresden", "bremen", "freiburg",
            "mainz", "erfurt", "kiel", "magdeburg", "karlsruhe", "wiesbaden",
            "duisburg", "saarbruecken", "potsdam"
        ]
        for name in reader_names:
            module = self._import_reader(name)
            if module and hasattr(module, name):
                func = getattr(module, name)
                result = func()
                assert isinstance(result, pd.DataFrame), f"{name}() should return DataFrame"


class TestPipeline:
    """Tests for the data processing pipeline."""

    @pytest.fixture
    def unify_module(self):
        """Import the unify module."""
        try:
            from src.german_protest_registrations import unify
            return unify
        except ImportError:
            pytest.skip("Unify module not found")

    def test_unify_function_exists(self, unify_module):
        """Unify module should have main functions."""
        assert hasattr(unify_module, "get_all_datasets")

    def test_output_files_exist(self):
        """Expected output files should exist."""
        expected_files = [
            "german_protest_registrations_17_cities_unfiltered.csv",
        ]
        processed_dir = ROOT / "data" / "processed"
        for filename in expected_files:
            path = processed_dir / filename
            assert path.exists(), f"Missing output file: {filename}"


class TestCategorizationSchema:
    """Tests for the categorization schema."""

    @pytest.fixture
    def schema(self):
        """Load the categorization schema."""
        path = ROOT / "categorization_schema.json"
        if not path.exists():
            pytest.skip("Categorization schema not found")
        with open(path) as f:
            return json.load(f)

    def test_schema_has_required_keys(self, schema):
        """Schema should have groups and topics."""
        assert "groups" in schema, "Schema missing 'groups'"
        assert "topics" in schema, "Schema missing 'topics'"

    def test_groups_have_names(self, schema):
        """All groups should have names."""
        for group in schema["groups"]:
            assert "name" in group, f"Group missing name: {group}"
            assert group["name"], "Group has empty name"

    def test_topics_have_names(self, schema):
        """All topics should have names."""
        for topic in schema["topics"]:
            assert "name" in topic, f"Topic missing name: {topic}"
            assert topic["name"], "Topic has empty name"

    def test_no_duplicate_group_names(self, schema):
        """Group names should be unique."""
        names = [g["name"] for g in schema["groups"]]
        assert len(names) == len(set(names)), "Duplicate group names found"

    def test_no_duplicate_topic_names(self, schema):
        """Topic names should be unique."""
        names = [t["name"] for t in schema["topics"]]
        assert len(names) == len(set(names)), "Duplicate topic names found"


class TestVisualization:
    """Tests for the visualization data."""

    @pytest.fixture
    def viz_data(self):
        """Load the visualization data."""
        path = ROOT / "docs" / "data.csv"
        if not path.exists():
            pytest.skip("Visualization data not found")
        return pd.read_csv(path)

    def test_viz_data_not_empty(self, viz_data):
        """Visualization data should contain records."""
        assert len(viz_data) > 0, "Visualization data is empty"

    def test_viz_data_has_required_columns(self, viz_data):
        """Visualization data should have required columns."""
        required = ["region", "city", "date", "topic"]
        for col in required:
            assert col in viz_data.columns, f"Missing column in viz data: {col}"

    def test_viz_data_size_reasonable(self, viz_data):
        """Visualization data should be reasonable size (not truncated)."""
        # Should have at least 50,000 events
        assert len(viz_data) >= 50000, f"Visualization data seems too small: {len(viz_data)}"

    def test_viz_data_has_protest_topics(self, viz_data):
        """Visualization data should have protest_topics column."""
        assert "protest_topics" in viz_data.columns, "Missing protest_topics column"

    def test_protest_topics_valid_json(self, viz_data):
        """All protest_topics values should be valid JSON arrays."""
        invalid_count = 0
        for idx, val in viz_data["protest_topics"].items():
            if pd.notna(val):
                try:
                    parsed = json.loads(val)
                    if not isinstance(parsed, list):
                        invalid_count += 1
                except (json.JSONDecodeError, TypeError):
                    invalid_count += 1

        error_rate = invalid_count / len(viz_data)
        assert error_rate < 0.01, f"Too many invalid protest_topics: {invalid_count} ({error_rate:.1%})"

    def test_protest_topics_coverage(self, viz_data):
        """Most events should have at least one topic categorized."""
        def has_topics(val):
            if pd.isna(val):
                return False
            try:
                parsed = json.loads(val)
                return isinstance(parsed, list) and len(parsed) > 0
            except Exception:
                return False

        has_topic = viz_data["protest_topics"].apply(has_topics)
        coverage = has_topic.sum() / len(viz_data)
        # At least 70% of events should have topics
        assert coverage >= 0.70, f"Topic coverage too low: {coverage:.1%}"


class TestTopicCategories:
    """Tests for topic category consistency."""

    @pytest.fixture
    def schema(self):
        """Load the categorization schema."""
        path = ROOT / "categorization_schema.json"
        if not path.exists():
            pytest.skip("Categorization schema not found")
        with open(path) as f:
            return json.load(f)

    @pytest.fixture
    def viz_constants(self):
        """Parse topic categories from visualization constants.js."""
        path = ROOT / "viz" / "src" / "constants.js"
        if not path.exists():
            pytest.skip("Visualization constants not found")
        content = path.read_text()

        # Extract TOPIC_CATEGORIES array
        import re
        match = re.search(r'export const TOPIC_CATEGORIES = \[(.*?)\];', content, re.DOTALL)
        if not match:
            pytest.skip("Could not parse TOPIC_CATEGORIES from constants.js")

        # Parse the array contents
        array_content = match.group(1)
        topics = re.findall(r'"([^"]+)"', array_content)
        return topics

    def test_schema_topics_match_viz_constants(self, schema, viz_constants):
        """Topics in schema should match visualization constants."""
        schema_topics = set(t["name"] for t in schema["topics"])
        viz_topics = set(viz_constants)

        missing_in_viz = schema_topics - viz_topics
        extra_in_viz = viz_topics - schema_topics

        if missing_in_viz:
            import warnings
            warnings.warn(f"Topics in schema but not in viz: {missing_in_viz}")
        if extra_in_viz:
            import warnings
            warnings.warn(f"Topics in viz but not in schema: {extra_in_viz}")

        # Allow some mismatch but not too much
        total_mismatch = len(missing_in_viz) + len(extra_in_viz)
        assert total_mismatch < 10, f"Too many topic mismatches: {total_mismatch}"

    def test_all_viz_topics_have_colors(self, viz_constants):
        """All topic categories should have a color defined."""
        path = ROOT / "viz" / "src" / "constants.js"
        content = path.read_text()

        # Extract TOPIC_COLORS object
        import re
        colors_match = re.search(r'export const TOPIC_COLORS = \{(.*?)\};', content, re.DOTALL)
        if not colors_match:
            pytest.skip("Could not parse TOPIC_COLORS from constants.js")

        colors_content = colors_match.group(1)
        colored_topics = set(re.findall(r'"([^"]+)":\s*"#', colors_content))

        missing_colors = set(viz_constants) - colored_topics
        if missing_colors:
            import warnings
            warnings.warn(f"Topics without colors: {missing_colors}")

        # Allow a few topics without colors (they'll use default)
        assert len(missing_colors) <= 3, f"Too many topics without colors: {missing_colors}"

    def test_viz_data_topics_mostly_valid(self):
        """Most topic assignments should be from known categories."""
        viz_data_path = ROOT / "docs" / "data.csv"
        constants_path = ROOT / "viz" / "src" / "constants.js"

        if not viz_data_path.exists() or not constants_path.exists():
            pytest.skip("Required files not found")

        # Get valid topics from constants
        import re
        content = constants_path.read_text()
        match = re.search(r'export const TOPIC_CATEGORIES = \[(.*?)\];', content, re.DOTALL)
        valid_topics = set(re.findall(r'"([^"]+)"', match.group(1)))

        # Count topic assignments by validity
        viz_data = pd.read_csv(viz_data_path)
        valid_count = 0
        invalid_count = 0
        all_invalid_topics = set()

        for val in viz_data["protest_topics"].dropna():
            try:
                topics = json.loads(val)
                if isinstance(topics, list):
                    for t in topics:
                        if t in valid_topics:
                            valid_count += 1
                        else:
                            invalid_count += 1
                            all_invalid_topics.add(t)
            except Exception:
                pass

        total = valid_count + invalid_count
        if total > 0:
            valid_rate = valid_count / total
            # At least 60% of topic assignments should be from known categories
            # (GPT-4 generates additional specific topics, which is acceptable)
            assert valid_rate >= 0.60, f"Known topic rate too low: {valid_rate:.1%}"

            if len(all_invalid_topics) > 0:
                import warnings
                warnings.warn(f"Found {len(all_invalid_topics)} unknown topic types ({invalid_count} occurrences, {1-valid_rate:.1%})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
