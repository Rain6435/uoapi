"""
Course command implementation.

This module provides CLI commands for querying course information
using the new service-based architecture.
"""

import argparse
from typing import Any, Dict, List

from uoapi.core import University, ServiceError
from uoapi.interfaces.cli.framework import UniversityCommand


class CourseCommand(UniversityCommand):
    """
    CLI command for querying course information.
    
    This command replaces the old course module CLI with a service-based
    implementation that provides the same functionality.
    """
    
    @property
    def name(self) -> str:
        return "course"
    
    @property
    def help(self) -> str:
        return "Query subjects and courses from university catalogs"
    
    @property
    def description(self) -> str:
        return (
            "Query the subject table and course information. "
            "By default, shows the subjects table. Use --courses to include "
            "course details. Use --nosubjects to suppress the subjects table. "
            "Provide subject codes as arguments to filter courses by subject."
        )
    
    @property
    def epilog(self) -> str:
        return (
            "Examples:\n"
            "  uoapi course -u uottawa                    # Show all subjects\n"
            "  uoapi course -u uottawa -c                 # Show subjects and all courses\n"
            "  uoapi course -u uottawa -c CSI MATH        # Show courses for CSI and MATH\n"
            "  uoapi course -u uottawa -s -c CSI          # Show only CSI courses, no subjects table\n"
            "  uoapi course -u carleton --search \"database\" # Search for courses containing 'database'"
        )
    
    def configure_command_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Configure course-specific arguments."""
        parser.add_argument(
            "-c", "--courses",
            action="store_true",
            default=False,
            help="Query for course information as well"
        )
        parser.add_argument(
            "-s", "--nosubjects",
            action="store_true",
            default=False,
            help="Suppress output of subjects table"
        )
        parser.add_argument(
            "--search",
            type=str,
            help="Search query for course titles and descriptions"
        )
        parser.add_argument(
            "subjects",
            nargs="*",
            help="Subject codes to filter courses (e.g., CSI MATH PHYS)"
        )
        
        return parser
    
    def execute_for_university(self, args: argparse.Namespace, university: University) -> Any:
        """Execute the course command for a specific university."""
        result_data = {}
        messages = []
        
        try:
            # Get subjects if not suppressed
            if not args.nosubjects:
                subjects = self.course_service.get_subjects(university)
                result_data['subjects'] = [
                    {
                        'code': s.code,
                        'name': s.name,
                        'url': s.url
                    }
                    for s in subjects
                ]
                messages.append(f"Found {len(subjects)} subjects")
            
            # Get courses if requested
            if args.courses or args.search or args.subjects:
                courses_data = self._get_courses_data(args, university, messages)
                if courses_data:
                    result_data['courses'] = courses_data
            
            return self.format_output(result_data, messages)
            
        except ServiceError as e:
            return self.handle_error(e, "Course query")
        except Exception as e:
            return self.handle_error(e, "Unexpected error")
    
    def _get_courses_data(self, args: argparse.Namespace, university: University, messages: List[str]) -> List[Dict[str, Any]]:
        """Get courses data based on the command arguments."""
        all_courses = []
        
        if args.search:
            # Search functionality
            if args.subjects:
                # Search within specific subjects
                for subject_code in args.subjects:
                    try:
                        search_result = self.course_service.search_courses(
                            university, args.search, subject_code
                        )
                        all_courses.extend(search_result.courses)
                        messages.append(f"Found {search_result.total_found} courses in {subject_code} matching '{args.search}'")
                    except ServiceError as e:
                        messages.append(f"Error searching in {subject_code}: {str(e)}")
            else:
                # Search across all subjects
                try:
                    search_result = self.course_service.search_courses(university, args.search)
                    all_courses = search_result.courses
                    messages.append(f"Found {search_result.total_found} courses matching '{args.search}'")
                except ServiceError as e:
                    messages.append(f"Error searching courses: {str(e)}")
        
        elif args.subjects:
            # Get courses for specific subjects
            for subject_code in args.subjects:
                try:
                    courses = self.course_service.get_courses(university, subject_code)
                    all_courses.extend(courses)
                    messages.append(f"Found {len(courses)} courses in {subject_code}")
                except ServiceError as e:
                    messages.append(f"Error getting courses for {subject_code}: {str(e)}")
        
        else:
            # Get all courses
            try:
                courses = self.course_service.get_courses(university)
                all_courses = courses
                messages.append(f"Found {len(courses)} total courses")
            except ServiceError as e:
                messages.append(f"Error getting all courses: {str(e)}")
        
        # Convert courses to dictionaries
        courses_data = []
        for course in all_courses:
            course_dict = {
                'course_code': course.course_code,
                'subject_code': course.subject_code,
                'course_number': course.course_number,
                'title': course.title,
                'credits': course.credits,
                'description': course.description,
                'components': course.components,
                'prerequisites': course.prerequisites,
                'is_offered': course.is_offered,
            }
            
            # Add sections if available
            if course.sections:
                course_dict['sections'] = [
                    {
                        'crn': s.crn,
                        'section': s.section,
                        'status': s.status,
                        'credits': s.credits,
                        'instructor': s.instructor,
                        'schedule_type': s.schedule_type,
                        'meeting_times': [
                            {
                                'days': mt.days,
                                'start_time': mt.start_time,
                                'end_time': mt.end_time,
                                'start_date': mt.start_date,
                                'end_date': mt.end_date,
                            }
                            for mt in s.meeting_times
                        ],
                        'notes': s.notes,
                    }
                    for s in course.sections
                ]
            
            courses_data.append(course_dict)
        
        return courses_data