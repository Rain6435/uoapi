"""
Discovery service for loading and serving course data from assets files.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


def get_assets_path() -> Path:
    """Get the path to the assets directory."""
    import sys
    import site

    # Check if we're in a virtual environment
    in_venv = hasattr(sys, "prefix") and sys.prefix != sys.base_prefix

    # PRIORITY 1: Development assets (current working directory)
    cwd_assets = Path.cwd() / "assets"
    if cwd_assets.exists() and (cwd_assets / "carleton" / "courses.json").exists():
        return cwd_assets

    # PRIORITY 2: Project root assets (for development)
    current_file = Path(__file__)
    src_dir = current_file.parent.parent.parent  # src/
    project_root = src_dir.parent  # project root
    dev_assets = project_root / "assets"

    if dev_assets.exists() and (dev_assets / "carleton" / "courses.json").exists():
        return dev_assets

    if in_venv:
        # If in virtual environment, ONLY check within the venv
        # PRIORITY 3: Virtual environment assets
        venv_assets = Path(sys.prefix) / "assets"
        if (
            venv_assets.exists()
            and (venv_assets / "carleton" / "courses.json").exists()
        ):
            return venv_assets

        # PRIORITY 4: Virtual environment site-packages
        for site_dir in site.getsitepackages():
            if site_dir.startswith(sys.prefix):  # Only venv site-packages
                site_assets = Path(site_dir).parent / "assets"
                if (
                    site_assets.exists()
                    and (site_assets / "carleton" / "courses.json").exists()
                ):
                    return site_assets
    else:
        # Not in virtual environment - check system locations
        # PRIORITY 3: System-wide installed assets
        if hasattr(sys, "prefix"):
            installed_assets = Path(sys.prefix) / "assets"
            if (
                installed_assets.exists()
                and (installed_assets / "carleton" / "courses.json").exists()
            ):
                return installed_assets

        # PRIORITY 4: User-installed assets (pip --user)
        if site.getusersitepackages():
            user_site = Path(site.getusersitepackages())
            # Go up from .../lib/python3.x/site-packages to .../assets
            user_local_assets = user_site.parent.parent.parent / "assets"
            if (
                user_local_assets.exists()
                and (user_local_assets / "carleton" / "courses.json").exists()
            ):
                return user_local_assets

        # PRIORITY 5: Site-packages locations
        for site_dir in site.getsitepackages():
            site_assets = Path(site_dir).parent / "assets"
            if (
                site_assets.exists()
                and (site_assets / "carleton" / "courses.json").exists()
            ):
                return site_assets

    # Final fallback: check relative to package
    package_dir = Path(__file__).parent.parent
    package_assets = package_dir / "assets"

    return package_assets


def get_available_universities() -> List[str]:
    """Get list of available universities based on assets directories."""
    assets_path = get_assets_path()
    universities = []

    # Check for university directories with courses.json files
    for university_dir in ["uottawa", "carleton"]:
        courses_file = assets_path / university_dir / "courses.json"
        if courses_file.exists():
            universities.append(university_dir)

    return universities


def normalize_university_name(university: str) -> Optional[str]:
    """Normalize university name to match directory structure."""
    normalized = university.lower().strip()

    if normalized in ["uottawa", "university of ottawa"]:
        return "uottawa"
    elif normalized in ["carleton", "carleton university"]:
        return "carleton"
    else:
        return None


def get_courses_data(university: str) -> Dict[str, Any]:
    """
    Load and return course data for the specified university.

    Args:
        university: University identifier (uottawa, carleton, etc.)

    Returns:
        Dictionary containing course data and metadata

    Raises:
        FileNotFoundError: If courses.json file doesn't exist for the university
        ValueError: If university is not supported
    """
    normalized_uni = normalize_university_name(university)
    if not normalized_uni:
        raise ValueError(f"Unsupported university: {university}")

    assets_path = get_assets_path()
    courses_file = assets_path / normalized_uni / "courses.json"

    if not courses_file.exists():
        raise FileNotFoundError(
            f"Courses data not found for {university} at {courses_file}"
        )

    try:
        with open(courses_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Add discovery metadata
        data["discovery_metadata"] = {
            "university": normalized_uni,
            "file_path": str(courses_file),
            "file_size_bytes": courses_file.stat().st_size,
        }

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in courses file for {university}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load courses data for {university}: {e}")


def get_course_count(university: str) -> int:
    """Get the total number of courses for a university."""
    try:
        data = get_courses_data(university)

        # Handle different data structures
        if "metadata" in data and "total_courses" in data["metadata"]:
            return data["metadata"]["total_courses"]
        elif "subjects" in data:
            # Count courses in subjects structure (Carleton format)
            total = 0
            for subject_courses in data["subjects"].values():
                total += len(subject_courses)
            return total
        elif "departments" in data:
            # Count courses in departments structure (UOttawa format)
            total = 0
            for dept_info in data["departments"].values():
                if "courses" in dept_info:
                    total += len(dept_info["courses"])
            return total
        else:
            return 0
    except:
        return 0


def get_subjects_list(university: str) -> List[str]:
    """Get list of subject codes for a university."""
    try:
        data = get_courses_data(university)

        if "subjects" in data:
            # Carleton format
            return list(data["subjects"].keys())
        elif "departments" in data:
            # UOttawa format
            return [
                info.get("department_code", "")
                for info in data["departments"].values()
                if info.get("department_code")
            ]
        else:
            return []
    except:
        return []


def search_courses(
    university: str, subject_code: Optional[str] = None, query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for courses in a university's data.

    Args:
        university: University identifier
        subject_code: Filter by subject code (optional)
        query: Search query for course title/description (optional)

    Returns:
        List of matching courses
    """
    try:
        data = get_courses_data(university)
        courses = []

        if "subjects" in data:
            # Carleton format
            for subject, subject_courses in data["subjects"].items():
                if subject_code and subject != subject_code.upper():
                    continue

                for course in subject_courses:
                    if query:
                        # Search in both title and code
                        title_match = query.lower() in course.get("title", "").lower()
                        code_match = query.lower() in course.get("code", "").lower()
                        description_match = (
                            query.lower() in course.get("description", "").lower()
                        )
                        if not (title_match or code_match or description_match):
                            continue

                    courses.append(
                        {
                            "subject": subject,
                            "code": course.get("code", ""),
                            "title": course.get("title", ""),
                            "credits": course.get("credits", 0),
                            "description": course.get("description", ""),
                        }
                    )

        elif "departments" in data:
            # UOttawa format
            for dept_name, dept_info in data["departments"].items():
                dept_code = dept_info.get("department_code", "")
                if subject_code and dept_code != subject_code.upper():
                    continue

                for course in dept_info.get("courses", []):
                    if query:
                        # Search in both title and code
                        title_match = query.lower() in course.get("title", "").lower()
                        code_match = (
                            query.lower() in course.get("course_code", "").lower()
                        )
                        description_match = (
                            query.lower() in course.get("description", "").lower()
                        )
                        if not (title_match or code_match or description_match):
                            continue

                    courses.append(
                        {
                            "subject": dept_code,
                            "code": f"{dept_code} {course.get('course_code', '')}",
                            "title": course.get("title", ""),
                            "credits": course.get("credits", ""),
                            "description": course.get("description", ""),
                        }
                    )

        return courses

    except Exception:
        return []
