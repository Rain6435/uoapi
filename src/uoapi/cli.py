#!/usr/bin/env python3
"""
Clean, unified CLI for Schedulo API.

Usage:
  schedulo terms carleton                          # List available terms
  schedulo courses uottawa fall2025 CSI           # List CSI courses (3-letter)
  schedulo courses carleton COMP --catalog        # List COMP catalog courses (4-letter)
  schedulo courses uottawa CSI --catalog          # List CSI catalog courses (3-letter)
  schedulo courses carleton --catalog              # List all catalog courses
  schedulo course carleton COMP1005 fall2025      # Get course details
  schedulo subjects uottawa                        # List subjects  
  schedulo professor John Smith carleton          # Get professor ratings
  schedulo server                                  # Start API server
"""

import argparse
import sys


def get_provider(university: str):
    """Get the appropriate provider for a university."""
    if university.lower() in ["carleton", "cu"]:
        from uoapi.universities.carleton.provider import CarletonProvider

        return CarletonProvider()
    elif university.lower() in ["uottawa", "ottawa", "uo"]:
        from uoapi.universities.uottawa.provider import UOttawaProvider

        return UOttawaProvider()
    else:
        raise ValueError(
            f"University '{university}' not supported. Available: carleton, uottawa"
        )


def parse_term(term_str: str) -> str:
    """Convert friendly term format to term code."""
    term_mapping = {
        "fall2025": "202530",
        "winter2025": "202510",
        "summer2025": "202520",
        "fall2024": "202430",
        "winter2024": "202410",
        "summer2024": "202420",
    }

    if term_str.isdigit() and len(term_str) == 6:
        return term_str

    return term_mapping.get(term_str.lower(), term_str)


def cmd_terms(args: argparse.Namespace):
    """List available terms."""
    provider = get_provider(args.university)
    print(f"Available terms at {args.university}:")

    terms = provider.get_available_terms()
    for code, name in terms:
        print(f"  {code}: {name}")


def cmd_subjects(args: argparse.Namespace):
    """List available subjects."""
    provider = get_provider(args.university)
    subjects = provider.get_subjects()
    sorted_subjects = sorted(subjects, key=lambda s: s.code)
    
    if args.full:
        # Show all subjects
        print(f"All subjects at {args.university} ({len(subjects)} total):")
        for subject in sorted_subjects:
            print(f"  {subject.code}: {subject.name}")
    else:
        # Show first 20 subjects
        print(f"Available subjects at {args.university} (showing first 20 of {len(subjects)}):")
        for subject in sorted_subjects[:20]:
            print(f"  {subject.code}: {subject.name}")
        if len(subjects) > 20:
            print(f"  ... and {len(subjects) - 20} more")
            print(f"Use --full to see all {len(subjects)} subjects")


def cmd_courses(args: argparse.Namespace):
    """List courses for subjects."""
    provider = get_provider(args.university)
    subjects = args.subjects if args.subjects else None

    # Handle case where subjects are provided as term when using --catalog
    if args.catalog and args.term and not subjects:
        # Check if term looks like a subject code based on university
        is_subject_code = False
        if args.term.isupper() and not args.term[-1].isdigit():
            if args.university.lower() in ["carleton", "cu"] and len(args.term) == 4:
                is_subject_code = True
            elif args.university.lower() in ["uottawa", "ottawa", "uo"] and len(args.term) == 3:
                is_subject_code = True
        
        if is_subject_code:
            subjects = [args.term]
            args.term = None  # Clear term since we don't need it for catalog

    # Validate arguments
    if not args.catalog and not args.term:
        print("Error: term is required when not using --catalog")
        return 1

    if args.catalog:
        # Show catalog courses (no live sections)
        print(f"Getting catalog courses from {args.university}...")
        
        if subjects:
            all_courses = []
            for subject in subjects:
                subject_courses = provider.get_courses(subject_code=subject.upper())
                # Apply limit per subject if specified
                if args.limit > 0:
                    subject_courses = subject_courses[:args.limit]
                all_courses.extend(subject_courses)
        else:
            # Get all courses if no subjects specified
            all_courses = provider.get_courses()
            if args.limit > 0:
                all_courses = all_courses[:args.limit]

        print(f"Found {len(all_courses)} catalog courses")

        # Group by subject for better display
        courses_by_subject = {}
        for course in all_courses:
            subject = course.subject_code
            if subject not in courses_by_subject:
                courses_by_subject[subject] = []
            courses_by_subject[subject].append(course)

        for subject in sorted(courses_by_subject.keys()):
            subject_courses = courses_by_subject[subject]
            print(f"\n{subject} - {len(subject_courses)} courses:")
            for course in subject_courses:
                print(f"  {course.course_code}: {course.title}")
                if hasattr(course, 'credits') and course.credits:
                    print(f"    Credits: {course.credits}")

    else:
        # Original live courses discovery
        term_code = parse_term(args.term)
        
        print(f"Discovering {args.university} courses for {args.term}...")

        result = provider.discover_courses(
            term_code=term_code, subjects=subjects, max_courses_per_subject=args.limit
        )

        print(f"Found {result.courses_offered}/{result.total_courses} offered courses")

        for course in result.courses:
            print(f"\n{course.course_code}: {course.title}")
            if course.sections:
                lectures = len(
                    [s for s in course.sections if "lecture" in s.schedule_type.lower()]
                )
                tutorials = len(
                    [s for s in course.sections if "tutorial" in s.schedule_type.lower()]
                )
                labs = len([s for s in course.sections if "lab" in s.schedule_type.lower()])

                parts = []
                if lectures:
                    parts.append(f"{lectures} lectures")
                if tutorials:
                    parts.append(f"{tutorials} tutorials")
                if labs:
                    parts.append(f"{labs} labs")

                print(f"  Sections: {len(course.sections)} ({', '.join(parts)})")


