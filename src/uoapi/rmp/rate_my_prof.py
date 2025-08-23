from typing import List, Dict, Optional, Any
from ratemyprofessor import School, get_professor_by_school_and_name
import re


# Store school IDs and names, create School objects lazily
SCHOOL_DATA = {
    "university of ottawa": (1452, "University of Ottawa"),
    "carleton university": (1420, "Carleton University"),
    "uottawa": (1452, "University of Ottawa"),
    "carleton": (1420, "Carleton University"),
}

# Cache for created School objects
_school_cache = {}


def get_school_by_name(school_name: str) -> Optional[School]:
    """
    Get a School object by name.

    Args:
        school_name: Name of the school (case insensitive)

    Returns:
        School object if found, None otherwise
    """
    normalized_name = school_name.lower().strip()

    if normalized_name not in SCHOOL_DATA:
        return None

    # Check cache first
    if normalized_name in _school_cache:
        return _school_cache[normalized_name]

    # Create School object
    school_id, school_name_formal = SCHOOL_DATA[normalized_name]
    try:
        # Try the constructor with both parameters
        school = School(school_id, school_name_formal)
    except TypeError:
        # Fallback: try with just the ID (some versions may not accept name)
        try:
            school = School(school_id)
        except Exception:
            return None
    except Exception:
        return None

    # Cache the result
    _school_cache[normalized_name] = school
    return school


def get_professor_ratings(professors: List[tuple], school_name: str) -> List[Dict]:
    """
    Get ratings for a list of professors from a specific school.

    Args:
        professors: List of tuples (first_name, last_name)
        school_name: Name of the school

    Returns:
        List of professor data with ratings
    """
    school = get_school_by_name(school_name)
    if not school:
        raise ValueError(f"School '{school_name}' not supported")

    professor_data = []

    for first_name, last_name in professors:
        try:
            professor = get_professor_by_school_and_name(school, f"{first_name} {last_name}")
            if professor:
                professor_data.append(
                    {
                        "rmp_id": professor.id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "rating": professor.rating,
                        "num_ratings": professor.num_ratings,
                        "department": professor.department,
                    }
                )
            else:
                professor_data.append(
                    {
                        "rmp_id": None,
                        "first_name": first_name,
                        "last_name": last_name,
                        "rating": None,
                        "num_ratings": 0,
                        "department": None,
                    }
                )
        except Exception as e:
            professor_data.append(
                {
                    "rmp_id": None,
                    "first_name": first_name,
                    "last_name": last_name,
                    "rating": None,
                    "num_ratings": 0,
                    "department": None,
                    "error": str(e),
                }
            )

    return professor_data


def get_teachers_ratings_by_school(
    school_name: str, professors: Optional[List[tuple]] = None
) -> Dict:
    """
    Get teacher ratings for a school. Maintains compatibility with existing API.

    Args:
        school_name: Name of the school
        professors: Optional list of professors to query

    Returns:
        Dictionary with ratings data
    """
    school = get_school_by_name(school_name)
    if not school:
        raise ValueError(f"School '{school_name}' not supported")

    if professors is None:
        professors = []

    ratings = get_professor_ratings(professors, school_name)

    return {"ratings": ratings, "school_id": school.id, "school_name": school.name}


def parse_instructor_name(instructor_text: str) -> Optional[tuple]:
    """
    Parse instructor name from timetable text to extract first and last name.

    Args:
        instructor_text: Raw instructor text from timetable

    Returns:
        Tuple of (first_name, last_name) if parseable, None otherwise
    """
    if not instructor_text or instructor_text.strip() == "":
        return None

    # Remove common prefixes and suffixes
    instructor_text = re.sub(
        r"\b(Dr|Prof|Professor|Mr|Ms|Mrs)\b\.?\s*", "", instructor_text, flags=re.IGNORECASE
    )
    instructor_text = re.sub(
        r"\s*,?\s*(Ph\.?D\.?|PhD|M\.?D\.?|MD)\b.*$", "", instructor_text, flags=re.IGNORECASE
    )

    # Handle multiple instructors (take the first one)
    if "," in instructor_text:
        instructor_text = instructor_text.split(",")[0]

    # Split into parts
    parts = instructor_text.strip().split()
    if len(parts) < 2:
        return None

    # Assume first part is first name, rest is last name
    first_name = parts[0]
    last_name = " ".join(parts[1:])

    return (first_name, last_name)


