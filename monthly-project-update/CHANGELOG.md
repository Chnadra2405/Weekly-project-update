# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- Add the monthly project update MVP with managed attachments, idempotent SMTP delivery, persisted status, and an accessible React form.

### Changed

- Replace PostgreSQL persistence with SQL Server 2022 and ODBC Driver 18 support.
- Replace free-text team/project entry with a fixed project dropdown.
- Replace monthly reporting with an exact seven-day weekly reporting period and display the persisted record after submission.

### Removed

- Remove employee identity, supporting files, SMTP delivery, delivery status, and their persisted legacy data.