def cmd_course(args: argparse.Namespace):
    """Get details for a specific course."""
    provider = get_provider(args.university)
    term_code = parse_term(args.term)

    course_code = args.course_code.upper().replace(" ", "")
    subject = "".join(c for c in course_code if c.isalpha())

    print(f"Getting details for {course_code} at {args.university}...")

    result = provider.discover_courses(
        term_code=term_code,
        subjects=[subject],
        course_codes=[course_code],
        max_courses_per_subject=50,
    )

    if result.courses:
        course = result.courses[0]
        print(f"\n{course.course_code}: {course.title}")
        print(f"Credits: {course.credits}")

        if course.sections:
            lectures = [
                s for s in course.sections if "lecture" in s.schedule_type.lower()
            ]
            tutorials = [
                s for s in course.sections if "tutorial" in s.schedule_type.lower()
            ]
            labs = [s for s in course.sections if "lab" in s.schedule_type.lower()]

            print(f"\nSections Summary:")
            print(f"  Total: {len(course.sections)}")
            if lectures:
                print(f"  Lectures: {len(lectures)}")
            if tutorials:
                print(f"  Tutorials: {len(tutorials)}")
            if labs:
                print(f"  Labs: {len(labs)}")

            print(f"\nAll Sections:")
            for section in course.sections:
                status_str = f" - {section.status}" if section.status else ""
                print(
                    f"  {section.section} ({section.schedule_type}) - CRN {section.crn}{status_str}"
                )
                if section.instructor and section.instructor != "TBA":
                    print(f"    Instructor: {section.instructor}")
    else:
        print(f"Course {course_code} not found for {args.term}")


def cmd_server(args: argparse.Namespace):
    """Start the API server."""
    import uvicorn
    from uoapi.server.app import create_app

    app = create_app()
    print("Starting Schedulo API server...")
    print(f"Server: http://127.0.0.1:{args.port}")
    print(f"Docs: http://127.0.0.1:{args.port}/docs")

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")


