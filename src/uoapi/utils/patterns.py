"""
Common regex patterns for course parsing.

This module consolidates all regex patterns used across the
application for parsing course codes, prerequisites, and other
course-related information.
"""

import regex as re

# Basic course code patterns
COURSE_CODE_PATTERN = r"[A-Z]{3,4}\s*[0-9]{4,5}[A-Za-z]{0,1}"
CODE_GROUPS_PATTERN = r"([A-Z]{3,4})\s*([0-9]{4,5}[A-Za-z]{0,1})"

# Non-course code patterns (things that look like course codes but aren't)
NOT_REAL_COURSE_CODES = (
    r"(?P<ForU>.*[34]U.*)|(?:an )?equivalent|Permission of the School|"
    r"Permission de l'(?:École|Institut)|Approval of the instructor|"
    r"Permission du Département"
)

# Faculty patterns
FACULTIES = r"(?:[Mm]athematics|[Mm]athématiques|[Ss]cience)"

# Credit count patterns
CREDIT_COUNT = (
    r"(?P<credit_count>\d+ crédits de cours(?: en)?(?: %s)? \(?(?:[A-Z]{3}\)?"
    r"(?: ou [A-Z]{3})* de niveau \d000(?: ou supérieur)*|universitaire)|"
    r"\d+(?: course)? units (?:of|in)(?: %s)? \(?(?:[A-Z]{3}\)?"
    r"(?: or [A-Z]{3})*(?: courses)? at(?: the| level)? \d000(?: level)?"
    r"(?: or above)?|university-level courses?))" % (FACULTIES, FACULTIES)
)

# Special program patterns
FOR_SPECIAL_PROGRAM = (
    r"(?P<for_special_program> or for honors %s students: | ou pour les "
    r"étudiants et étudiantes inscrits aux programmes spécialisés en %s : )"
    % (FACULTIES, FACULTIES)
)

# Parsable codes (combination of course codes and other patterns)
PARSABLE_CODES = r"(?:\(*(?:%s)\)*(?:, |/| or | ou | and | et |%s)?)+" % (
    COURSE_CODE_PATTERN + "|" + NOT_REAL_COURSE_CODES + "|(?:" + CREDIT_COUNT + ")",
    FOR_SPECIAL_PROGRAM,
)


# Compiled regex patterns for common use
class CompiledPatterns:
    """Container for compiled regex patterns."""

    # Basic patterns
    course_code = re.compile(COURSE_CODE_PATTERN)
    code_groups = re.compile(CODE_GROUPS_PATTERN)
    credit = re.compile(
        r"\([0-9]{1,} (unit[s]{0,1}|crédit[s]{0,1})\)|[0-9]{1,} (unit[s]{0,1}|crédit[s]{0,1})"
    )
    subject = re.compile(r"\([A-Z]{3}\)")
    href = re.compile(r"[/]{0,1}en/courses/[A-Za-z]{1,}[/]{0,1}")
    numbers = re.compile(r"[0-9]{1,}")

    # Prerequisite patterns
    class Prerequisites:
        """Prerequisite-specific patterns."""

        not_combined_for_credits = re.compile(
            r"(?:(?<=^(?:(?:The )?[Cc]ourses |Les cours ))%s(?=(?: cannot be combined for "
            r"(?:units|credits)$| ne peuvent être combinés pour l'obtention de crédits$))|"
            r"(?<=This course cannot be taken for units by any student who has previously "
            r"received units for )%s$)" % (PARSABLE_CODES, COURSE_CODE_PATTERN)
        )

        no_credits_in_program = re.compile(
            r"(?:This course cannot count for unit in any program in the Faculty of |"
            r"Prerequisite: This course cannot count as a %s elective for students in the "
            r"Faculty of |Ce cours ne peut pas compter pour fin de crédits dans un programme "
            r"de la Faculté des |Préalable : Ce cours ne peut pas compter comme cours au choix "
            r"en %s pour les étudiants et étudiantes de la Faculté des )%s"
            % (FACULTIES, FACULTIES, FACULTIES)
        )

        prerequisites = re.compile(
            r"(?<=^(?:/ )?(?:Prerequisite|Préalable)s?\s*:\s*(?:One of )?)%s$"
            % PARSABLE_CODES
        )

        corequisite = re.compile(
            r"(?:Corequisite|Concomitant)\s*:\s*%s|%s(?= are prerequisite or corequisite to %s$)|"
            r"(?<=Les cours )%s(?= sont préalables ou concomitants à %s$)"
            % (
                PARSABLE_CODES,
                PARSABLE_CODES,
                COURSE_CODE_PATTERN,
                PARSABLE_CODES,
                COURSE_CODE_PATTERN,
            )
        )

        cgpa_requirements = re.compile(
            r"(?:Prerequisite: The student must have a minimum CGPA of \d(?:\.|,)\d|"
            r"Préalable : L'étudiant ou l'étudiante doit avoir conservé une MPC minimale de "
            r"\d(?:\.|,)\d|Seulement disponible pour les étudiants ayant une MPC de \d,\d et plus)|"
            r"Open only to students whose cumulative grade point average is \d\.\d or over"
            r"(?: and the permission of the Department| et avoir la permission du Département)?"
            r"(?:, and who have completed all the first(?: and second)? year [A-Z]{3} core courses "
            r"of their program| et ayant réussi tous les cours [A-Z]{3} du tronc commun de niveaux "
            r"1000(?: et 2000)? de leur programme)?$"
        )

        prior_knowledge = re.compile(
            r"Prerequisites: familiarity with basic concepts in .*|(?:or )?A basic knowledge of .*$|"
            r"Prerequisite: Some familiarity with .*"
        )

        additional_prereqs = re.compile(
            r"Additional prerequisites may be imposed depending on the topic|"
            r"Des préalables supplémentaires peuvent s'appliquer selon le sujet du cours"
        )

        permission = re.compile(
            r"Permission of the Department is required$|Permission du Département est requise.?$"
        )

        interview = re.compile(
            r"Interview with Professor is required$|Entrevue avec le professeur est requise$"
        )

        also_offered_as = re.compile(
            r"(?<=^(?:Also offered as |Aussi offert sous la cote ))%s$"
            % COURSE_CODE_PATTERN
        )

        primarily_intended_for = re.compile(
            r"[Tt]his course is .* for .*$|Ce cours .* principalement(?: destiné)? aux "
            r"étudiants et étudiantes .*$"
        )

        previously = re.compile(
            r"(?:Previously|Antérieurement) %s" % COURSE_CODE_PATTERN
        )


