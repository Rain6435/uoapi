"""
Timetable command implementation.

This module provides CLI commands for querying live timetable information
using the new service-based architecture.
"""

import argparse
from typing import Any, Dict, List

from uoapi.core import University, ServiceError, LiveDataNotSupportedError, TermNotAvailableError
from uoapi.interfaces.cli.framework import UniversityCommand


class TimetableCommand(UniversityCommand):
    """
    CLI command for querying live timetable information.
    
    This command provides access to current semester course schedules
    for universities that support live data.
    """
    
    @property
    def name(self) -> str:
        return "timetable"
    
    @property
    def help(self) -> str:
        return "Query live timetable and course schedule data"
    
    @property
    def description(self) -> str:
        return (
            "Query live course schedule data including sections, instructors, "
            "and meeting times. Shows available terms by default, or discovers "
            "courses for a specific term and subjects."
        )
    
    @property
    def epilog(self) -> str:
        return (
            "Examples:\n"
            "  uoapi timetable -u carleton                    # Show available terms\n"
            "  uoapi timetable -u carleton --term 202501 --subjects COMP MATH\n"
            "  uoapi timetable -u carleton --term 202501 --subjects COMP --courses COMP1001,COMP1002\n"
            "  uoapi timetable -u carleton --term 202501 --subjects COMP --limit 20 --ratings"
        )
    
    def configure_command_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Configure timetable-specific arguments."""
        parser.add_argument(
            "--term",
            type=str,
            help="Term code (e.g., 202501 for Winter 2025)"
        )
        parser.add_argument(
            "--subjects",
            type=str,
            help="Comma-separated list of subject codes (e.g., COMP,MATH,PHYS)"
        )
        parser.add_argument(
            "--courses",
            type=str,
            help="Comma-separated list of specific course codes (e.g., COMP1001,MATH1007)"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum courses per subject (default: 50)"
        )
        parser.add_argument(
            "--ratings",
            action="store_true",
            default=False,
            help="Include Rate My Professor ratings for instructors"
        )
        
        return parser
    
    def execute_for_university(self, args: argparse.Namespace, university: University) -> Any:
        """Execute the timetable command for a specific university."""
        try:
            # Check if university supports live data
            supported_universities = self.timetable_service.get_supported_universities()
            if university not in supported_universities:
                return self.handle_error(
                    LiveDataNotSupportedError(university.value),
                    "Live data check"
                )
            
            # If no term specified, show available terms
            if not args.term:
                return self._show_available_terms(university)
            
            # Validate required arguments for term query
            if not args.subjects:
                return self.handle_error(
                    ValueError("--subjects is required when --term is specified"),
                    "Argument validation"
                )
            
            # Query live course data
            return self._query_live_courses(args, university)
            
        except ServiceError as e:
            return self.handle_error(e, "Timetable query")
        except Exception as e:
            return self.handle_error(e, "Unexpected error")
    
    def _show_available_terms(self, university: University) -> Dict[str, Any]:
        """Show available terms for the university."""
        try:
            terms = self.timetable_service.get_available_terms(university)
            
            terms_data = [
                {
                    'term_code': code,
                    'term_name': name,
                    'formatted_name': self.timetable_service.format_term_name(code)
                }
                for code, name in terms
            ]
            
            messages = [f"Found {len(terms)} available terms for {university.value}"]
            
            return self.format_output({
                'university': university.value,
                'available_terms': terms_data
            }, messages)
            
        except Exception as e:
            return self.handle_error(e, "Getting available terms")
    
    def _query_live_courses(self, args: argparse.Namespace, university: University) -> Dict[str, Any]:
        """Query live course data for the specified term and subjects."""
        try:
            # Parse subjects
            subjects = [s.strip().upper() for s in args.subjects.split(',')]
            
            # Parse course codes if provided
            course_codes = None
            if args.courses:
                course_codes = [c.strip().upper() for c in args.courses.split(',')]
            
            # Discover courses
            result = self.timetable_service.get_live_courses(
                university=university,
                term_code=args.term,
                subjects=subjects,
                course_codes=course_codes,
                max_courses_per_subject=args.limit
            )
            
            # Enhance with ratings if requested
            if args.ratings:
                try:
                    enhanced_courses = self.rating_service.inject_ratings_into_courses(
                        result.courses, university
                    )
                    result.courses = enhanced_courses
                except Exception as e:
                    # Don't fail the whole request if ratings fail
                    pass
            
            # Convert result to dictionary format
            result_data = {
                'university': result.university.value,
                'term_code': result.term_code,
                'term_name': result.term_name,
                'subjects_queried': result.subjects_queried,
                'total_courses': result.total_courses,
                'courses_offered': result.courses_offered,
                'courses_with_errors': result.courses_with_errors,
                'offering_rate_percent': round(result.offering_rate, 2),
                'processing_time_seconds': round(result.processing_time or 0, 2),
                'courses': self._format_courses_for_output(result.courses)
            }
            
            messages = [
                f"Discovered {result.total_courses} courses",
                f"Offering rate: {result.offering_rate:.1f}%",
            ]
            
            if result.processing_time:
                messages.append(f"Processing time: {result.processing_time:.2f}s")
            
            if args.ratings:
                messages.append("Rate My Professor ratings included where available")
            
            return self.format_output(result_data, messages)
            
        except TermNotAvailableError as e:
            return self.handle_error(e, "Term validation")
        except Exception as e:
            return self.handle_error(e, "Course discovery")
    
    def _format_courses_for_output(self, courses) -> List[Dict[str, Any]]:
        """Format courses for JSON output."""
        courses_data = []
        
        for course in courses:
            course_dict = {
                'course_code': course.course_code,
                'subject_code': course.subject_code,
                'course_number': course.course_number,
                'title': course.title,
                'credits': course.credits,
                'is_offered': course.is_offered,
                'sections_found': len(course.sections),
                'sections': []
            }
            
            # Format sections
            for section in course.sections:
                section_dict = {
                    'crn': section.crn,
                    'section': section.section,
                    'status': section.status,
                    'credits': section.credits,
                    'schedule_type': section.schedule_type,
                    'instructor': section.instructor,
                    'notes': section.notes,
                    'meeting_times': []
                }
                
                # Format meeting times
                for mt in section.meeting_times:
                    meeting_dict = {
                        'days': mt.days,
                        'start_time': mt.start_time,
                        'end_time': mt.end_time,
                        'start_date': mt.start_date,
                        'end_date': mt.end_date,
                    }
                    section_dict['meeting_times'].append(meeting_dict)
                
                # Add enrollment info if available
                if section.capacity is not None:
                    section_dict['capacity'] = section.capacity
                if section.enrolled is not None:
                    section_dict['enrolled'] = section.enrolled
                if section.remaining is not None:
                    section_dict['remaining'] = section.remaining
                
                course_dict['sections'].append(section_dict)
            
            courses_data.append(course_dict)
        
        return courses_data