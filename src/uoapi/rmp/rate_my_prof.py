from typing import List, Dict, Optional, Any
import requests
import re


# GraphQL endpoint and headers for RateMyProfessor API
GRAPHQL_ENDPOINT = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    ),
    "Content-Type": "application/json",
}

# Store school IDs and GraphQL IDs for Canadian universities
SCHOOL_DATA = {
    "university of ottawa": {
        "legacy_id": 1452,
        "graphql_id": "U2Nob29sLTE0NTI=",
        "name": "University of Ottawa",
    },
    "carleton university": {
        "legacy_id": 1420,
        "graphql_id": "U2Nob29sLTE0MjA=",
        "name": "Carleton University",
    },
    "uottawa": {
        "legacy_id": 1452,
        "graphql_id": "U2Nob29sLTE0NTI=",
        "name": "University of Ottawa",
    },
    "carleton": {
        "legacy_id": 1420,
        "graphql_id": "U2Nob29sLTE0MjA=",
        "name": "Carleton University",
    },
}

# Cache for GraphQL responses to avoid repeated requests
_school_cache = {}


def get_school_by_name(school_name: str) -> Optional[Dict]:
    """
    Get school information by name using direct GraphQL API.

    Args:
        school_name: Name of the school (case insensitive)

    Returns:
        Dictionary with school information if found, None otherwise
    """
    normalized_name = school_name.lower().strip()

    if normalized_name not in SCHOOL_DATA:
        return None

    # Check cache first
    if normalized_name in _school_cache:
        return _school_cache[normalized_name]

    school_info = SCHOOL_DATA[normalized_name]

    # Create a simple school object with the information we need
    school_data = {
        "id": school_info["graphql_id"],
        "legacy_id": school_info["legacy_id"],
        "name": school_info["name"],
    }

    # Cache the result
    _school_cache[normalized_name] = school_data
    return school_data


def search_professor_graphql(first_name: str, last_name: str, school_id: str) -> Optional[Dict]:
    """
    Search for a professor using GraphQL API.

    Args:
        first_name: Professor's first name
        last_name: Professor's last name
        school_id: School's GraphQL ID

    Returns:
        Professor data if found, None otherwise
    """
    query = """
    {
      newSearch {
        teachers(query: {text: "%s %s", schoolID: "%s"}, first: 5) {
          edges {
            node {
              id
              legacyId
              firstName
              lastName
              department
              avgRating
              numRatings
              wouldTakeAgainPercent
              avgDifficulty
              school {
                name
                id
              }
            }
          }
        }
      }
    }
    """ % (
        first_name,
        last_name,
        school_id,
    )

    try:
        response = requests.post(
            GRAPHQL_ENDPOINT, json={"query": query}, headers=HEADERS, timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()
        if "errors" in data or not data.get("data"):
            return None

        teachers = data["data"]["newSearch"]["teachers"]["edges"]

        # Find exact match for the professor
        for teacher_edge in teachers:
            teacher = teacher_edge["node"]
            teacher_first = teacher["firstName"].lower().strip()
            teacher_last = teacher["lastName"].lower().strip()

            if (
                teacher_first == first_name.lower().strip()
                and teacher_last == last_name.lower().strip()
            ):
                return teacher

        # If no exact match, return the first result if it exists
        if teachers:
            return teachers[0]["node"]

        return None

    except Exception:
        return None


def get_professor_ratings(professors: List[tuple], school_name: str) -> List[Dict]:
    """
    Get ratings for a list of professors from a specific school using GraphQL API.

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
            professor = search_professor_graphql(first_name, last_name, school["id"])
            if professor:
                professor_data.append(
                    {
                        "rmp_id": professor.get("legacyId"),
                        "first_name": first_name,
                        "last_name": last_name,
                        "rating": professor.get("avgRating"),
                        "num_ratings": professor.get("numRatings", 0),
                        "department": professor.get("department"),
                        "would_take_again_percent": professor.get("wouldTakeAgainPercent"),
                        "avg_difficulty": professor.get("avgDifficulty"),
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
                        "would_take_again_percent": None,
                        "avg_difficulty": None,
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
                    "would_take_again_percent": None,
                    "avg_difficulty": None,
                    "error": str(e),
                }
            )

    return professor_data


def get_teachers_ratings_by_school(
    school_name: str, professors: Optional[List[tuple]] = None
) -> Dict:
    """
    Get teacher ratings for a school using GraphQL API. Maintains compatibility with existing API.

    Args:
        school_name: Name of the school
        professors: Optional list of professors to query

    Returns:
        Dictionary with ratings data
    """
    school = get_school_by_name(school_name)
    if not school:
        # Instead of crashing, return a response indicating no ratings are available
        if professors is None:
            professors = []

        # Return empty ratings for all professors
        empty_ratings = []
        for prof_tuple in professors:
            if len(prof_tuple) >= 2:
                first_name, last_name = prof_tuple[0], prof_tuple[1]
                empty_ratings.append(
                    {
                        "name": f"{first_name} {last_name}",
                        "rating": None,
                        "num_ratings": 0,
                        "department": None,
                        "rmp_id": None,
                        "error": f"School '{school_name}' not supported or not found",
                    }
                )

        return {
            "ratings": empty_ratings,
            "school_id": None,
            "school_name": school_name,
            "error": f"School '{school_name}' not supported or not found",
        }

    if professors is None:
        professors = []

    ratings = get_professor_ratings(professors, school_name)

    return {"ratings": ratings, "school_id": school["legacy_id"], "school_name": school["name"]}


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
    Get rating for a single instructor using GraphQL API.

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
            "would_take_again_percent": None,
            "avg_difficulty": None,
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
                "would_take_again_percent": rating_data.get("would_take_again_percent"),
                "avg_difficulty": rating_data.get("avg_difficulty"),
            }
    except Exception:
        pass

    return {
        "instructor": instructor_text,
        "rating": None,
        "num_ratings": 0,
        "department": None,
        "rmp_id": None,
        "would_take_again_percent": None,
        "avg_difficulty": None,
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
                enhanced_entry["instructor_would_take_again_percent"] = rating_info[
                    "would_take_again_percent"
                ]
                enhanced_entry["instructor_avg_difficulty"] = rating_info["avg_difficulty"]

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
                                enhanced_component["instructor_would_take_again_percent"] = (
                                    rating_info["would_take_again_percent"]
                                )
                                enhanced_component["instructor_avg_difficulty"] = rating_info[
                                    "avg_difficulty"
                                ]

                            enhanced_components.append(enhanced_component)

                        enhanced_section["components"] = enhanced_components

                    enhanced_sections.append(enhanced_section)

                enhanced_entry["sections"] = enhanced_sections

            enhanced_timetables.append(enhanced_entry)

        enhanced_data["timetables"] = enhanced_timetables

    return enhanced_data
