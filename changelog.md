### Version `4.0.0` - BREAKING CHANGES

**Release Date**: TBD

#### 🚨 Breaking Changes
- **CLI Removed**: The package no longer provides CLI commands. All CLI functionality has been removed.
  - Removed commands: `schedulo`, `schedulo-api`, and all subcommands (`terms`, `subjects`, `courses`, `course`, `professor`, etc.)
  - **Migration**: Use the REST API server instead. Start the server with `schedulo-server` and consume the API via HTTP.

- **Server-Only Entry Point**: The only command-line entry point is now `schedulo-server` to start the REST API server.
  - Old: `schedulo terms carleton`
  - New: Start server with `schedulo-server` and query `GET /universities/carleton/terms`

#### ✨ New Features
- **Standalone Server**: `schedulo-server` command for starting the REST API
  - Options: `--host`, `--port`, `--workers`, `--reload`, `--log-level`
  - Full production-ready server with worker support

#### 🔧 Architecture Changes
- Removed modules: `cli.py`, `cli_old.py`, `cli_tools.py`
- Removed legacy CLI modules from all subpackages
- Updated entry points in `pyproject.toml` and `setup.py`
- Server module now completely standalone without CLI dependencies

#### 📚 Documentation
- Updated README to reflect server-only usage
- All examples now use REST API or Python library
- Added migration guide from CLI to REST API

#### 🎯 Migration Guide
If you were using the CLI:
1. Install the package: `pip install schedulo-api`
2. Start the server: `schedulo-server --port 8000`
3. Access data via REST API: `http://localhost:8000/docs`
4. Or use the Python library directly (see README for examples)

---

### Version `1.0.0dev5`

#### Timetable
- Normalized whitespace in output strings (e.g. replacing `&nbsp;` and `\xa0` with a space)
- Capitalized all standard labels (e.g. subject/course codes, section/component labels, session types, etc.)
except for term, which are lowered (winter, summer, fall)
- Changed `subject`/`course` to `subject_code`/`course_code`
- **N.B.** This may break applications which traverse the JSON structure
- **N.B.** This may break applications which use the standard labels from other sources (or hard-coded)


### Version `1.0.0dev6`

#### Timetable
- Updated tests to match new field names
- Added periodic connection refresh to `TimetableQuery`
- Added check for when queries exceed the maximum number of results allowed by the University
- Updated link to webpage
- Explicitly specify encoding as UTF-8 when saving HTML


### Version `1.0.0dev7`

#### Timetable
- Moved the ability to save queried HTML to `TimetableQuery`
- Improved logging


### Version `1.0.0dev8`
- Added native logging config


### Version `1.0.0dev9`
- Added NullHandler to suppress default logging
- Fixed logging bug

#### Timetable
- Updated tests
- Made `"section_id"`s optional
- Parsed separate case of "No classes found"
- Refresh and retry when unknown errors are encountered


### Version `1.0.0dev10`

#### Timetable
- Improved CLI help pages
- Added ability to search for course code with comparison (less/greater than, in)


### Version `1.0.0dev11`

#### Timetable
- Increased default refresh rate, sleep/wait times
- Changed `"course_number"` to `"course_code"`
- Changed field name from `"courses"` to `"timetables"`
