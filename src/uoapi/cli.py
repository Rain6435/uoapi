#!/usr/bin/env python3
"""
Clean, unified CLI for Schedulo API.

Usage:
  schedulo terms carleton                          # List available terms
  schedulo courses carleton fall2025 COMP         # List COMP courses  
  schedulo course carleton COMP1005 fall2025      # Get course details
  schedulo subjects carleton                       # List subjects
  schedulo server                                  # Start API server
"""

import argparse
import sys


def get_provider(university: str):
    """Get the appropriate provider for a university."""
    if university.lower() in ['carleton', 'cu']:
        from uoapi.universities.carleton.provider import CarletonProvider
        return CarletonProvider()
    else:
        raise ValueError(f"University '{university}' not supported. Available: carleton")


def parse_term(term_str: str) -> str:
    """Convert friendly term format to term code."""
    term_mapping = {
        'fall2025': '202530',
        'winter2025': '202510', 
        'summer2025': '202520',
        'fall2024': '202430',
        'winter2024': '202410',
        'summer2024': '202420',
    }
    
    if term_str.isdigit() and len(term_str) == 6:
        return term_str
    
    return term_mapping.get(term_str.lower(), term_str)


def cmd_terms(args):
    """List available terms."""
    provider = get_provider(args.university)
    print(f"Available terms at {args.university}:")
    
    terms = provider.get_available_terms()
    for code, name in terms:
        print(f"  {code}: {name}")


def cmd_subjects(args):
    """List available subjects."""
    provider = get_provider(args.university)
    print(f"Available subjects at {args.university}:")
    
    subjects = provider.get_subjects()
    for subject in sorted(subjects, key=lambda s: s.code)[:20]:  # Show first 20
        print(f"  {subject.code}: {subject.name}")
    
    if len(subjects) > 20:
        print(f"  ... and {len(subjects) - 20} more")


def cmd_courses(args):
    """List courses for subjects."""
    provider = get_provider(args.university)
    term_code = parse_term(args.term)
    subjects = args.subjects if args.subjects else None
    
    print(f"Discovering {args.university} courses for {args.term}...")
    
    result = provider.discover_courses(
        term_code=term_code,
        subjects=subjects,
        max_courses_per_subject=args.limit
    )
    
    print(f"Found {result.courses_offered}/{result.total_courses} offered courses")
    
    for course in result.courses:
        print(f"\n{course.course_code}: {course.title}")
        if course.sections:
            lectures = len([s for s in course.sections if 'lecture' in s.schedule_type.lower()])
            tutorials = len([s for s in course.sections if 'tutorial' in s.schedule_type.lower()])
            labs = len([s for s in course.sections if 'lab' in s.schedule_type.lower()])
            
            parts = []
            if lectures: parts.append(f"{lectures} lectures")
            if tutorials: parts.append(f"{tutorials} tutorials") 
            if labs: parts.append(f"{labs} labs")
            
            print(f"  Sections: {len(course.sections)} ({', '.join(parts)})")


def cmd_course(args):
    """Get details for a specific course."""
    provider = get_provider(args.university)
    term_code = parse_term(args.term)
    
    course_code = args.course_code.upper().replace(' ', '')
    subject = ''.join(c for c in course_code if c.isalpha())
    
    print(f"Getting details for {course_code} at {args.university}...")
    
    result = provider.discover_courses(
        term_code=term_code,
        subjects=[subject],
        course_codes=[course_code],
        max_courses_per_subject=50
    )
    
    if result.courses:
        course = result.courses[0]
        print(f"\n{course.course_code}: {course.title}")
        print(f"Credits: {course.credits}")
        
        if course.sections:
            lectures = [s for s in course.sections if 'lecture' in s.schedule_type.lower()]
            tutorials = [s for s in course.sections if 'tutorial' in s.schedule_type.lower()]
            labs = [s for s in course.sections if 'lab' in s.schedule_type.lower()]
            
            print(f"\nSections Summary:")
            print(f"  Total: {len(course.sections)}")
            if lectures: print(f"  Lectures: {len(lectures)}")
            if tutorials: print(f"  Tutorials: {len(tutorials)}")
            if labs: print(f"  Labs: {len(labs)}")
                
            print(f"\nAll Sections:")
            for section in course.sections:
                status_str = f" - {section.status}" if section.status else ""
                print(f"  {section.section} ({section.schedule_type}) - CRN {section.crn}{status_str}")
                if section.instructor and section.instructor != "TBA":
                    print(f"    Instructor: {section.instructor}")
    else:
        print(f"Course {course_code} not found for {args.term}")


def cmd_server(args):
    """Start the API server."""
    import uvicorn
    from uoapi.server.app import create_app
    
    app = create_app()
    print("Starting Schedulo API server...")
    print(f"Server: http://127.0.0.1:{args.port}")
    print(f"Docs: http://127.0.0.1:{args.port}/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='schedulo',
        description='Simple CLI for University course data'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # terms
    terms_parser = subparsers.add_parser('terms', help='List available terms')
    terms_parser.add_argument('university', help='University (carleton)')
    terms_parser.set_defaults(func=cmd_terms)
    
    # subjects  
    subjects_parser = subparsers.add_parser('subjects', help='List available subjects')
    subjects_parser.add_argument('university', help='University (carleton)')
    subjects_parser.set_defaults(func=cmd_subjects)
    
    # courses
    courses_parser = subparsers.add_parser('courses', help='List courses for subjects')
    courses_parser.add_argument('university', help='University (carleton)')
    courses_parser.add_argument('term', help='Term (fall2025, winter2025, 202530)')
    courses_parser.add_argument('subjects', nargs='*', help='Subject codes (COMP, MATH)')
    courses_parser.add_argument('--limit', '-l', type=int, default=10, help='Max courses per subject')
    courses_parser.set_defaults(func=cmd_courses)
    
    # course
    course_parser = subparsers.add_parser('course', help='Get details for a specific course')
    course_parser.add_argument('university', help='University (carleton)')
    course_parser.add_argument('course_code', help='Course code (COMP1005)')
    course_parser.add_argument('term', help='Term (fall2025, winter2025, 202530)')
    course_parser.set_defaults(func=cmd_course)
    
    # server
    server_parser = subparsers.add_parser('server', help='Start API server')
    server_parser.add_argument('--port', '-p', type=int, default=8000, help='Port (default: 8000)')
    server_parser.set_defaults(func=cmd_server)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
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


if __name__ == '__main__':
    sys.exit(main())