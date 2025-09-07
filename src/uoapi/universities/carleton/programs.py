"""
Carleton programs data provider.

This module fetches program information from Carleton University's JSON API
and provides filtering capabilities similar to the web interface.
"""

import requests
from typing import List, Optional, Dict, Any, Set
import logging
from enum import Enum

from uoapi.core import (
    University,
    ProviderError,
)

# Reuse the enums from UOttawa but adjust for Carleton
from uoapi.universities.uottawa.programs import (
    ProgramType, 
    ProgramDegreeType, 
    Faculty, 
    Discipline, 
    Program
)

logger = logging.getLogger(__name__)

# Carleton-specific faculty mapping
class CarletonFaculty(str, Enum):
    """Carleton University faculties."""
    ARTS_AND_SOCIAL_SCIENCES = "faculty-of-arts-and-social-sciences"
    ENGINEERING_AND_DESIGN = "faculty-of-engineering-and-design"
    PUBLIC_AND_GLOBAL_AFFAIRS = "faculty-of-public-and-global-affairs"
    SCIENCE = "faculty-of-science"
    SPROTT_SCHOOL_OF_BUSINESS = "sprott-school-of-business"

# Mapping from Carleton API faculty strings to our unified Faculty enum
CARLETON_FACULTY_MAPPING = {
    "faculty-of-arts-and-social-sciences": Faculty.ARTS,
    "faculty-of-engineering-and-design": Faculty.ENGINEERING,
    "faculty-of-public-and-global-affairs": Faculty.SOCIAL_SCIENCES,
    "faculty-of-science": Faculty.SCIENCE,
    "sprott-school-of-business": Faculty.MANAGEMENT,
}

# Mapping from Carleton degree names to our unified degree types
CARLETON_DEGREE_TYPE_MAPPING = {
    "Arts": ProgramDegreeType.BACHELOR,
    "Science": ProgramDegreeType.BACHELOR,
    "Engineering": ProgramDegreeType.BACHELOR,
    "Commerce (Business)": ProgramDegreeType.BACHELOR,
    "Computer Science": ProgramDegreeType.BACHELOR,
    "Mathematics": ProgramDegreeType.BACHELOR,
    "Bachelor of Accounting": ProgramDegreeType.BACHELOR,
    "Global and International Studies": ProgramDegreeType.BACHELOR,
    "Information Technology": ProgramDegreeType.BACHELOR,
    "International Business": ProgramDegreeType.BACHELOR,
    "Journalism": ProgramDegreeType.BACHELOR,
    "Media Production and Design": ProgramDegreeType.BACHELOR,
    "Music": ProgramDegreeType.BACHELOR,
    "Public Affairs and Policy Management": ProgramDegreeType.BACHELOR,
    "Social Work": ProgramDegreeType.BACHELOR,
    "Cognitive Science": ProgramDegreeType.BACHELOR,
    "Communication and Media Studies": ProgramDegreeType.BACHELOR,
    "Data Science": ProgramDegreeType.BACHELOR,
    "Economics": ProgramDegreeType.BACHELOR,
    "Health Sciences": ProgramDegreeType.BACHELOR,
    "Humanities (Great Books)": ProgramDegreeType.BACHELOR,
    "Industrial Design": ProgramDegreeType.BACHELOR,
    "Journalism and Humanities": ProgramDegreeType.BACHELOR,
    "Nursing": ProgramDegreeType.BACHELOR,
    "Cybersecurity": ProgramDegreeType.BACHELOR,
    "Architectural Studies": ProgramDegreeType.BACHELOR,
}

# Common disciplines mapping for Carleton
CARLETON_DISCIPLINE_MAPPING = {
    "accounting": Discipline.ACCOUNTING,
    "computer-science": Discipline.COMPUTER_SCIENCE,
    "business": Discipline.BUSINESS,
    "economics": Discipline.ECONOMICS,
    "mathematics": Discipline.MATHEMATICS,
    "physics": Discipline.PHYSICS,
    "chemistry": Discipline.CHEMISTRY,
    "biology": Discipline.BIOLOGY,
    "psychology": Discipline.PSYCHOLOGY,
    "history": Discipline.HISTORY,
    "english": Discipline.ENGLISH,
    "journalism": Discipline.JOURNALISM,
    "music": Discipline.MUSIC,
    "nursing": Discipline.NURSING,
    # Add more mappings based on careers data
}


