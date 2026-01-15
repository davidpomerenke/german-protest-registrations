# FragDenStaat Requests - Complete Discussion History

## Summary

Successfully fetched complete discussion history for **65 Freedom of Information requests** related to demonstration/protest data from German authorities.

### Data Collection Details

- **Fetch Date**: 2026-01-14 03:16:46
- **Output File**: `/tmp/claude/-home-david/e23e4074-d2d1-4b0b-b92f-595578c2f098/scratchpad/user_requests_discussion_history.json`
- **File Size**: 1.1 MB
- **Total Lines**: 11,435
- **Search Criteria**: "demonstration csv" from December 2022 onwards
- **Source**: Based on German Protest Registrations dataset (https://zenodo.org/records/10094245)

## Request Statistics

### Status Breakdown
- **Resolved**: 61 requests
- **Asleep**: 4 requests

### Resolution Breakdown
- **Successful**: 41 requests (63%)
- **Not Held**: 9 requests (14%)
- **Refused**: 5 requests (8%)
- **No Resolution**: 4 requests (6%)
- **User Withdrew (Costs)**: 2 requests (3%)
- **User Withdrew**: 2 requests (3%)
- **Partially Successful**: 2 requests (3%)

### Temporal Distribution
- **2022**: 7 requests
- **2023**: 33 requests
- **2024**: 25 requests

## Communication Statistics

- **Total Messages**: 349
- **Total Attachments**: 96
- **Average Messages per Request**: 5.4
- **Requests with Costs**: 8
- **Total Costs**: €1,107.49

## Public Bodies Contacted

40 different public bodies were contacted across Germany. Top 15:

1. Polizei Berlin - 5 requests
2. Polizeipräsidium Dortmund - 3 requests
3. Polizeipräsidium Köln - 2 requests
4. Ordnungsamt Stadt Frankfurt am Main - 2 requests
5. Stadtverwaltung München - 2 requests
6. Polizeipräsidium Brandenburg - 2 requests
7. Landeshauptstadt Wiesbaden - 2 requests
8. Polizeiinspektion Magdeburg - 2 requests
9. Landeshauptstadt Mainz - 2 requests
10. Landeshauptstadt Saarbrücken - 2 requests
11. Landeshauptstadt Kiel - 2 requests
12. Stadt Erfurt - 2 requests
13. Polizeipräsidium Duisburg - 2 requests
14. Stadt Augsburg - 2 requests
15. Polizei Hamburg - 2 requests

## Data Structure

Each request includes:

### Request Metadata
- Request ID, title, URL, slug
- Status and resolution
- Creation date, due date, last message date
- Costs and refusal reasons
- Tags and summary

### Public Body Information
- Name, email, address
- Jurisdiction details
- Classification

### Complete Message Thread
For each message:
- Message ID, URL, timestamp
- Subject and content (full text)
- Sender and recipient information
- Message type (email/postal)
- Status updates

### Attachments
For each attachment:
- Attachment ID, name, file type, size
- File URL and site URL
- Approval and redaction status
- PDF conversion information

## Cities Covered

The requests cover demonstration data from major German cities including:

- Berlin
- München (Munich)
- Köln (Cologne)
- Hamburg
- Frankfurt
- Stuttgart
- Dortmund
- Duisburg
- Dresden
- Hannover
- Leipzig
- Bremen
- Nürnberg (Nuremberg)
- Augsburg
- Wiesbaden
- Mainz
- Potsdam
- Kiel
- Erfurt
- Magdeburg
- Saarbrücken
- Karlsruhe
- Freiburg
- Mannheim
- Wuppertal
- Flensburg
- Bochum
- Chemnitz
- Rostock
- Halle
- Schwerin
- And others

## Notable Findings

1. **Success Rate**: 63% of requests were successful in obtaining the requested data
2. **Costs**: Most requests were processed for free, but 8 requests incurred costs totaling over €1,100
3. **Response Time**: Average of 5.4 messages per request indicates multiple rounds of communication
4. **Data Quality**: Most authorities provided data in machine-readable formats (CSV/Excel) when successful
5. **Transparency Variation**: Some states/cities were more cooperative than others, with some refusing access or not having the data

## Usage

The JSON file can be processed programmatically to:
- Extract specific requests by city, date, or status
- Analyze communication patterns between requesters and authorities
- Track success rates by jurisdiction
- Download attachments for further analysis
- Generate statistics on protest data availability across Germany

## Context

These Freedom of Information requests were made to obtain official records of protest registrations from demonstration authorities across Germany. The data is part of the German Protest Registrations dataset, which provides unprecedented detail on protest events in Germany from 2012-2024, compiled from official sources rather than newspaper reports.

## Related Links

- German Protest Registrations Dataset: https://zenodo.org/records/10094245
- FragDenStaat Platform: https://fragdenstaat.de
- Project Repository: https://github.com/davidpomerenke/german-protest-registrations
