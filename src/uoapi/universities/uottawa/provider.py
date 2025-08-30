"""
University of Ottawa provider implementation.

This module wraps the existing UOttawa scraping functionality
to implement the UniversityProvider interface.
"""

from typing import List, Optional, Tuple, Dict, Any
import logging

from uoapi.core import (
    University,
    Subject,
    Course,
    SearchResult,
    DiscoveryResult,
    ProviderError,
    DataSourceError,
    NetworkError,
)
from uoapi.universities.base import BaseUniversityProvider

# Import existing functionality
from uoapi.course.course_info import scrape_subjects, get_courses
from uoapi.course.models import Subject as OldSubject, Course as OldCourse

logger = logging.getLogger(__name__)


class UOttawaProvider(BaseUniversityProvider):
    """
    University of Ottawa course data provider.
    
    This provider scrapes course information from the University of Ottawa
    course catalog website.
    """
    
    def __init__(self):
        super().__init__()
        self._base_url = "https://catalogue.uottawa.ca/en/courses/"
    
    @property
    def university(self) -> University:
        return University.UOTTAWA
    
    @property
    def name(self) -> str:
        return "University of Ottawa"
    
    def get_subjects(self) -> List[Subject]:
        """
        Retrieve all available subjects from UOttawa catalog.
        
        Uses cached data if available and valid.
        """
        if self._is_cache_valid() and self._subjects_cache:
            logger.debug("Using cached subjects data")
            return self._subjects_cache
        
        try:
            logger.info("Scraping subjects from UOttawa catalog")
            raw_subjects = scrape_subjects(self._base_url)
            
            subjects = []
            for subject_data in raw_subjects:
                # Convert from old Subject model to new unified model
                subjects.append(Subject(
                    name=subject_data['subject'],
                    code=subject_data['subject_code'],
                    university=self.university,
                    url=subject_data.get('link')
                ))
            
            # Cache the results
            self._subjects_cache = subjects
            self._update_cache_timestamp()
            
            logger.info(f"Successfully scraped {len(subjects)} subjects")
            return subjects
            
        except Exception as e:
            logger.error(f"Failed to scrape subjects: {e}")
            raise DataSourceError(f"Failed to retrieve subjects from UOttawa: {str(e)}")
    
    def get_courses(self, subject_code: Optional[str] = None) -> List[Course]:
        """
        Retrieve courses from UOttawa catalog.
        
        Args:
            subject_code: Optional subject code to filter by
            
        Returns:
            List of Course objects
        """
        if self._is_cache_valid() and self._courses_cache:
            logger.debug("Using cached courses data")
            courses = self._courses_cache
        else:
            logger.info("Scraping courses from UOttawa catalog")
            courses = self._scrape_all_courses()
            self._courses_cache = courses
            self._update_cache_timestamp()
        
        # Filter by subject code if provided
        if subject_code:
            normalized_code = self._normalize_subject_code(subject_code)
            filtered_courses = [
                course for course in courses 
                if course.subject_code == normalized_code
            ]
            logger.info(f"Filtered to {len(filtered_courses)} courses for subject {subject_code}")
            return filtered_courses
        
        return courses
    
    def _scrape_all_courses(self) -> List[Course]:
        """
        Scrape all courses from all subjects.
        
        Returns:
            List of Course objects
        """
        all_courses = []
        subjects = self.get_subjects()
        
        for subject in subjects:
            if not subject.url:
                logger.warning(f"No URL available for subject {subject.code}")
                continue
                
            try:
                logger.debug(f"Scraping courses for subject {subject.code}")
                raw_courses = list(get_courses(subject.url))
                
                for course_data in raw_courses:
                    try:
                        course = self._convert_old_course_to_new(course_data, subject)
                        all_courses.append(course)
                    except Exception as e:
                        logger.warning(f"Failed to convert course {course_data.get('course_code', 'unknown')}: {e}")
                        continue
                        
                logger.debug(f"Scraped {len(raw_courses)} courses for {subject.code}")
                
            except Exception as e:
                logger.error(f"Failed to scrape courses for subject {subject.code}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(all_courses)} total courses")
        return all_courses
    
    def _convert_old_course_to_new(self, old_course_data: Dict[str, Any], subject: Subject) -> Course:
        """
        Convert old course data format to new unified Course model.
        
        Args:
            old_course_data: Course data in old format
            subject: Subject this course belongs to
            
        Returns:
            Course object in new format
        """
        course_code = self._normalize_course_code(old_course_data['course_code'])
        
        return Course(
            course_code=course_code,
            subject_code=subject.code,
            course_number=self._extract_course_number(course_code),
            title=old_course_data.get('title', ''),
            description=old_course_data.get('description', ''),
            credits=old_course_data.get('credits', 0),
            university=self.university,
            components=old_course_data.get('components', []),
            prerequisites=old_course_data.get('prerequisites', ''),
            prerequisite_courses=old_course_data.get('dependencies', []),
            sections=[],  # UOttawa provider doesn't have live section data
            is_offered=True,  # Assume offered if in catalog
        )
    
    def supports_live_data(self) -> bool:
        """UOttawa provider only supports catalog data, not live timetables."""
        return False
    
    def get_available_terms(self) -> List[Tuple[str, str]]:
        """UOttawa provider doesn't support live data."""
        raise NotImplementedError("UOttawa provider doesn't support live timetable data")
    
    def discover_courses(
        self,
        term_code: str,
        subjects: Optional[List[str]] = None,
        course_codes: Optional[List[str]] = None,
        max_courses_per_subject: int = 50
    ) -> DiscoveryResult:
        """UOttawa provider doesn't support live data discovery."""
        raise NotImplementedError("UOttawa provider doesn't support live course discovery")