"""
UOttawa programs data provider.

This module scrapes program information from the UOttawa programs page
and provides filtering capabilities similar to the web interface.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any, Set
import re
import logging
from enum import Enum

from uoapi.core import (
    University,
    ProviderError,
)

logger = logging.getLogger(__name__)

# Program-related data models
class ProgramType(str, Enum):
    """Types of academic programs."""
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    DUAL_LEVEL = "dual_level"

class ProgramDegreeType(str, Enum):
    """Types of degrees/credentials."""
    BACHELOR = "bachelor"
    CERTIFICATE = "certificate"
    DOCTORATE = "doctorate"
    DUAL_DEGREE = "dual_degree"
    GRADUATE_DIPLOMA = "graduate_diploma"
    JURIS_DOCTOR = "juris_doctor"
    LICENTIATE = "licentiate"
    MAJOR = "major"
    MASTER = "master"
    MICROPROGRAM = "microprogram"
    MINOR = "minor"
    ONLINE = "online"
    OPTION = "option"

class Faculty(str, Enum):
    """University faculties."""
    ARTS = "arts"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    HEALTH_SCIENCES = "health_sciences"
    LAW = "law"
    MANAGEMENT = "management"
    MEDICINE = "medicine"
    SCIENCE = "science"
    SOCIAL_SCIENCES = "social_sciences"

class Discipline(str, Enum):
    """Academic disciplines."""
    # Popular disciplines - expand based on full list from programs page
    ACCOUNTING = "accounting"
    ADVANCED_MATERIALS_MANUFACTURING = "advanced_materials_manufacturing"
    AFRICAN_STUDIES = "african_studies"
    ANTHROPOLOGY = "anthropology"
    ART_HISTORY = "art_history"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    AUDIOLOGY = "audiology"
    BIOCHEMISTRY = "biochemistry"
    BIOINFORMATICS = "bioinformatics"
    BIOLOGY = "biology"
    BIOMEDICAL_ENGINEERING = "biomedical_engineering"
    BIOMEDICAL_SCIENCE = "biomedical_science"
    BIOPHARMACEUTICAL_SCIENCE = "biopharmaceutical_science"
    BIOPHYSICS = "biophysics"
    BIOSTATISTICS = "biostatistics"
    BUSINESS = "business"
    BUSINESS_ANALYTICS = "business_analytics"
    CANADIAN_LAW = "canadian_law"
    CANADIAN_STUDIES = "canadian_studies"
    CELTIC_STUDIES = "celtic_studies"
    CHEMICAL_ENGINEERING = "chemical_engineering"
    CHEMISTRY = "chemistry"
    CINEMA = "cinema"
    CIVIL_ENGINEERING = "civil_engineering"
    CLASSICAL_STUDIES = "classical_studies"
    CLINICAL_SCIENCE_TRANSLATIONAL_MEDICINE = "clinical_science_translational_medicine"
    COMMUNICATION = "communication"
    COMPUTER_ENGINEERING = "computer_engineering"
    COMPUTER_SCIENCE = "computer_science"
    CONFERENCE_INTERPRETING = "conference_interpreting"
    CONFLICT_STUDIES_HUMAN_RIGHTS = "conflict_studies_human_rights"
    EARTH_SCIENCES = "earth_sciences"
    ECONOMICS = "economics"
    ELECTRICAL_ENGINEERING = "electrical_engineering"
    ENGLISH = "english"
    ENGLISH_AS_SECOND_LANGUAGE = "english_as_second_language"
    ENTREPRENEURSHIP = "entrepreneurship"
    ENVIRONMENT = "environment"
    ENVIRONMENTAL_ENGINEERING = "environmental_engineering"
    ENVIRONMENTAL_SCIENCE = "environmental_science"
    ENVIRONMENTAL_SUSTAINABILITY = "environmental_sustainability"
    EPIDEMIOLOGY = "epidemiology"
    ETHICS = "ethics"
    EXPERIMENTAL_MEDICINE = "experimental_medicine"
    FEMINIST_GENDER_STUDIES = "feminist_gender_studies"
    FINANCE = "finance"
    FINE_ARTS = "fine_arts"
    FOOD_NUTRITION = "food_nutrition"
    FRENCH = "french"
    FRENCH_AS_SECOND_LANGUAGE = "french_as_second_language"
    GENETICS = "genetics"
    GEOGRAPHY = "geography"
    GEOLOGY = "geology"
    GEOMATICS_SPATIAL_ANALYSIS = "geomatics_spatial_analysis"
    GERMAN = "german"
    GREEK_ROMAN_STUDIES = "greek_roman_studies"
    HEALTH = "health"
    HEALTH_SYSTEMS = "health_systems"
    HISTORY = "history"
    HUMAN_KINETICS = "human_kinetics"
    HUMAN_RESOURCE_MANAGEMENT = "human_resource_management"
    INDIGENOUS_STUDIES = "indigenous_studies"
    INFORMATION_STUDIES = "information_studies"
    INTERNATIONAL_AFFAIRS = "international_affairs"
    INTERNATIONAL_DEVELOPMENT = "international_development"
    INTERNATIONAL_ECONOMICS_DEVELOPMENT = "international_economics_development"
    INTERNATIONAL_STUDIES = "international_studies"
    ITALIAN = "italian"
    JEWISH_CANADIAN_STUDIES = "jewish_canadian_studies"
    JOURNALISM = "journalism"
    LATIN_AMERICAN_STUDIES = "latin_american_studies"
    LAW = "law"
    LIFE_SCIENCES = "life_sciences"
    LINGUISTICS = "linguistics"
    MANAGEMENT = "management"
    MARKETING = "marketing"
    MATHEMATICS = "mathematics"
    MECHANICAL_ENGINEERING = "mechanical_engineering"
    MEDIA = "media"
    MEDICINE = "medicine"
    MEDIEVAL_RENAISSANCE_STUDIES = "medieval_renaissance_studies"
    MICROBIOLOGY_IMMUNOLOGY = "microbiology_immunology"
    MUSIC = "music"
    NEUROSCIENCE = "neuroscience"
    NURSING = "nursing"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    OPHTHALMIC_MEDICAL_TECHNOLOGY = "ophthalmic_medical_technology"
    PHILOSOPHY = "philosophy"
    PHYSICS = "physics"
    PHYSIOTHERAPY = "physiotherapy"
    POLITICAL_SCIENCE = "political_science"
    PSYCHOLOGY = "psychology"
    PUBLIC_ADMINISTRATION = "public_administration"
    PUBLIC_HEALTH = "public_health"
    PUBLIC_POLICY = "public_policy"
    RELIGIOUS_STUDIES = "religious_studies"
    RUSSIAN = "russian"
    SECOND_LANGUAGE_TEACHING = "second_language_teaching"
    SOCIAL_IMPACT = "social_impact"
    SOCIAL_WORK = "social_work"
    SOCIOLOGY = "sociology"
    SOFTWARE_ENGINEERING = "software_engineering"
    SPANISH = "spanish"
    SPEECH_LANGUAGE_PATHOLOGY = "speech_language_pathology"
    STATISTICS = "statistics"
    THEATRE = "theatre"
    VISUAL_ARTS = "visual_arts"
    WORLD_CINEMAS = "world_cinemas"
    WRITING = "writing"

class Program:
    """Represents an academic program at a university."""
    
    def __init__(
        self,
        name: str,
        university: University,
        level: ProgramType = ProgramType.UNDERGRADUATE,
        degree_type: ProgramDegreeType = ProgramDegreeType.BACHELOR,
        faculty: Optional[Faculty] = None,
        discipline: Optional[Discipline] = None,
        code: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        credits_required: Optional[float] = None,
        duration_years: Optional[float] = None,
        is_offered: bool = True,
    ):
        self.name = name
        self.university = university
        self.level = level
        self.degree_type = degree_type
        self.faculty = faculty
        self.discipline = discipline
        self.code = code
        self.url = url
        self.description = description
        self.credits_required = credits_required
        self.duration_years = duration_years
        self.is_offered = is_offered

# Filter mapping from HTML filter IDs to enums
FILTER_MAPPINGS = {
    # Level filters
    "filter_19": ProgramType.UNDERGRADUATE,
    "filter_20": ProgramType.GRADUATE,
    "filter_185": ProgramType.DUAL_LEVEL,
    
    # Degree type filters
    "filter_21": ProgramDegreeType.BACHELOR,
    "filter_23": ProgramDegreeType.CERTIFICATE,
    "filter_25": ProgramDegreeType.DOCTORATE,
    "filter_189": ProgramDegreeType.DUAL_DEGREE,
    "filter_26": ProgramDegreeType.GRADUATE_DIPLOMA,
    "filter_190": ProgramDegreeType.JURIS_DOCTOR,
    "filter_163": ProgramDegreeType.LICENTIATE,
    "filter_164": ProgramDegreeType.MAJOR,
    "filter_24": ProgramDegreeType.MASTER,
    "filter_183": ProgramDegreeType.MICROPROGRAM,
    "filter_22": ProgramDegreeType.MINOR,
    "filter_172": ProgramDegreeType.ONLINE,
    "filter_170": ProgramDegreeType.OPTION,
    
    # Faculty filters
    "filter_27": Faculty.ARTS,
    "filter_35": Faculty.EDUCATION,
    "filter_30": Faculty.ENGINEERING,
    "filter_29": Faculty.HEALTH_SCIENCES,
    "filter_32": Faculty.LAW,
    "filter_34": Faculty.MANAGEMENT,
    "filter_36": Faculty.MEDICINE,
    "filter_28": Faculty.SCIENCE,
    "filter_31": Faculty.SOCIAL_SCIENCES,
    
    # Sample discipline mappings (expand as needed)
    "filter_62": Discipline.ACCOUNTING,
    "filter_184": Discipline.ADVANCED_MATERIALS_MANUFACTURING,
    "filter_193": Discipline.AFRICAN_STUDIES,
    "filter_46": Discipline.ANTHROPOLOGY,
    "filter_179": Discipline.ART_HISTORY,
    "filter_191": Discipline.ARTIFICIAL_INTELLIGENCE,
    "filter_49": Discipline.AUDIOLOGY,
    "filter_51": Discipline.BIOCHEMISTRY,
    "filter_52": Discipline.BIOINFORMATICS,
    "filter_53": Discipline.BIOLOGY,
    "filter_90": Discipline.BIOMEDICAL_ENGINEERING,
    "filter_136": Discipline.BIOMEDICAL_SCIENCE,
    "filter_137": Discipline.BIOPHARMACEUTICAL_SCIENCE,
    "filter_54": Discipline.BIOPHYSICS,
    "filter_55": Discipline.BIOSTATISTICS,
    "filter_59": Discipline.BUSINESS,
    "filter_195": Discipline.BUSINESS_ANALYTICS,
    "filter_68": Discipline.CANADIAN_LAW,
    "filter_79": Discipline.CANADIAN_STUDIES,
    "filter_80": Discipline.CELTIC_STUDIES,
    "filter_91": Discipline.CHEMICAL_ENGINEERING,
    "filter_57": Discipline.CHEMISTRY,
    "filter_58": Discipline.CINEMA,
    "filter_92": Discipline.CIVIL_ENGINEERING,
    "filter_78": Discipline.CLASSICAL_STUDIES,
    "filter_197": Discipline.CLINICAL_SCIENCE_TRANSLATIONAL_MEDICINE,
    "filter_61": Discipline.COMMUNICATION,
    "filter_94": Discipline.COMPUTER_ENGINEERING,
    "filter_104": Discipline.COMPUTER_SCIENCE,
    "filter_106": Discipline.CONFERENCE_INTERPRETING,
    "filter_81": Discipline.CONFLICT_STUDIES_HUMAN_RIGHTS,
    "filter_140": Discipline.EARTH_SCIENCES,
    "filter_70": Discipline.ECONOMICS,
    "filter_93": Discipline.ELECTRICAL_ENGINEERING,
    "filter_44": Discipline.ENGLISH,
    "filter_45": Discipline.ENGLISH_AS_SECOND_LANGUAGE,
    "filter_72": Discipline.ENTREPRENEURSHIP,
    "filter_73": Discipline.ENVIRONMENT,
    "filter_180": Discipline.ENVIRONMENTAL_ENGINEERING,
    "filter_146": Discipline.ENVIRONMENTAL_SCIENCE,
    "filter_162": Discipline.ENVIRONMENTAL_SUSTAINABILITY,
    "filter_74": Discipline.EPIDEMIOLOGY,
    "filter_77": Discipline.ETHICS,
    "filter_114": Discipline.EXPERIMENTAL_MEDICINE,
    "filter_82": Discipline.FEMINIST_GENDER_STUDIES,
    "filter_85": Discipline.FINANCE,
    "filter_50": Discipline.FINE_ARTS,
    "filter_120": Discipline.FOOD_NUTRITION,
    "filter_86": Discipline.FRENCH,
    "filter_87": Discipline.FRENCH_AS_SECOND_LANGUAGE,
    "filter_88": Discipline.GENETICS,
    "filter_97": Discipline.GEOGRAPHY,
    "filter_98": Discipline.GEOLOGY,
    "filter_99": Discipline.GEOMATICS_SPATIAL_ANALYSIS,
    "filter_108": Discipline.GERMAN,
    "filter_47": Discipline.GREEK_ROMAN_STUDIES,
    "filter_132": Discipline.HEALTH,
    "filter_138": Discipline.HEALTH_SYSTEMS,
    "filter_103": Discipline.HISTORY,
    "filter_38": Discipline.HUMAN_KINETICS,
    "filter_166": Discipline.HUMAN_RESOURCE_MANAGEMENT,
    "filter_173": Discipline.INDIGENOUS_STUDIES,
    "filter_142": Discipline.INFORMATION_STUDIES,
    "filter_42": Discipline.INTERNATIONAL_AFFAIRS,
    "filter_66": Discipline.INTERNATIONAL_DEVELOPMENT,
    "filter_105": Discipline.INTERNATIONAL_ECONOMICS_DEVELOPMENT,
    "filter_83": Discipline.INTERNATIONAL_STUDIES,
    "filter_65": Discipline.ITALIAN,
    "filter_194": Discipline.INTERNATIONAL_AFFAIRS,
    "filter_175": Discipline.JEWISH_CANADIAN_STUDIES,
    "filter_107": Discipline.JOURNALISM,
    "filter_48": Discipline.LATIN_AMERICAN_STUDIES,
    "filter_67": Discipline.LAW,
    "filter_141": Discipline.LIFE_SCIENCES,
    "filter_110": Discipline.LINGUISTICS,
    "filter_37": Discipline.MANAGEMENT,
    "filter_111": Discipline.MARKETING,
    "filter_112": Discipline.MATHEMATICS,
    "filter_96": Discipline.MECHANICAL_ENGINEERING,
    "filter_115": Discipline.MEDIA,
    "filter_113": Discipline.MEDICINE,
    "filter_84": Discipline.MEDIEVAL_RENAISSANCE_STUDIES,
    "filter_116": Discipline.MICROBIOLOGY_IMMUNOLOGY,
    "filter_118": Discipline.MUSIC,
    "filter_119": Discipline.NEUROSCIENCE,
    "filter_149": Discipline.NURSING,
    "filter_75": Discipline.OCCUPATIONAL_THERAPY,
    "filter_121": Discipline.OPHTHALMIC_MEDICAL_TECHNOLOGY,
    "filter_124": Discipline.PHILOSOPHY,
    "filter_126": Discipline.PHYSICS,
    "filter_125": Discipline.PHYSIOTHERAPY,
    "filter_135": Discipline.POLITICAL_SCIENCE,
    "filter_128": Discipline.PSYCHOLOGY,
    "filter_39": Discipline.PUBLIC_ADMINISTRATION,
    "filter_181": Discipline.PUBLIC_HEALTH,
    "filter_127": Discipline.PUBLIC_POLICY,
    "filter_143": Discipline.RELIGIOUS_STUDIES,
    "filter_60": Discipline.RUSSIAN,
    "filter_71": Discipline.SECOND_LANGUAGE_TEACHING,
    "filter_150": Discipline.SOCIAL_IMPACT,
    "filter_151": Discipline.SOCIAL_WORK,
    "filter_152": Discipline.SOCIOLOGY,
    "filter_95": Discipline.SOFTWARE_ENGINEERING,
    "filter_76": Discipline.SPANISH,
    "filter_122": Discipline.SPEECH_LANGUAGE_PATHOLOGY,
    "filter_153": Discipline.STATISTICS,
    "filter_156": Discipline.THEATRE,
    "filter_168": Discipline.VISUAL_ARTS,
    "filter_58": Discipline.WORLD_CINEMAS,
    "filter_129": Discipline.WRITING,
}

class UOttawaProgramsProvider:
    """Provider for UOttawa academic programs data."""
    
    def __init__(self):
        self.programs_url = "https://catalogue.uottawa.ca/en/programs/"
        self._programs_cache: Optional[List[Program]] = None
        self._filter_mappings_cache: Optional[Dict[str, Any]] = None
    
    def _scrape_programs(self) -> List[Program]:
        """Scrape programs data from the UOttawa website."""
        try:
            response = requests.get(self.programs_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            programs = []
            
            # Find all program items
            program_items = soup.find_all("li", class_="item")
            
            for item in program_items:
                try:
                    program = self._parse_program_item(item)
                    if program:
                        programs.append(program)
                except Exception as e:
                    logger.warning(f"Failed to parse program item: {e}")
                    continue
            
            logger.info(f"Scraped {len(programs)} programs from UOttawa")
            return programs
            
        except Exception as e:
            logger.error(f"Failed to scrape programs: {e}")
            raise ProviderError(f"Failed to retrieve programs from UOttawa: {str(e)}")
    
    def _parse_program_item(self, item) -> Optional[Program]:
        """Parse a single program item from HTML."""
        # Extract program name and URL
        link_tag = item.find("a")
        if not link_tag:
            return None
            
        title_span = link_tag.find("span", class_="title")
        if not title_span:
            return None
            
        program_name = title_span.get_text().strip()
        program_url = link_tag.get("href")
        if program_url and not program_url.startswith("http"):
            program_url = f"https://catalogue.uottawa.ca{program_url}"
        
        # Extract filter classes
        class_attr = item.get("class", [])
        filter_classes = [cls for cls in class_attr if cls.startswith("filter_")]
        
        # Map filters to program attributes
        level = ProgramType.UNDERGRADUATE  # Default assumption
        degree_type = ProgramDegreeType.BACHELOR  # Default assumption
        faculty = None
        discipline = None
        
        # Process filters to determine program characteristics
        for filter_class in filter_classes:
            if filter_class in FILTER_MAPPINGS:
                mapped_value = FILTER_MAPPINGS[filter_class]
                
                # Determine which attribute this maps to based on type
                if isinstance(mapped_value, ProgramType):
                    level = mapped_value
                elif isinstance(mapped_value, ProgramDegreeType):
                    degree_type = mapped_value
                elif isinstance(mapped_value, Faculty):
                    faculty = mapped_value
                elif isinstance(mapped_value, Discipline):
                    discipline = mapped_value
        
        return Program(
            name=program_name,
            url=program_url,
            university=University.UOTTAWA,
            level=level,
            degree_type=degree_type,
            faculty=faculty,
            discipline=discipline,
            is_offered=True,
        )
    
    def get_programs(self) -> List[Program]:
        """Get all programs (cached)."""
        if self._programs_cache:
            return self._programs_cache
            
        self._programs_cache = self._scrape_programs()
        return self._programs_cache
    
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