def get_instructor_rating(instructor_text: str, school_name: str) -> Dict[str, Any]:
    """
    Get rating for a single instructor.

    Args:
        instructor_text: Raw instructor text from timetable
        school_name: Name of the school

    Returns:
        Dictionary with rating information
    """
    name_tuple = parse_instructor_name(instructor_text)
    if not name_tuple:
        return {
            "instructor": instructor_text,
            "rating": None,
            "num_ratings": 0,
            "department": None,
            "rmp_id": None,
        }

    try:
        ratings = get_professor_ratings([name_tuple], school_name)
        if ratings and len(ratings) > 0:
            rating_data = ratings[0]
            return {
                "instructor": instructor_text,
                "rating": rating_data.get("rating"),
                "num_ratings": rating_data.get("num_ratings", 0),
                "department": rating_data.get("department"),
                "rmp_id": rating_data.get("rmp_id"),
            }
    except Exception:
        pass

    return {
        "instructor": instructor_text,
        "rating": None,
        "num_ratings": 0,
        "department": None,
        "rmp_id": None,
    }


def inject_ratings_into_timetable(
    timetable_data: Dict[str, Any], school_name: str
) -> Dict[str, Any]:
    """
    Inject professor ratings into timetable data.

    Args:
        timetable_data: Timetable data from query_timetable
        school_name: Name of the school

    Returns:
        Enhanced timetable data with ratings
    """
    if not isinstance(timetable_data, dict):
        return timetable_data

    # Make a copy to avoid modifying the original
    enhanced_data = dict(timetable_data)

    # Check if this has timetables array
    if "timetables" in enhanced_data and isinstance(enhanced_data["timetables"], list):
        enhanced_timetables = []
        for timetable_entry in enhanced_data["timetables"]:
            enhanced_entry = dict(timetable_entry)

            # Handle both flat structure (direct instructor field) and nested structure
            if "instructor" in enhanced_entry:
                # Flat structure - instructor directly in timetable entry
                instructor_text = enhanced_entry["instructor"]
                rating_info = get_instructor_rating(instructor_text, school_name)

                # Add rating fields to the entry
                enhanced_entry["instructor_rating"] = rating_info["rating"]
                enhanced_entry["instructor_num_ratings"] = rating_info["num_ratings"]
                enhanced_entry["instructor_department"] = rating_info["department"]
                enhanced_entry["instructor_rmp_id"] = rating_info["rmp_id"]

            # Handle nested structure - sections with components
            if "sections" in enhanced_entry and isinstance(enhanced_entry["sections"], list):
                enhanced_sections = []
                for section in enhanced_entry["sections"]:
                    enhanced_section = dict(section)

                    if "components" in enhanced_section and isinstance(
                        enhanced_section["components"], list
                    ):
                        enhanced_components = []
                        for component in enhanced_section["components"]:
                            enhanced_component = dict(component)

                            # If this component has an instructor field, add rating
                            if "instructor" in enhanced_component:
                                instructor_text = enhanced_component["instructor"]
                                rating_info = get_instructor_rating(instructor_text, school_name)

                                # Add rating fields to the component
                                enhanced_component["instructor_rating"] = rating_info["rating"]
                                enhanced_component["instructor_num_ratings"] = rating_info[
                                    "num_ratings"
                                ]
                                enhanced_component["instructor_department"] = rating_info[
                                    "department"
                                ]
                                enhanced_component["instructor_rmp_id"] = rating_info["rmp_id"]

                            enhanced_components.append(enhanced_component)

                        enhanced_section["components"] = enhanced_components

                    enhanced_sections.append(enhanced_section)

                enhanced_entry["sections"] = enhanced_sections

            enhanced_timetables.append(enhanced_entry)

        enhanced_data["timetables"] = enhanced_timetables

    return enhanced_data
