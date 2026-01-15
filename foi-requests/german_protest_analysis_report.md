# German Protest Registrations Dataset: Comprehensive Analysis

**Author:** Analysis of David Pomerenke's dataset
**Date:** January 12, 2026
**Repository:** https://github.com/davidpomerenke/german-protest-registrations
**DOI:** 10.5281/zenodo.10094245

## Executive Summary

This report provides a comprehensive analysis of the German Protest Registrations Dataset, examining the data quality, processing methods, and challenges for each of the 19 cities where Freedom of Information requests were submitted. The dataset covers **57,010 protest events** across **16 successfully processed cities** from **2012-2022**.

**Key Findings:**
- **Successfully Processed:** 16 cities with usable data
- **Excluded:** 3 cities (Augsburg, Mannheim, Dortmund) due to data quality issues
- **Best Quality:** Berlin and Magdeburg (both registered and actual participant counts)
- **Longest Coverage:** Erfurt (2012-2022, 11 years)
- **Most Records:** Berlin (28,078 events)
- **Organizer Information:** Only 4 cities (Erfurt, München, Wiesbaden, Wuppertal)

---

## Methodology Overview

### Data Retrieval
- 32 FOI requests sent to German demonstration authorities
- 19 partially or completely successful responses
- Data obtained through FragDenStaat.de platform
- Requests sent December 2022 - July 2023

### Processing Challenges
1. **Format Diversity:** PDF, CSV, XLSX, XLS formats
2. **Column Name Inconsistency:** 10+ variations for same field in some cities
3. **Structural Issues:** Unnamed columns, multi-dataset files, cell color encoding
4. **Date Parsing:** 90% automated (dateparser library), 9% regex, 1% manual
5. **Participant Numbers:** Complex regex + manual coding for ranges and specifiers

---

## City-by-City Analysis

### 1. Berlin
**Region:** Berlin | **Years:** 2018-2022 | **Records:** 28,078 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#265731](https://fragdenstaat.de/anfrage/demonstrationen-in-den-jahren-2020-2022/)

**Data Quality:** ⭐⭐⭐⭐⭐ Excellent
- **Fields Available:** date, topic, participants_registered, participants_actual, start_time, end_time, street, zip code, route
- **Unique Features:**
  - Only city with complete location details (street, number, zip)
  - Has time ranges for events
  - Both ex-ante and ex-post participant counts
- **Format:** CSV (2020), XLSX (other years)

**Processing Notes:**
- Most comprehensive dataset
- Handles file overlap by cutting off 2020 data at July 1st
- Fixes 24:00 time format to 23:59
- Clean conversion with minimal issues

**Code Idiosyncrasies:**
```python
# Temporal deduplication between overlapping files
df = df[pd.to_datetime(df["event_date"]) < pd.to_datetime("2020-07-01")]

# Time format fix
df["start"] = df["start"].str.replace("24:00", "23:59")
```

---

### 2. München (Munich)
**Region:** Bayern | **Years:** 2018-2022 | **Records:** 6,841 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#265859](https://fragdenstaat.de/anfrage/demonstrationen-in-den-jahren-2020-2022-2/)

**Data Quality:** ⭐⭐⭐⭐ Very Good
- **Fields Available:** date, topic, organizer, location, participants_registered
- **Unique Features:**
  - **Cancelled event detection via Excel cell color** (red = cancelled)
  - Organizer information available
  - Multiple worksheets per file (monthly organization)
- **Format:** XLSX

**Processing Notes:**
- Uses openpyxl library to inspect cell formatting
- Reads font color to determine event status
- Most creative data extraction technique in the dataset

**Code Idiosyncrasies:**
```python
# Detect cancelled events by red font color
cancelled = pd.Series([isinstance(cell.font.color.rgb, str)
                       for cell in sheet["A:A"][3:]])
df_ = df[~cancelled]
```

---

### 3. Dresden
**Region:** Sachsen | **Years:** 2020-2022 | **Records:** 861 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#266526](https://fragdenstaat.de/anfrage/demonstrationen-in-dresden/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date, topic, location, participants_registered
- **Format:** XLSX converted to CSV

**Processing Notes:**
- Straightforward processing
- Location field explicitly labeled as "exclusively Dresden"
- Standard field mapping

---