class CarletonProgramsProvider:
    """Provider for Carleton academic programs data."""
    
    def __init__(self):
        self.programs_url = "https://admissions.carleton.ca/wp-json/adm-api/programs"
        self._programs_cache: Optional[List[Program]] = None
    
    def _fetch_programs_data(self) -> List[Dict[str, Any]]:
        """Fetch programs data from Carleton's JSON API."""
        try:
            response = requests.get(self.programs_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data)} programs from Carleton API")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch programs from Carleton API: {e}")
            raise ProviderError(f"Failed to retrieve programs from Carleton: {str(e)}")
    
    def _parse_program_data(self, program_data: Dict[str, Any]) -> Program:
        """Parse a single program from Carleton API data."""
        
        # Extract basic information
        title = program_data.get("title", "")
        degree = program_data.get("degree", "")
        description = program_data.get("description", "")
        link = program_data.get("link", "")
        
        # Determine program level (all Carleton programs are undergraduate)
        level = ProgramType.UNDERGRADUATE
        
        # Map degree type
        degree_type = CARLETON_DEGREE_TYPE_MAPPING.get(degree, ProgramDegreeType.BACHELOR)
        
        # Determine faculty
        faculty = None
        faculty_list = program_data.get("faculty", [])
        if faculty_list:
            carleton_faculty = faculty_list[0]  # Take the first faculty
            faculty = CARLETON_FACULTY_MAPPING.get(carleton_faculty)
        
        # Determine discipline from careers/title
        discipline = None
        careers = program_data.get("careers", [])
        
        # Try to map discipline from title keywords first
        title_lower = title.lower()
        for keyword, disc in CARLETON_DISCIPLINE_MAPPING.items():
            if keyword.replace("-", " ") in title_lower:
                discipline = disc
                break
        
        # If no discipline from title, try from careers
        if not discipline and careers:
            for career in careers:
                if career in CARLETON_DISCIPLINE_MAPPING:
                    discipline = CARLETON_DISCIPLINE_MAPPING[career]
                    break
        
        # Generate program code from title
        program_code = title.upper().replace(" ", "").replace("(", "").replace(")", "")[:10]
        
        return Program(
            name=title,
            university=University.CARLETON,
            level=level,
            degree_type=degree_type,
            faculty=faculty,
            discipline=discipline,
            code=program_code,
            url=link,
            description=description,
            is_offered=True,
        )
    
    def get_programs(self) -> List[Program]:
        """Get all programs (cached)."""
        if self._programs_cache:
            return self._programs_cache
        
        raw_data = self._fetch_programs_data()
        programs = []
        
        for program_data in raw_data:
            try:
                program = self._parse_program_data(program_data)
                programs.append(program)
            except Exception as e:
                logger.warning(f"Failed to parse program {program_data.get('title', 'Unknown')}: {e}")
                continue
        
        self._programs_cache = programs
        logger.info(f"Parsed {len(programs)} programs from Carleton")
        return programs
    
    def get_programs_by_filters(
        self,
        level: Optional[ProgramType] = None,
        degree_type: Optional[ProgramDegreeType] = None,
        faculty: Optional[Faculty] = None,
        discipline: Optional[Discipline] = None,
    ) -> List[Program]:
        """Get programs filtered by criteria."""
        all_programs = self.get_programs()
        filtered_programs = []
        
        for program in all_programs:
            # Apply filters
            if level and program.level != level:
                continue
            if degree_type and program.degree_type != degree_type:
                continue
            if faculty and program.faculty != faculty:
                continue
            if discipline and program.discipline != discipline:
                continue
                
            filtered_programs.append(program)
        
        return filtered_programs
    
    def get_program_by_name(self, name: str) -> Optional[Program]:
        """Get a specific program by name."""
        all_programs = self.get_programs()
        
        # Normalize name for comparison
        normalized_name = name.lower().strip()
        
        for program in all_programs:
            if normalized_name in program.name.lower():
                return program
                
        return None
    
    def get_unique_faculties(self) -> List[Faculty]:
        """Get list of unique faculties."""
        programs = self.get_programs()
        faculties: Set[Faculty] = set()
        
        for program in programs:
            if program.faculty:
                faculties.add(program.faculty)
                
        return sorted(list(faculties), key=lambda f: f.value)
    
    def get_unique_disciplines(self) -> List[Discipline]:
        """Get list of unique disciplines."""
        programs = self.get_programs()
        disciplines: Set[Discipline] = set()
        
        for program in programs:
            if program.discipline:
                disciplines.add(program.discipline)
                
        return sorted(list(disciplines), key=lambda d: d.value)