def cmd_professor(args: argparse.Namespace):
    """Get Rate My Professor ratings for an instructor."""
    from uoapi.rmp.rate_my_prof import get_professor_ratings
    
    # Map university names to school names for RMP
    university_to_school = {
        "carleton": "Carleton University",
        "cu": "Carleton University", 
        "uottawa": "University of Ottawa",
        "ottawa": "University of Ottawa",
        "uo": "University of Ottawa"
    }
    
    university = args.university.lower()
    if university not in university_to_school:
        print(f"Error: University '{args.university}' not supported.")
        print("Available universities: carleton, uottawa")
        return
    
    school_name = university_to_school[university]
    
    try:
        print(f"Searching for {args.first_name} {args.last_name} at {school_name}...")
        
        # Get ratings using RMP API
        ratings = get_professor_ratings([(args.first_name, args.last_name)], school_name)
        
        if not ratings:
            print(f"No ratings found for {args.first_name} {args.last_name} at {school_name}")
            print("\nTips:")
            print("- Try different name variations (nicknames, middle names)")
            print("- Check spelling of first and last name")
            print("- Some professors may not be on Rate My Professor")
            return
        
        professor = ratings[0]
        
        print(f"\n📊 Professor Rating: {args.first_name} {args.last_name}")
        print("=" * 50)
        
        if professor.get("rating"):
            print(f"Overall Rating: {professor['rating']:.1f}/5.0 ⭐")
        else:
            print("Overall Rating: Not available")
            
        print(f"Number of Ratings: {professor.get('num_ratings', 0)}")
        
        if professor.get('department'):
            print(f"Department: {professor['department']}")
            
        if professor.get('would_take_again_percent') is not None:
            print(f"Would Take Again: {professor['would_take_again_percent']:.0f}%")
            
        if professor.get('avg_difficulty') is not None:
            print(f"Average Difficulty: {professor['avg_difficulty']:.1f}/5.0")
            
        if professor.get('rmp_id'):
            print(f"Rate My Professor ID: {professor['rmp_id']}")
            print(f"Profile URL: https://www.ratemyprofessors.com/professor/{professor['rmp_id']}")
        
        # Provide interpretation
        rating = professor.get('rating')
        if rating:
            print(f"\n📝 Rating Interpretation:")
            if rating >= 4.0:
                print("🟢 Excellent professor (4.0+ rating)")
            elif rating >= 3.0:
                print("🟡 Good professor (3.0+ rating)")  
            elif rating >= 2.0:
                print("🟠 Fair professor (2.0+ rating)")
            else:
                print("🔴 Below average professor (<2.0 rating)")
                
    except Exception as e:
        print(f"Error retrieving professor ratings: {e}")
        print("This may be due to network issues or Rate My Professor API changes.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="schedulo", description="Simple CLI for University course data"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # terms
    terms_parser = subparsers.add_parser("terms", help="List available terms")
    terms_parser.add_argument("university", help="University (carleton, uottawa)")
    terms_parser.set_defaults(func=cmd_terms)

    # subjects
    subjects_parser = subparsers.add_parser("subjects", help="List available subjects")
    subjects_parser.add_argument("university", help="University (carleton, uottawa)")
    subjects_parser.add_argument(
        "--full", "-f", action="store_true", help="Show all subjects (default: first 20)"
    )
    subjects_parser.set_defaults(func=cmd_subjects)

    # courses
    courses_parser = subparsers.add_parser("courses", help="List courses for subjects")
    courses_parser.add_argument("university", help="University (carleton, uottawa)")
    courses_parser.add_argument("term", nargs="?", help="Term (fall2025, winter2025, 202530) - not needed with --catalog")
    courses_parser.add_argument(
        "subjects", nargs="*", help="Subject codes (COMP, MATH, CSI)"
    )
    courses_parser.add_argument(
        "--limit", "-l", type=int, default=10, help="Max courses per subject"
    )
    courses_parser.add_argument(
        "--catalog", "-c", action="store_true", help="Show catalog courses (no live sections)"
    )
    courses_parser.set_defaults(func=cmd_courses)

    # course
    course_parser = subparsers.add_parser(
        "course", help="Get details for a specific course"
    )
    course_parser.add_argument("university", help="University (carleton, uottawa)")
    course_parser.add_argument("course_code", help="Course code (COMP1005, CSI3140)")
    course_parser.add_argument("term", help="Term (fall2025, winter2025, 202530)")
    course_parser.set_defaults(func=cmd_course)

    # professor
    professor_parser = subparsers.add_parser(
        "professor", help="Get Rate My Professor ratings for an instructor"
    )
    professor_parser.add_argument("first_name", help="Professor's first name")
    professor_parser.add_argument("last_name", help="Professor's last name")
    professor_parser.add_argument("university", help="University (carleton, uottawa)")
    professor_parser.set_defaults(func=cmd_professor)

    # server
    server_parser = subparsers.add_parser("server", help="Start API server")
    server_parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Port (default: 8000)"
    )
    server_parser.set_defaults(func=cmd_server)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        args.func(args)
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


# Legacy CLI function for backward compatibility
def cli():
    """Legacy entry point."""
    return main()


if __name__ == "__main__":
    sys.exit(main())