### 4. Erfurt
**Region:** Thüringen | **Years:** 2012-2022 | **Records:** 2,897 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268576](https://fragdenstaat.de/anfrage/demonstrationen-in-erfurt/)

**Data Quality:** ⭐⭐⭐ Good (despite format issues)
- **Fields Available:** date, topic, organizer, location
- **Missing:** Participant numbers (neither registered nor actual)
- **Unique Features:**
  - **Longest historical coverage** (starts 2012)
  - Organizer information
- **Format:** XLSX converted to CSV

**Processing Notes:**
- **Most inconsistent column names** in the dataset
- Maps 10+ variations of the same field
- Column names contain newlines and varied abbreviations

**Code Idiosyncrasies:**
```python
# Handles numerous column name variations
columns={
    "Datum der Vers.": "event_date",
    "Datum der Versammlung": "event_date",
    "Datum der\\nVersammlung": "event_date",  # with newline!
    "Veranstalter/Vertreter": "organizer",
    "Versammlungsanmelder": "organizer",
    "Versammlungsmelder": "organizer",
    # ... and more variations
}
```

---

### 5. Magdeburg
**Region:** Sachsen-Anhalt | **Years:** 2015-2022 | **Records:** 2,057 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268459](https://fragdenstaat.de/anfrage/demonstrationen-in-magdeburg/)

**Data Quality:** ⭐⭐⭐ Good (poor structure, but rich data)
- **Fields Available:** date, topic, location, participants_registered, participants_actual
- **Unique Features:**
  - One of only **2 cities with actual participant counts** (with Berlin)
  - Longest coverage among non-capital cities
- **Format:** XLSX converted to CSV

**Processing Notes:**
- **Poor CSV structure:** Missing column headers
- Uses "Unnamed: 6" and "Unnamed: 7" for participant columns
- Skips second row (likely header in German)
- Contains duplicates (removed by keeping last)

**Code Idiosyncrasies:**
```python
# Skip problematic second row
df = df.iloc[1:]

# Map unnamed columns
"Unnamed: 6": "participants_registered",  # TN angemeldet
"Unnamed: 7": "participants_actual",      # TN anwesend

# Remove duplicates
df = df.drop_duplicates(subset=["event_date", "topic", "location"], keep="last")
```

---

### 6. Mainz
**Region:** Rheinland-Pfalz | **Years:** 2018-2022 | **Records:** 1,531 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268573](https://fragdenstaat.de/anfrage/demonstrationen-in-mainz/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date, topic, location, participants_registered
- **Format:** XLSX converted to CSV

**Processing Notes:**
- Skips first 2 rows, then skips row 1 again
- Drops sequence number column ('Lfd Nr.')
- Column name with newline: 'Datum\n'

---

### 7. Freiburg
**Region:** Baden-Württemberg | **Years:** 2013-2022 | **Records:** 3,165 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#269444](https://fragdenstaat.de/anfrage/demonstrationen-in-freiburg/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date, topic, location
- **Missing:** Participant numbers, organizer
- **Format:** XLSX converted to CSV (separate files per year)

**Processing Notes:**
- Simple, clean structure
- 10 separate annual files (2013-2022)
- No participant data available

---

### 8. Karlsruhe
**Region:** Baden-Württemberg | **Years:** 2021-2022 | **Records:** 954 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#269443](https://fragdenstaat.de/anfrage/demonstrationen-in-karlsruhe/)

**Data Quality:** ⭐⭐⭐⭐ Very Good
- **Fields Available:** date, topic, location, participants_registered, cancelled status
- **Unique Features:** Explicit cancellation flag ('Absage' column with 'x')
- **Format:** XLSX converted to CSV

**Processing Notes:**
- Filters out cancelled events
- Skips first row
- Clean structure

**Code Idiosyncrasies:**
```python
# Filter cancelled events
df = df[df["cancelled"] != "x"]
```

---

### 9. Potsdam
**Region:** Brandenburg | **Years:** 2019-2022 | **Records:** 1,064 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268447](https://fragdenstaat.de/anfrage/demonstrationen-in-potsdam/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date, time, city, topic, participants_registered, location
- **Unique Features:** Time information, no column headers in source
- **Format:** PDF + XLSX converted to CSV

**Processing Notes:**
- **No headers in source files** - columns assigned manually by position
- Both PDF and XLSX versions available
- Has time information

**Code Idiosyncrasies:**
```python
# Manual column assignment (no headers in file)
df.columns = [
    "event_date", "event_time", "city", "topic",
    "participants_registered", "location"
]
```

---

### 10. Wiesbaden
**Region:** Hessen | **Years:** 2019-2022 | **Records:** 952 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268455](https://fragdenstaat.de/anfrage/demonstrationen-in-wiesbaden/)

**Data Quality:** ⭐⭐⭐⭐ Very Good
- **Fields Available:** date, organizer, topic, location, participants_registered
- **Unique Features:** Organizer field with format "Organisation / verantwortliche Person"
- **Format:** XLSX converted to CSV

**Processing Notes:**
- Skips first 2 rows
- Drops rows without dates
- Clean structure with organizer info

---

### 11. Kiel
**Region:** Schleswig-Holstein | **Years:** 2021-2022 | **Records:** 602 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268575](https://fragdenstaat.de/anfrage/demonstrationen-in-kiel/)

**Data Quality:** ⭐⭐ Fair
- **Fields Available:** date, topic, location, participants_registered
- **Format:** XLSX converted to CSV

**Processing Notes:**
- **Inconsistent file structures**
- File '2022_2020.csv' is skipped entirely
- File '2022_2021.csv' requires skiprows=1
- Other files use standard format

**Code Idiosyncrasies:**
```python
# Different handling per file
if file.name == "2022_2020.csv":
    continue  # Skip this file
elif file.name == "2022_2021.csv":
    df = pd.read_csv(file, skiprows=1)  # Special handling
else:
    df = pd.read_csv(file)  # Standard
```

---

### 12. Wuppertal
**Region:** Nordrhein-Westfalen | **Years:** 2022 only | **Records:** 207 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#269446](https://fragdenstaat.de/anfrage/demonstrationen-in-wuppertal/)

**Data Quality:** ⭐⭐⭐⭐ Very Good
- **Fields Available:** date, organizer, topic, location, participants_registered
- **Unique Features:** Already in CSV format, organizer information
- **Format:** CSV

**Processing Notes:**
- Only 2022 data available
- Native CSV format (no conversion needed)
- Clean structure

---

### 13. Saarbrücken
**Region:** Saarland | **Years:** 2021-2022 | **Records:** 633 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268574](https://fragdenstaat.de/anfrage/demonstrationen-in-saarbruecken/)

**Data Quality:** ⭐⭐ Fair (complex structure)
- **Fields Available:** date, topic, location, participants_registered
- **Unique Features:** **Two datasets side-by-side** in each file
- **Format:** XLS converted to CSV

**Processing Notes:**
- **Most complex structure in dataset**
- Each file contains TWO separate datasets:
  - Columns 0:9 = Gatherings ("Versammlungen")
  - Columns 9: = Marches ("Aufzüge")
- Different column names for each dataset type
- Cleans 'erl.' prefix from dates

**Code Idiosyncrasies:**
```python
# Split file into two datasets
df1 = df.iloc[:, :9]   # Gatherings
df2 = df.iloc[:, 9:]   # Marches

# Clean date markers
df["event_date"] = df["event_date"].str.replace("erl.", "").str.strip()
```

---

### 14. Köln (Cologne)
**Region:** Nordrhein-Westfalen | **Years:** 2018, 2022 | **Records:** 2,112 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#265868](https://fragdenstaat.de/anfrage/demonstrationen-in-koeln/)

**Data Quality:** ⭐⭐⭐ Good (format issues)
- **Fields Available:** date, topic, location, participants_registered
- **Coverage Gap:** Only 2018 and 2022 (no 2019-2021)
- **Format:** PDF + XLSX converted to CSV

**Processing Notes:**
- **Large temporal gap** in coverage
- Multiple column name variations with embedded newlines
- Inconsistent spacing in column names

**Code Idiosyncrasies:**
```python
columns={
    "Zahl der Teilnehm er / -\\ninnen": "participants_registered",
    "erwartete TN-Zahl\\n": "participants_registered",
    "Datum\\n": "event_date",
}
```

---

### 15. Duisburg
**Region:** Nordrhein-Westfalen | **Years:** 2016-2022 | **Records:** 2,110 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#268602](https://fragdenstaat.de/anfrage/demonstrationen-in-duisburg/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date, topic, location, participants_registered
- **Unique Features:** Requires data cleaning for invalid dates
- **Format:** XLSX converted to CSV

**Processing Notes:**
- Contains invalid date entries (dashes, question marks)
- Requires regex cleaning

**Code Idiosyncrasies:**
```python
# Remove placeholder dates
df["event_date"] = df["event_date"].str.replace(
    r"^\\s*(-|\\?)+\\s*$", "", regex=True
)
```

---

### 16. Bremen
**Region:** Bremen | **Years:** 2019-2022 | **Records:** 2,641 | **Status:** ✅ Resolved

**FragDenStaat Request:** [#270596](https://fragdenstaat.de/anfrage/demonstrationen-in-bremen-1/)

**Data Quality:** ⭐⭐⭐ Good
- **Fields Available:** date_start, date_end, topic, location
- **Missing:** Participant numbers
- **Unique Features:** Start and end dates for multi-day events
- **Format:** CSV

**Processing Notes:**
- Has both start (Beginn) and end (Ende) dates
- Cleans 'NV' markers from date fields
- No participant data

**Code Idiosyncrasies:**
```python
# Clean date markers
df["event_date"] = df["event_date"].str.replace("NV", "")
df["event_date_end"] = df["event_date_end"].str.replace("NV", "")
```

---

## Excluded Cities

### 17. Dortmund ❌
**Region:** Nordrhein-Westfalen | **Years:** 2019-2022 | **Status:** ✅ Resolved (but excluded)

**FragDenStaat Request:** [#268577](https://fragdenstaat.de/anfrage/demonstrationen-in-dortmund/)

**Exclusion Reason:** **No topic information**

**Processing Notes:**
- Data exists with dates, locations, and participant numbers
- Excluded because **topics are a required field**
- Code comment indicates topics will be available starting 2023
- Returns empty DataFrame

```python
def dortmund():
    # Dortmund does not have topics
    # but starting from 2023 they will have them!
    # ... code to read data ...
    return pd.DataFrame()  # Excluded
```

---

### 18. Augsburg ❌
**Region:** Bayern | **Years:** 2022 | **Status:** ✅ Resolved (but excluded)

**FragDenStaat Request:** [#268603](https://fragdenstaat.de/anfrage/demonstrationen-in-augsburg/)

**Exclusion Reason:** **Cannot convert PDF to CSV**

**Processing Notes:**
- PDF file cannot be processed by automated tools
- Both PDF and XLSX versions provided, but conversion fails
- Returns empty DataFrame

```python
def augsburg():
    return pd.DataFrame()
```

---

### 19. Mannheim ❌
**Region:** Baden-Württemberg | **Years:** 2022 | **Status:** ✅ Resolved (but excluded)

**FragDenStaat Request:** [#269440](https://fragdenstaat.de/anfrage/demonstrationen-in-mannheim/)

**Exclusion Reason:** **Poorly structured data**

**Processing Notes:**
- XLS file exists and converts to CSV
- Data structure is too problematic to parse reliably
- Returns empty DataFrame despite file reading

```python
def mannheim():
    # ... code reads file ...
    return pd.DataFrame()  # Too poorly structured
```

---

## Data Quality Summary

### By Field Availability

| Field | Cities with Data | Percentage |
|-------|-----------------|------------|
| Date | 16/16 | 100% |
| Topic | 16/16 | 100% |
| Location | 16/16 | 100% |
| Participants (Registered) | 13/16 | 81% |
| Participants (Actual) | 2/16 | 13% |
| Organizer | 4/16 | 25% |
| Time Information | 2/16 | 13% |

### By Coverage Period

| Period | Cities | Notes |
|--------|--------|-------|
| 2012-2022 | 1 | Erfurt only |
| 2015-2022 | 1 | Magdeburg |
| 2016-2022 | 1 | Duisburg |
| 2018-2022 | 5 | Core consistent dataset |
| 2019-2022 | 4 | |
| 2020-2022 | 2 | |
| 2021-2022 | 2 | |
| 2022 only | 1 | Wuppertal |

### By Data Quality Rating

| Rating | Cities | Names |
|--------|--------|-------|
| ⭐⭐⭐⭐⭐ (5/5) | 1 | Berlin |
| ⭐⭐⭐⭐ (4/5) | 4 | München, Karlsruhe, Wiesbaden, Wuppertal |
| ⭐⭐⭐ (3/5) | 9 | Dresden, Erfurt, Magdeburg, Mainz, Freiburg, Potsdam, Köln, Duisburg, Bremen |
| ⭐⭐ (2/5) | 2 | Kiel, Saarbrücken |
| ❌ Excluded | 3 | Dortmund, Augsburg, Mannheim |

---

## Processing Challenges & Solutions

### 1. Column Name Variations
**Problem:** Same field has 5-10 different column names across files
**Solution:** Extensive column mapping dictionaries in each reader

**Example (Erfurt):**
```python
"Datum der Vers.": "event_date",
"Datum der Versammlung": "event_date",
"Datum der\\nVersammlung": "event_date",  # newline embedded!
```

### 2. Missing Column Headers
**Problem:** Files lack proper headers
**Solution:** Manual column assignment by position (Potsdam) or use of "Unnamed" pandas defaults (Magdeburg)

### 3. Multi-Dataset Files
**Problem:** Single file contains multiple independent datasets
**Solution:** Column slicing to separate datasets (Saarbrücken)

### 4. Metadata in Cell Formatting
**Problem:** Cancellation status encoded in Excel cell color
**Solution:** openpyxl library to inspect cell formatting (München)

### 5. Invalid Date Values
**Problem:** Dashes, question marks, or text markers in date fields
**Solution:** Regex-based cleaning (Duisburg, Bremen, Saarbrücken)

### 6. File Format Inconsistencies
**Problem:** Different files from same city require different parsing
**Solution:** File-specific conditionals (Kiel)

---

## Code Patterns & Technical Observations

### Common Processing Pattern
```python
def city_name():
    path = data / "interim/csv/CityName"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(columns={...})  # City-specific mapping
        # City-specific cleaning
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "CityName"
    df["region"] = "RegionName"
    df["is_regional_capital"] = True/False
    return df
```

### Special Techniques Used

1. **Excel Color Detection** (München):
   ```python
   cancelled = pd.Series([isinstance(cell.font.color.rgb, str)
                          for cell in sheet["A:A"][3:]])
   ```

2. **Column Slicing** (Saarbrücken):
   ```python
   df1 = df.iloc[:, :9]   # First dataset
   df2 = df.iloc[:, 9:]   # Second dataset
   ```

3. **Temporal Deduplication** (Berlin):
   ```python
   df = df[pd.to_datetime(df["event_date"]) < pd.to_datetime("2020-07-01")]
   ```

4. **Manual Column Assignment** (Potsdam):
   ```python
   df.columns = ["event_date", "event_time", "city", "topic",
                 "participants_registered", "location"]
   ```

---

## Recommendations

### For Future Data Collection

1. **Standardize Requests:** Use template requesting specific column format
2. **Request CSV:** Explicitly ask for CSV format to avoid PDF conversion issues
3. **Column Headers:** Request files with English or standardized German headers
4. **Metadata Separation:** Request cancellation/status flags as separate columns, not formatting

### For Dataset Users

1. **Use Filtered Subsets:**
   - 2018-2022 dataset for temporal analysis
   - 2022 dataset for geographic analysis
   - Avoid unfiltered dataset for direct analysis

2. **Be Aware of Limitations:**
   - Registration ≠ actual attendance (except Berlin, Magdeburg)
   - Not all protests are registered
   - Geographic coverage limited to 16 cities
   - Organizer info only in 4 cities

3. **Quality Tiers:**
   - **Tier 1** (Best): Berlin, München - use for detailed analysis
   - **Tier 2** (Good): 4-star and 3-star cities - reliable for most purposes
   - **Tier 3** (Use with caution): 2-star cities - structural issues

---

## Conclusions

This dataset represents a **significant achievement** in protest research, providing official registration data at unprecedented scale. The processing involved:

- **19 custom parsers** for different city formats
- **Complex data cleaning** (regex, manual coding, format detection)
- **Creative solutions** (Excel color inspection, column slicing)
- **Robust handling** of inconsistent data structures

### Key Strengths
✅ **57,010 events** - largest German protest dataset
✅ **Official data** - avoids media selection bias
✅ **Rich metadata** - topics always available
✅ **Long temporal coverage** - up to 11 years (Erfurt)
✅ **Actual attendance** - available for Berlin & Magdeburg

### Key Limitations
⚠️ **Limited geography** - only 16 cities (85%+ population not covered)
⚠️ **Registered only** - unregistered protests excluded
⚠️ **Inconsistent timeframes** - requires careful subsetting
⚠️ **Participant data gaps** - not available in all cities

The dataset exemplifies both the **promise and challenges** of using Freedom of Information requests for systematic data collection. While data quality varies significantly, the successful cities provide valuable insights into protest activity in Germany.

---

## Sources & References

- **Dataset Repository:** https://github.com/davidpomerenke/german-protest-registrations
- **DOI:** https://doi.org/10.5281/zenodo.10094245
- **FragDenStaat Platform:** https://fragdenstaat.de/
- **FOI Requests:** All requests viewable at FragDenStaat with original documents
- **Report:** Available in repository as report.qmd and compiled PDF

---

**Report Generated:** January 12, 2026
**Analysis Tool:** Automated analysis of repository code and documentation
