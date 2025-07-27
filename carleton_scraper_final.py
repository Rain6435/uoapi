#!/usr/bin/env python3
"""
Carleton University Course Catalog Scraper - Final Version

This script scrapes all course information from Carleton University's
course catalog and saves it to a JSON file.
"""

import requests
import json
import re
import time
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, List, Optional
from urllib.parse import urljoin


class CarletonCourseScraper:
    def __init__(self):
        self.base_url = "https://calendar.carleton.ca"
        self.courses_url = f"{self.base_url}/undergrad/courses/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_subject_codes(self) -> List[str]:
        """Extract all subject codes from the main courses page."""
        print("Fetching subject codes...")
        
        response = self.session.get(self.courses_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to subject pages - they are relative links like "COMP/", "MATH/"
        subject_links = soup.find_all('a', href=re.compile(r'^[A-Z]{3,4}/$'))
        
        subject_codes = []
        for link in subject_links:
            # Extract subject code from href (remove trailing slash)
            subject_code = link['href'].rstrip('/')
            subject_codes.append(subject_code)
        
        # Remove duplicates and sort
        subject_codes = sorted(list(set(subject_codes)))
        print(f"Found {len(subject_codes)} subject codes")
        
        return subject_codes

    def parse_prerequisites(self, prereq_text: str) -> List[str]:
        """Extract course codes from prerequisite text."""
        if not prereq_text:
            return []
        
        # Find all course codes in format like "AERO 2001", "MATH 1104"
        course_pattern = r'[A-Z]{3,4}\s+\d{4}'
        courses = re.findall(course_pattern, prereq_text)
        
        return list(set(courses))  # Remove duplicates

    def parse_course_block(self, course_block) -> Optional[Dict]:
        """Parse a single course block and extract all relevant information."""
        try:
            # Extract course code
            code_span = course_block.find('span', class_='courseblockcode')
            if not code_span:
                return None
            
            course_code = code_span.get_text().strip().replace('\xa0', ' ')
            
            # Extract title span
            title_span = course_block.find('span', class_='courseblocktitle')
            if not title_span:
                return None
            
            # Extract credits
            title_text = title_span.get_text()
            credit_match = re.search(r'\[([0-9.]+)\s+credit[s]?\]', title_text)
            credits = float(credit_match.group(1)) if credit_match else None
            
            # Extract course title - everything after the credit information
            # Split by newlines and take the last non-empty part
            lines = title_text.split('\n')
            course_title = ""
            for line in reversed(lines):
                line = line.strip()
                if line and not re.search(r'[A-Z]{3,4}\s+\d{4}', line) and '[credit' not in line:
                    course_title = line
                    break
            
            # Extract description - get text from course block, excluding title and additional info
            full_text = course_block.get_text()
            
            # Remove the title part
            desc_start = full_text.find(course_title)
            if desc_start != -1:
                remaining_text = full_text[desc_start + len(course_title):].strip()
                
                # Find where additional info starts
                additional_markers = [
                    'Includes:', 'Prerequisite(s):', 'Corequisite(s):', 
                    'Precludes additional credit', 'Also listed as',
                    'Lectures', 'Tutorial', 'Laboratory', 'Seminar'
                ]
                
                description = remaining_text
                for marker in additional_markers:
                    marker_pos = remaining_text.find(marker)
                    if marker_pos != -1:
                        description = remaining_text[:marker_pos].strip()
                        break
            else:
                description = ""
            
            # Extract additional course details
            additional_div = course_block.find('div', class_='coursedescadditional')
            additional_info = {
                'experiential_learning': False,
                'prerequisites': [],
                'corequisites': [],
                'preclusions': [],
                'cross_listed': [],
                'schedule': "",
            }
            
            if additional_div:
                additional_text = additional_div.get_text()
                
                # Check for experiential learning
                if 'Experiential Learning Activity' in additional_text:
                    additional_info['experiential_learning'] = True
                
                # Extract prerequisites
                prereq_match = re.search(r'Prerequisite\(s\):\s*([^.]+?)(?:\.|$)', additional_text, re.DOTALL)
                if prereq_match:
                    prereq_text = prereq_match.group(1)
                    additional_info['prerequisites'] = self.parse_prerequisites(prereq_text)
                
                # Extract corequisites
                coreq_match = re.search(r'Corequisite\(s\):\s*([^.]+?)(?:\.|$)', additional_text, re.DOTALL)
                if coreq_match:
                    coreq_text = coreq_match.group(1)
                    additional_info['corequisites'] = self.parse_prerequisites(coreq_text)
                
                # Extract preclusions
                preclusion_match = re.search(r'Precludes additional credit for\s*([^.]+?)(?:\.|$)', additional_text, re.DOTALL)
                if preclusion_match:
                    preclusion_text = preclusion_match.group(1)
                    additional_info['preclusions'] = self.parse_prerequisites(preclusion_text)
                
                # Extract cross-listed courses
                cross_listed_match = re.search(r'Also listed as\s*([^.]+?)(?:\.|$)', additional_text, re.DOTALL)
                if cross_listed_match:
                    cross_listed_text = cross_listed_match.group(1)
                    additional_info['cross_listed'] = self.parse_prerequisites(cross_listed_text)
                
                # Extract schedule information
                schedule_matches = re.findall(r'(Lectures?[^.]*|Tutorial[s]?[^.]*|Laboratory[^.]*|Seminar[s]?[^.]*|Workshop[s]?[^.]*)', additional_text, re.IGNORECASE)
                if schedule_matches:
                    additional_info['schedule'] = '; '.join(schedule_matches)
            
            course_data = {
                'code': course_code,
                'title': course_title,
                'credits': credits,
                'description': description,
                **additional_info
            }
            
            return course_data
            
        except Exception as e:
            print(f"Error parsing course block for {course_code if 'course_code' in locals() else 'unknown'}: {e}")
            return None

    def scrape_subject(self, subject_code: str) -> List[Dict]:
        """Scrape all courses for a given subject."""
        print(f"Scraping {subject_code}...")
        
        subject_url = f"{self.courses_url}{subject_code}/"
        
        try:
            response = self.session.get(subject_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all course blocks
            course_blocks = soup.find_all('div', class_='courseblock')
            
            courses = []
            for block in course_blocks:
                course_data = self.parse_course_block(block)
                if course_data:
                    courses.append(course_data)
            
            print(f"  Found {len(courses)} courses in {subject_code}")
            return courses
            
        except Exception as e:
            print(f"Error scraping {subject_code}: {e}")
            return []

    def scrape_all_courses(self) -> Dict:
        """Scrape all courses from all subjects."""
        subject_codes = self.get_subject_codes()
        
        all_courses = {}
        
        for i, subject_code in enumerate(subject_codes, 1):
            print(f"Progress: {i}/{len(subject_codes)}")
            
            courses = self.scrape_subject(subject_code)
            if courses:
                all_courses[subject_code] = courses
            
            # Be nice to the server
            time.sleep(1)
        
        return all_courses

    def save_to_json(self, data: Dict, filename: str = "carleton_courses.json"):
        """Save course data to JSON file."""
        print(f"Saving data to {filename}...")
        
        # Add metadata
        output_data = {
            'metadata': {
                'university': 'Carleton University',
                'source_url': self.courses_url,
                'total_subjects': len(data),
                'total_courses': sum(len(courses) for courses in data.values()),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'subjects': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {output_data['metadata']['total_courses']} courses from {output_data['metadata']['total_subjects']} subjects")

    def run(self):
        """Main execution method."""
        try:
            print("Starting Carleton University course scraper...")
            
            all_courses = self.scrape_all_courses()
            self.save_to_json(all_courses)
            
            print("Scraping completed successfully!")
            
        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
        except Exception as e:
            print(f"Error during scraping: {e}")


if __name__ == "__main__":
    scraper = CarletonCourseScraper()
    scraper.run()