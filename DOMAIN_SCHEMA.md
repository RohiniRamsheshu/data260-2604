# Domain Schema — Open-Source Package Vulnerabilities

## Entity: Vulnerability Report

| Field           | Type          | Required | Description                                      |
|-----------------|---------------|----------|---------------------------------------------------|
| package_name    | text          | yes      | Name of the affected open-source package (primary)|
| affected_version| text          | yes      | Version number where the vulnerability exists      |
| submitter_email | email         | yes      | Email of the person reporting the vulnerability     |
| description     | textarea      | yes      | Details of the vulnerability (min 25 characters)    |
| severity        | dropdown      | yes      | One of: Low, Medium, High, Critical                |
| terms_agreed    | checkbox      | yes      | Confirms agreement to terms and conditions          |

## Category Values (severity dropdown)
- Low
- Medium
- High
- Critical