# Create instances for easy access
patterns = CompiledPatterns()
prereq_patterns = CompiledPatterns.Prerequisites()


def extract_course_codes(text: str) -> list[str]:
    """
    Extract all course codes from text.

    Args:
        text: Text to search for course codes

    Returns:
        List of course codes found
    """
    return patterns.course_code.findall(text)


def extract_subject_code(course_code: str) -> str:
    """
    Extract subject code from a course code.

    Args:
        course_code: Full course code (e.g., "CSI3140")

    Returns:
        Subject code (e.g., "CSI")
    """
    match = patterns.code_groups.match(course_code.replace(" ", ""))
    return match.group(1) if match else course_code


def extract_course_number(course_code: str) -> str:
    """
    Extract course number from a course code.

    Args:
        course_code: Full course code (e.g., "CSI3140")

    Returns:
        Course number (e.g., "3140")
    """
    match = patterns.code_groups.match(course_code.replace(" ", ""))
    return match.group(2) if match else course_code


def normalize_course_code(course_code: str) -> str:
    """
    Normalize course code format.

    Args:
        course_code: Course code to normalize

    Returns:
        Normalized course code (uppercase, no spaces)
    """
    return course_code.upper().replace(" ", "")


def extract_credits(text: str) -> str:
    """
    Extract credit information from text.

    Args:
        text: Text to search for credit information

    Returns:
        Credit string if found, empty string otherwise
    """
    match = patterns.credit.search(text)
    return match.group(0) if match else ""


def is_valid_course_code(code: str) -> bool:
    """
    Check if a string is a valid course code.

    Args:
        code: String to check

    Returns:
        True if valid course code format, False otherwise
    """
    return bool(patterns.course_code.fullmatch(code.replace(" ", "")))


# Legacy compatibility - maintain the old interface
code_re = patterns.course_code
code_groups = patterns.code_groups
credit_re = patterns.credit
subj_re = patterns.subject
href_re = patterns.href
numbers_re = patterns.numbers

# Legacy prereq dictionary for backward compatibility
prereq = {
    "not_combined_for_credits": prereq_patterns.not_combined_for_credits,
    "no_credits_in_program": prereq_patterns.no_credits_in_program,
    "prerequisites": prereq_patterns.prerequisites,
    "corequisite": prereq_patterns.corequisite,
    "CGPA_requirements": prereq_patterns.cgpa_requirements,
    "prior_knowledge": prereq_patterns.prior_knowledge,
    "additional_prereqs": prereq_patterns.additional_prereqs,
    "permission": prereq_patterns.permission,
    "interview": prereq_patterns.interview,
    "also_offered_as": prereq_patterns.also_offered_as,
    "primarily_intended_for": prereq_patterns.primarily_intended_for,
    "previously": prereq_patterns.previously,
}
