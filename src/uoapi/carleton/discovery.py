"""
Carleton University course discovery functionality
Adapted from carleton_production_discovery.py to integrate with uoapi
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import logging
import re
import sys

from .models import Course, CourseSection, MeetingTime

logger = logging.getLogger(__name__)


class CarletonDiscovery:
    """Carleton University course discovery system integrated with uoapi"""

    def __init__(self, max_workers=4, cookie_file=None):
        self.max_workers = max_workers
        self.session_template = self._load_cookies(cookie_file)
        self.catalog_data = self._load_catalog()

        # URLs
        self.banner_base = "https://central.carleton.ca/prod"
        self.term_select_url = (
            f"{self.banner_base}/bwysched.p_select_term?wsea_code=EXT"
        )
        self.search_fields_url = f"{self.banner_base}/bwysched.p_search_fields"
        self.course_search_url = f"{self.banner_base}/bwysched.p_course_search"

        # Progress tracking
        self.total_courses = 0
        self.completed_courses = 0
        self.offered_courses = 0
        self.error_courses = 0

        logger.info(f"Carleton Discovery initialized with {max_workers} workers")

    def _load_cookies(self, cookie_file):
        """Load cookies from file"""
        cookies = {}

        # Try different cookie file locations
        cookie_paths = []
        if cookie_file:
            cookie_paths.append(cookie_file)
        cookie_paths.extend(
            ["fresh_cookies.txt", "../fresh_cookies.txt", "../../fresh_cookies.txt"]
        )

        for cookie_path in cookie_paths:
            try:
                with open(cookie_path, "r") as f:
                    for line in f:
                        if line.startswith("#") or not line.strip():
                            continue
                        parts = line.strip().split("\t")
                        if len(parts) >= 7:
                            domain, _, path, _, _, name, value = parts[:7]
                            if domain == "central.carleton.ca":
                                cookies[name] = value
                logger.info(f"Loaded {len(cookies)} cookies from {cookie_path}")
                break
            except FileNotFoundError:
                continue

        if not cookies:
            logger.warning("No cookie file found - using empty cookies")

        return {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "cookies": cookies,
        }

    def _load_catalog(self):
        """Load catalog data"""
        from uoapi.discovery.discovery_service import get_assets_path

        try:
            # Use the discovery service to get the proper assets path
            assets_path = get_assets_path()
            catalog_path = assets_path / "carleton" / "courses.json"

            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                catalog_data = data.get("subjects", {})
                total_courses = sum(len(courses) for courses in catalog_data.values())
                logger.info(
                    f"Loaded catalog: {len(catalog_data)} subjects, "
                    f"{total_courses} courses from {catalog_path}"
                )
                return catalog_data
        except Exception as e:
            logger.warning(f"Failed to load catalog: {e}")

        logger.warning("No catalog file found - using empty catalog")
        return {}

    def _create_session(self):
        """Create new session with cookies"""
        session = requests.Session()
        session.headers.update(self.session_template["headers"])
        session.cookies.update(self.session_template["cookies"])
        return session

    def get_available_terms(self):
        """Get all available terms"""
        session = self._create_session()

        try:
            response = session.get(self.term_select_url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to get available terms: {e}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        form = soup.find("form", action="bwysched.p_search_fields")
        if not form:
            return []

        select_element = form.find("select", attrs={"name": "term_code"})
        if not select_element:
            return []

        terms = []
        for option in select_element.find_all("option"):
            term_code = option.get("value", "").strip()
            term_name = option.get_text().strip()
            if term_code and term_name:
                terms.append((term_code, term_name))

        logger.info(f"Found {len(terms)} available terms")
        return terms

    def get_subjects_for_term(self, term_code):
        """Get available subjects for a specific term"""
        print(f"[DEBUG] Fetching subjects for term {term_code}...", file=sys.stderr)
        session = self._create_session()

        try:
            # Get session ID from term selection page
            response = session.get(self.term_select_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            session_input = soup.find("input", {"name": "session_id"})
            session_id = session_input.get("value") if session_input else ""

            # Submit term selection to get subject list
            form_data = {
                "wsea_code": "EXT",
                "term_code": term_code,
                "session_id": session_id,
            }

            response = session.post(self.search_fields_url, data=form_data, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract available subjects
            subject_select = soup.find("select", attrs={"name": "sel_subj"})
            subjects = set()
            if subject_select:
                for option in subject_select.find_all("option"):
                    subject_code = option.get("value", "").strip()
                    if subject_code and subject_code not in ["dummy", "%"]:
                        subjects.add(subject_code)

            print(
                f"[DEBUG] Found {len(subjects)} subjects for term {term_code}.",
                file=sys.stderr,
            )
            return subjects, session_id

        except Exception as e:
            print(
                f"[ERROR] Failed to get subjects for term {term_code}: {e}",
                file=sys.stderr,
            )
            logger.error(f"Failed to get subjects for term {term_code}: {e}")
            return set(), ""

    def search_course(
        self,
        term_code,
        session_id,
        subject_code,
        course_number,
        course_title="",
        course_credits=0.0,
    ):
        print(
            f"[DEBUG]   > Searching course {subject_code} {course_number}...",
            file=sys.stderr,
        )
        session = self._create_session()

        # Rate limiting
        time.sleep(0.8)

        try:
            # Prepare Banner search request - broadened to capture all sections
            search_data = [
                ("wsea_code", "EXT"),
                ("term_code", term_code),
                ("session_id", session_id),
                ("ws_numb", ""),
                ("sel_aud", "dummy"),
                ("sel_subj", "dummy"),
                ("sel_camp", "dummy"),
                ("sel_sess", "dummy"),
                ("sel_attr", "dummy"),
                ("sel_levl", "dummy"),
                (
                    "sel_schd",
                    "dummy",
                ),  # Don't filter by schedule type to get all sections
                ("sel_insm", "dummy"),
                ("sel_link", "dummy"),
                ("sel_wait", "dummy"),
                ("sel_day", "dummy"),
                ("sel_begin_hh", "dummy"),
                ("sel_begin_mi", "dummy"),
                ("sel_begin_am_pm", "dummy"),
                ("sel_end_hh", "dummy"),
                ("sel_end_mi", "dummy"),
                ("sel_end_am_pm", "dummy"),
                ("sel_instruct", "dummy"),
                ("sel_special", "dummy"),
                ("sel_resd", "dummy"),
                ("sel_breadth", "dummy"),
                ("sel_levl", ""),
                ("sel_subj", subject_code),
                ("sel_number", course_number),
                ("sel_crn", ""),
                ("sel_special", "N"),
                ("sel_sess", ""),
                ("sel_schd", ""),  # Leave empty to get all schedule types
                ("sel_instruct", ""),
                ("sel_begin_hh", "0"),
                ("sel_begin_mi", "0"),
                ("sel_begin_am_pm", "a"),
                ("sel_end_hh", "0"),
                ("sel_end_mi", "0"),
                ("sel_end_am_pm", "a"),
                ("sel_day", "m"),
                ("sel_day", "t"),
                ("sel_day", "w"),
                ("sel_day", "r"),
                ("sel_day", "f"),
                ("sel_day", "s"),
                ("sel_day", "u"),
                ("block_button", ""),
            ]

            # Make the request
            response = session.post(
                self.course_search_url, data=search_data, timeout=45
            )
            response.raise_for_status()

            # Parse response
            if "No classes were found" in response.text:
                print(
                    f"[DEBUG]   > No classes found for {subject_code} {course_number}.",
                    file=sys.stderr,
                )
                return Course(
                    course_code=f"{subject_code} {course_number}",
                    subject_code=subject_code,
                    course_number=course_number,
                    catalog_title=course_title,
                    catalog_credits=course_credits,
                    is_offered=False,
                    sections_found=0,
                    banner_title="",
                    banner_credits=0.0,
                    sections=[],
                    error=False,
                    error_message="",
                )

            # Parse detailed section information
            soup = BeautifulSoup(response.content, "html.parser")
            sections_data = []
            banner_title = ""
            banner_credits = 0.0

            # Find course title from links
            title_links = soup.find_all(
                "a", href=lambda x: x and "bwysched.p_display_course" in x
            )
            for link in title_links:
                link_text = link.get_text().strip()
                if not link_text.isdigit() and subject_code not in link_text:
                    banner_title = link_text
                    break

            # Find the main results table - it's usually the largest table with course data
            # Skip scrollable divs as they often contain summary tables, find the largest table directly
            results_table = None
            all_tables = soup.find_all("table")
            logger.debug(f"Found {len(all_tables)} tables total")
            max_rows = 0
            for i, table in enumerate(all_tables):
                rows = table.find_all("tr")
                table_text = table.get_text()
                logger.debug(
                    f"Table {i}: {len(rows)} rows, has_crn: {'CRN' in table_text}, has_subject: {'Subject' in table_text}"
                )
                # Look for tables containing course data (has CRN, Subject headers or course codes)
                if len(rows) > max_rows and (
                    "CRN" in table_text
                    and "Subject" in table_text
                    and (
                        subject_code in table_text
                        or any(
                            keyword in table_text
                            for keyword in ["Status", "Credits", "Schedule"]
                        )
                    )
                ):
                    results_table = table
                    max_rows = len(rows)
                    logger.debug(
                        f"Selected table {i} with {max_rows} rows for course data"
                    )

            if results_table:
                rows = results_table.find_all("tr")
                current_section = None

                for row in rows:
                    cells = row.find_all("td")

                    # Check if this is a main section row (has CRN, Section, etc.)
                    # Look for rows with sufficient cells that contain a CRN
                    if len(cells) >= 8:  # Reduced from 11 to catch more sections
                        try:
                            # Try to find CRN in different positions
                            crn = ""
                            crn_cell_idx = None
                            for i, cell in enumerate(
                                cells[:5]
                            ):  # Check first 5 cells for CRN
                                cell_text = cell.get_text().strip()
                                crn_link = cell.find("a")
                                if crn_link:
                                    crn_text = crn_link.get_text().strip()
                                else:
                                    crn_text = cell_text

                                # CRN is typically 5 digits
                                if crn_text.isdigit() and len(crn_text) == 5:
                                    crn = crn_text
                                    crn_cell_idx = i
                                    break

                            if not crn:
                                continue  # Skip rows without valid CRN

                            # Skip duplicate CRNs
                            if any(section.crn == crn for section in sections_data):
                                logger.debug(f"Skipping duplicate CRN {crn}")
                                continue

                            # Extract other fields relative to CRN position
                            # Standard Banner layout: Status, CRN, Subject, Crse, Section, Campus, Credits, Title, Schedule Type, Days, Time, Instructor
                            status = (
                                cells[max(0, crn_cell_idx - 1)].get_text().strip()
                                if crn_cell_idx > 0
                                else ""
                            )

                            # Find section identifier - typically 1-2 positions after CRN
                            section = ""
                            for i in range(
                                crn_cell_idx + 1, min(len(cells), crn_cell_idx + 4)
                            ):
                                cell_text = cells[i].get_text().strip()
                                if (
                                    cell_text
                                    and not cell_text.isdigit()
                                    and len(cell_text) <= 4
                                    and cell_text != subject_code
                                    and cell_text not in ["COMP", "1005"]
                                ):  # Section codes are short and not subject/course
                                    section = cell_text
                                    break

                            # Find credits - look for numeric values
                            credits = 0.0
                            credits_text = ""
                            for i in range(
                                crn_cell_idx + 2, min(len(cells), crn_cell_idx + 6)
                            ):
                                cell_text = cells[i].get_text().strip()
                                try:
                                    if cell_text and float(cell_text) > 0:
                                        credits = float(cell_text)
                                        credits_text = cell_text
                                        break
                                except ValueError:
                                    continue

                            # Find schedule type - keywords like "Lecture", "Tutorial", "Laboratory"
                            schedule_type = ""
                            schedule_keywords = [
                                "Lecture",
                                "Tutorial",
                                "Laboratory",
                                "Lab",
                                "Seminar",
                                "Workshop",
                                "Practicum",
                            ]
                            for cell in cells[crn_cell_idx:]:
                                cell_text = cell.get_text().strip()
                                for keyword in schedule_keywords:
                                    if keyword.lower() in cell_text.lower():
                                        schedule_type = keyword
                                        break
                                if schedule_type:
                                    break

                            if not schedule_type:
                                schedule_type = "Lecture"  # Default assumption

                            # Skip sections with empty names unless it's clearly a main lecture
                            if not section:
                                if schedule_type == "Lecture":
                                    # Try to infer section name from position or default to A
                                    section = (
                                        "A"  # Default for unnamed lecture sections
                                    )
                                else:
                                    logger.debug(
                                        f"Skipping section with no name and CRN {crn}"
                                    )
                                    continue

                            # Find instructor - typically in the last few cells, look for names
                            instructor = "TBA"
                            for cell in cells[-3:]:  # Check last 3 cells for instructor
                                cell_text = cell.get_text().strip()
                                # Simple heuristic: if it contains letters and spaces, might be a name
                                if (
                                    cell_text
                                    and any(c.isalpha() for c in cell_text)
                                    and len(cell_text) > 3
                                ):
                                    instructor = cell_text
                                    break

                            if credits > 0 and banner_credits == 0.0:
                                banner_credits = credits

                            current_section = CourseSection(
                                crn=crn,
                                section=section,
                                status=status,
                                credits=credits,
                                schedule_type=schedule_type,
                                instructor=instructor,
                                meeting_times=[],
                                notes=[],
                            )
                            sections_data.append(current_section)
                            logger.debug(
                                f"Added section {section} ({schedule_type}) with CRN {crn}"
                            )

                        except (IndexError, AttributeError, ValueError) as e:
                            logger.debug(f"Skipped row due to parsing error: {e}")
                            continue

                    elif len(cells) > 0 and current_section:
                        # This might be a meeting time or note row
                        row_text = row.get_text().strip()
                        if "Meeting Date:" in row_text:
                            # Parse meeting time
                            date_match = re.search(
                                r"Meeting Date:\s*(\w+ \d+, \d+)\s*to\s*(\w+ \d+, \d+)",
                                row_text,
                            )
                            days_match = re.search(
                                r"Days:\s*([^T]+?)(?=Time:|$)", row_text
                            )
                            time_match = re.search(
                                r"Time:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
                                row_text,
                            )

                            if date_match and days_match and time_match:
                                meeting_time = MeetingTime(
                                    start_date=date_match.group(1).strip(),
                                    end_date=date_match.group(2).strip(),
                                    days=days_match.group(1).strip(),
                                    start_time=time_match.group(1),
                                    end_time=time_match.group(2),
                                )
                                current_section.meeting_times.append(meeting_time)
                        elif (
                            "Also Register in:" in row_text
                            or "Section Information:" in row_text
                        ):
                            current_section.notes.append(row_text.strip())

            is_offered = len(sections_data) > 0

            print(f"[DEBUG]   > Done {subject_code} {course_number}.", file=sys.stderr)
            return Course(
                course_code=f"{subject_code} {course_number}",
                subject_code=subject_code,
                course_number=course_number,
                catalog_title=course_title,
                catalog_credits=course_credits,
                is_offered=is_offered,
                sections_found=len(sections_data),
                banner_title=banner_title,
                banner_credits=banner_credits,
                sections=sections_data,
                error=False,
                error_message="",
            )

        except Exception as e:
            print(
                f"[ERROR]   > Error searching {subject_code} {course_number}: {e}",
                file=sys.stderr,
            )
            logger.error(f"Error searching {subject_code} {course_number}: {e}")
            return Course(
                course_code=f"{subject_code} {course_number}",
                subject_code=subject_code,
                course_number=course_number,
                catalog_title=course_title,
                catalog_credits=course_credits,
                is_offered=False,
                sections_found=0,
                banner_title="",
                banner_credits=0.0,
                sections=[],
                error=True,
                error_message=str(e),
            )

    def discover_subjects(self, term_code):
        """Discover available subjects for a term"""
        subjects, session_id = self.get_subjects_for_term(term_code)
        return list(subjects), session_id

    def discover_courses(self, term_code, subjects=None, max_courses_per_subject=None):
        """Discover courses for specific subjects in a term"""
        if not subjects:
            available_subjects, session_id = self.get_subjects_for_term(term_code)
            subjects = list(available_subjects)
        else:
            # Validate subjects are available
            available_subjects, session_id = self.get_subjects_for_term(term_code)
            subjects = [s for s in subjects if s in available_subjects]

        if not subjects or not session_id:
            return []

        # Prepare course list from catalog
        course_args = []
        for subject_code in subjects:
            subject_courses = self.catalog_data.get(subject_code, [])
            if not subject_courses:
                continue

            # Limit courses per subject if specified
            if max_courses_per_subject:
                subject_courses = subject_courses[:max_courses_per_subject]

            for course in subject_courses:
                course_code = course.get("code", "").replace(" ", "")
                if course_code.startswith(subject_code):
                    course_number = course_code.replace(subject_code, "").strip()
                    course_title = course.get("title", "")
                    course_credits = course.get("credits", 0.0)

                    course_args.append(
                        (
                            term_code,
                            session_id,
                            subject_code,
                            course_number,
                            course_title,
                            course_credits,
                        )
                    )

        if not course_args:
            return []

        print(
            f"[DEBUG] Starting course queries ({len(course_args)} to process)...",
            file=sys.stderr,
        )

        # Process courses (single-threaded for CLI simplicity)
        results = []
        for idx, args in enumerate(course_args, 1):
            (
                term_code,
                session_id,
                subject_code,
                course_number,
                course_title,
                course_credits,
            ) = args
            print(
                f"[DEBUG] [{idx}/{len(course_args)}] Querying {subject_code} {course_number}...",
                file=sys.stderr,
            )
            course = self.search_course(
                term_code,
                session_id,
                subject_code,
                course_number,
                course_title,
                course_credits,
            )
            print(
                f"[DEBUG] [{idx}/{len(course_args)}] Finished {subject_code} {course_number}.",
                file=sys.stderr,
            )
            results.append(course)

        print(f"[DEBUG] All course queries complete.", file=sys.stderr)
        return results
