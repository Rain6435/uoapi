#!/usr/bin/env python3
"""
Production Carleton University Course Discovery System

High-performance parallel processing with simple progress tracking
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Optional, Tuple
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('carleton_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionCarletonDiscovery:
    """Production-ready parallel course discovery system"""
    
    def __init__(self, max_workers=6, cookie_file="fresh_cookies.txt"):
        self.max_workers = max_workers
        self.session_template = self._load_cookies(cookie_file)
        self.catalog_data = self._load_catalog()
        
        # URLs
        self.banner_base = "https://central.carleton.ca/prod"
        self.term_select_url = f"{self.banner_base}/bwysched.p_select_term?wsea_code=EXT"
        self.search_fields_url = f"{self.banner_base}/bwysched.p_search_fields"
        self.course_search_url = f"{self.banner_base}/bwysched.p_course_search"
        
        # Progress tracking
        self.total_courses = 0
        self.completed_courses = 0
        self.offered_courses = 0
        self.error_courses = 0
        
        logger.info(f"🚀 Production Discovery initialized with {max_workers} workers")
    
    def _load_cookies(self, cookie_file):
        """Load cookies from file"""
        cookies = {}
        try:
            with open(cookie_file, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, _, _, name, value = parts[:7]
                        if domain == 'central.carleton.ca':
                            cookies[name] = value
            logger.info(f"🍪 Loaded {len(cookies)} cookies")
        except FileNotFoundError:
            logger.warning(f"⚠️  Cookie file {cookie_file} not found")
        
        return {
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            'cookies': cookies
        }
    
    def _load_catalog(self, catalog_file="carleton_courses.json"):
        """Load catalog data"""
        try:
            with open(catalog_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                catalog_data = data.get('subjects', {})
                total_courses = sum(len(courses) for courses in catalog_data.values())
                logger.info(f"📚 Loaded catalog: {len(catalog_data)} subjects, {total_courses} courses")
                return catalog_data
        except FileNotFoundError:
            logger.error(f"❌ Catalog file {catalog_file} not found")
            return {}
    
    def _create_session(self):
        """Create new session with cookies"""
        session = requests.Session()
        session.headers.update(self.session_template['headers'])
        session.cookies.update(self.session_template['cookies'])
        return session
    
    def get_available_terms(self):
        """Get all available terms"""
        session = self._create_session()
        response = session.get(self.term_select_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        form = soup.find('form', action='bwysched.p_search_fields')
        if not form:
            return []
        
        select_element = form.find('select', attrs={'name': 'term_code'})
        if not select_element:
            return []
        
        terms = []
        for option in select_element.find_all('option'):
            term_code = option.get('value', '').strip()
            term_name = option.get_text().strip()
            if term_code and term_name:
                terms.append((term_code, term_name))
        
        logger.info(f"📅 Found {len(terms)} available terms")
        return terms
    
    def get_subjects_for_term(self, term_code):
        """Get available subjects for a specific term"""
        session = self._create_session()
        
        # Get session ID from term selection page
        response = session.get(self.term_select_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        session_input = soup.find('input', {'name': 'session_id'})
        session_id = session_input.get('value') if session_input else ""
        
        # Submit term selection to get subject list
        form_data = {
            'wsea_code': 'EXT',
            'term_code': term_code,
            'session_id': session_id
        }
        
        response = session.post(self.search_fields_url, data=form_data)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract available subjects
        subject_select = soup.find('select', attrs={'name': 'sel_subj'})
        subjects = set()
        if subject_select:
            for option in subject_select.find_all('option'):
                subject_code = option.get('value', '').strip()
                if subject_code and subject_code not in ['dummy', '%']:
                    subjects.add(subject_code)
        
        logger.info(f"🎯 Term {term_code}: {len(subjects)} subjects available")
        return subjects, session_id
    
    def search_single_course(self, args):
        """Search for a single course - thread-safe function"""
        term_code, session_id, subject_code, course_number, course_title, course_credits = args
        
        # Create fresh session for this thread
        session = self._create_session()
        
        # Rate limiting - wait between requests
        time.sleep(0.8)  # 0.8 seconds between requests
        
        try:
            # Prepare Banner search request
            search_data = [
                ('wsea_code', 'EXT'),
                ('term_code', term_code),
                ('session_id', session_id),
                ('ws_numb', ''),
                ('sel_aud', 'dummy'),
                ('sel_subj', 'dummy'),
                ('sel_camp', 'dummy'),
                ('sel_sess', 'dummy'),
                ('sel_attr', 'dummy'),
                ('sel_levl', 'dummy'),
                ('sel_schd', 'dummy'),
                ('sel_insm', 'dummy'),
                ('sel_link', 'dummy'),
                ('sel_wait', 'dummy'),
                ('sel_day', 'dummy'),
                ('sel_begin_hh', 'dummy'),
                ('sel_begin_mi', 'dummy'),
                ('sel_begin_am_pm', 'dummy'),
                ('sel_end_hh', 'dummy'),
                ('sel_end_mi', 'dummy'),
                ('sel_end_am_pm', 'dummy'),
                ('sel_instruct', 'dummy'),
                ('sel_special', 'dummy'),
                ('sel_resd', 'dummy'),
                ('sel_breadth', 'dummy'),
                ('sel_levl', ''),
                ('sel_subj', subject_code),
                ('sel_number', course_number),
                ('sel_crn', ''),
                ('sel_special', 'N'),
                ('sel_sess', ''),
                ('sel_schd', ''),
                ('sel_instruct', ''),
                ('sel_begin_hh', '0'),
                ('sel_begin_mi', '0'),
                ('sel_begin_am_pm', 'a'),
                ('sel_end_hh', '0'),
                ('sel_end_mi', '0'),
                ('sel_end_am_pm', 'a'),
                ('sel_day', 'm'),
                ('sel_day', 't'),
                ('sel_day', 'w'),
                ('sel_day', 'r'),
                ('sel_day', 'f'),
                ('sel_day', 's'),
                ('sel_day', 'u'),
                ('block_button', '')
            ]
            
            # Make the request
            response = session.post(self.course_search_url, data=search_data, timeout=45)
            
            # Parse response
            if "No classes were found" in response.text:
                is_offered = False
                sections_found = 0
                banner_title = ""
                banner_credits = 0.0
            else:
                # Count sections and extract complete details
                soup = BeautifulSoup(response.content, 'html.parser')
                checkboxes = soup.find_all('input', {'type': 'checkbox', 'name': 'select_action'})
                sections_found = len([cb for cb in checkboxes if cb.get('value', '') != 'dummy'])
                is_offered = sections_found > 0
                
                # Extract banner title and credits
                banner_title = ""
                banner_credits = 0.0
                sections_data = []
                
                # Find course title from links
                title_links = soup.find_all('a', href=lambda x: x and 'bwysched.p_display_course' in x)
                for link in title_links:
                    link_text = link.get_text().strip()
                    if not link_text.isdigit() and subject_code not in link_text:
                        banner_title = link_text
                        break
                
                # Parse detailed section information
                if is_offered:
                    # Find the scrollable div with course results
                    results_div = soup.find('div', style=lambda value: value and 'overflow:auto' in value)
                    if results_div:
                        results_table = results_div.find('table')
                        if results_table:
                            rows = results_table.find_all('tr')
                            current_section = None
                            
                            for row in rows:
                                cells = row.find_all('td')
                                if len(cells) >= 11:  # Main section row
                                    # Extract section data
                                    try:
                                        status = cells[1].get_text().strip()
                                        crn_link = cells[2].find('a')
                                        crn = crn_link.get_text().strip() if crn_link else cells[2].get_text().strip()
                                        section = cells[4].get_text().strip()
                                        credits_text = cells[6].get_text().strip()
                                        schedule_type = cells[7].get_text().strip()
                                        instructor = cells[10].get_text().strip()
                                        
                                        # Get credits
                                        try:
                                            credits = float(credits_text) if credits_text and credits_text != '0' else 0.0
                                            if credits > 0 and banner_credits == 0.0:
                                                banner_credits = credits
                                        except ValueError:
                                            credits = 0.0
                                        
                                        current_section = {
                                            'crn': crn,
                                            'section': section,
                                            'status': status,
                                            'credits': credits,
                                            'schedule_type': schedule_type,
                                            'instructor': instructor,
                                            'meeting_times': [],
                                            'notes': []
                                        }
                                        sections_data.append(current_section)
                                        
                                    except (IndexError, AttributeError):
                                        continue
                                        
                                elif len(cells) > 0 and current_section:
                                    # This might be a meeting time or note row
                                    row_text = row.get_text().strip()
                                    if 'Meeting Date:' in row_text:
                                        # Parse meeting time
                                        import re
                                        date_match = re.search(r'Meeting Date:\s*(\w+ \d+, \d+)\s*to\s*(\w+ \d+, \d+)', row_text)
                                        days_match = re.search(r'Days:\s*([^T]+?)(?=Time:|$)', row_text)
                                        time_match = re.search(r'Time:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', row_text)
                                        
                                        if date_match and days_match and time_match:
                                            meeting_info = {
                                                'start_date': date_match.group(1).strip(),
                                                'end_date': date_match.group(2).strip(),
                                                'days': days_match.group(1).strip(),
                                                'start_time': time_match.group(1),
                                                'end_time': time_match.group(2)
                                            }
                                            current_section['meeting_times'].append(meeting_info)
                                    elif 'Also Register in:' in row_text or 'Section Information:' in row_text:
                                        current_section['notes'].append(row_text.strip())
            
            # Update progress
            self.completed_courses += 1
            if is_offered:
                self.offered_courses += 1
            
            # Simple progress indicator
            if self.completed_courses % 10 == 0:
                progress_pct = (self.completed_courses / max(1, self.total_courses)) * 100
                print(f"⏳ Progress: {self.completed_courses}/{self.total_courses} ({progress_pct:.1f}%) | {self.offered_courses} offered")
            
            return {
                'course_code': f"{subject_code} {course_number}",
                'subject_code': subject_code,
                'course_number': course_number,
                'catalog_title': course_title,
                'catalog_credits': course_credits,
                'is_offered': is_offered,
                'sections_found': sections_found,
                'banner_title': banner_title,
                'banner_credits': banner_credits,
                'sections': sections_data,
                'error': False,
                'error_message': ''
            }
            
        except Exception as e:
            self.error_courses += 1
            logger.error(f"❌ Error searching {subject_code} {course_number}: {str(e)}")
            
            return {
                'course_code': f"{subject_code} {course_number}",
                'subject_code': subject_code,
                'course_number': course_number,
                'catalog_title': course_title,
                'catalog_credits': course_credits,
                'is_offered': False,
                'sections_found': 0,
                'banner_title': '',
                'banner_credits': 0.0,
                'sections': [],
                'error': True,
                'error_message': str(e)
            }
    
    def discover_term(self, term_code, term_name, max_courses_per_subject=None):
        """Discover all courses for a specific term"""
        logger.info(f"🔍 Starting discovery for {term_name}")
        
        # Get subjects and session for this term
        subjects, session_id = self.get_subjects_for_term(term_code)
        
        if not subjects or not session_id:
            return {"error": "Failed to get subjects or session ID"}
        
        # Prepare course list from catalog
        course_args = []
        subject_stats = {}
        
        for subject_code in sorted(subjects):
            subject_courses = self.catalog_data.get(subject_code, [])
            if not subject_courses:
                continue
            
            # Limit courses per subject if specified
            if max_courses_per_subject:
                subject_courses = subject_courses[:max_courses_per_subject]
            
            subject_stats[subject_code] = {
                'total_in_catalog': len(self.catalog_data.get(subject_code, [])),
                'tested': len(subject_courses),
                'offered': 0
            }
            
            for course in subject_courses:
                course_code = course.get('code', '').replace(' ', '')
                if course_code.startswith(subject_code):
                    course_number = course_code.replace(subject_code, '').strip()
                    course_title = course.get('title', '')
                    course_credits = course.get('credits', 0.0)
                    
                    course_args.append((term_code, session_id, subject_code, course_number, course_title, course_credits))
        
        self.total_courses = len(course_args)
        self.completed_courses = 0
        self.offered_courses = 0
        self.error_courses = 0
        
        logger.info(f"🎯 Processing {self.total_courses} courses from {len(subject_stats)} subjects with {self.max_workers} workers")
        
        # Process courses in parallel
        all_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_course = {executor.submit(self.search_single_course, args): args for args in course_args}
            
            # Collect results as they complete
            for future in as_completed(future_to_course):
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    # Update subject stats
                    subject_code = result['subject_code']
                    if result['is_offered'] and subject_code in subject_stats:
                        subject_stats[subject_code]['offered'] += 1
                        
                except Exception as e:
                    args = future_to_course[future]
                    logger.error(f"❌ Future error for {args[2]} {args[3]}: {e}")
        
        # Calculate final statistics
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ Discovery complete for {term_name}")
        logger.info(f"⏱️  Time: {elapsed_time:.1f} seconds")
        logger.info(f"📊 Results: {self.offered_courses}/{self.total_courses} courses offered ({(self.offered_courses/max(1,self.total_courses)*100):.1f}%)")
        logger.info(f"❌ Errors: {self.error_courses}")
        
        # Print top subjects with offerings
        top_subjects = sorted([(s, stats['offered']) for s, stats in subject_stats.items()], key=lambda x: x[1], reverse=True)[:10]
        if top_subjects:
            logger.info(f"🔥 Top subjects: {', '.join([f'{s}({n})' for s, n in top_subjects if n > 0])}")
        
        return {
            'term_code': term_code,
            'term_name': term_name,
            'session_id': session_id,
            'total_subjects_available': len(subjects),
            'subjects_tested': len(subject_stats),
            'total_courses_tested': self.total_courses,
            'courses_offered': self.offered_courses,
            'errors': self.error_courses,
            'processing_time_seconds': elapsed_time,
            'offering_rate_percent': (self.offered_courses/max(1,self.total_courses)*100),
            'subject_statistics': subject_stats,
            'courses': all_results,
            'processed_at': datetime.now().isoformat()
        }
    
    def discover_all_terms(self, max_courses_per_subject=None):
        """Discover courses for all available terms"""
        logger.info("🌟 Starting comprehensive multi-term discovery")
        
        # Get all available terms
        terms = self.get_available_terms()
        if not terms:
            return {"error": "No terms found"}
        
        all_results = {}
        summary_stats = {
            'total_terms': len(terms),
            'successful_terms': 0,
            'failed_terms': 0,
            'total_courses_tested': 0,
            'total_courses_offered': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Process each term
        for i, (term_code, term_name) in enumerate(terms, 1):
            logger.info(f"📆 Processing term {i}/{len(terms)}: {term_name}")
            
            try:
                term_results = self.discover_term(term_code, term_name, max_courses_per_subject)
                
                if "error" in term_results:
                    logger.error(f"❌ Failed to process {term_name}: {term_results['error']}")
                    summary_stats['failed_terms'] += 1
                else:
                    all_results[term_code] = term_results
                    summary_stats['successful_terms'] += 1
                    summary_stats['total_courses_tested'] += term_results.get('total_courses_tested', 0)
                    summary_stats['total_courses_offered'] += term_results.get('courses_offered', 0)
                
                # Save individual term results
                term_filename = f"carleton_term_{term_code}_{term_name.replace(' ', '_').replace('(', '').replace(')', '')}.json"
                with open(term_filename, 'w', encoding='utf-8') as f:
                    json.dump(term_results, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Saved {term_filename}")
                
                # Brief pause between terms
                if i < len(terms):
                    logger.info("⏸️  Pausing 30 seconds between terms...")
                    time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Exception processing {term_name}: {e}")
                summary_stats['failed_terms'] += 1
        
        # Final summary
        summary_stats['end_time'] = datetime.now().isoformat()
        summary_stats['overall_offering_rate'] = (summary_stats['total_courses_offered'] / max(1, summary_stats['total_courses_tested']) * 100)
        
        comprehensive_results = {
            'summary': summary_stats,
            'configuration': {
                'max_workers': self.max_workers,
                'max_courses_per_subject': max_courses_per_subject
            },
            'terms': all_results
        }
        
        logger.info("🎉 Multi-term discovery complete!")
        logger.info(f"📊 Final Stats: {summary_stats['total_courses_offered']}/{summary_stats['total_courses_tested']} courses offered ({summary_stats['overall_offering_rate']:.1f}%)")
        
        return comprehensive_results


def main():
    """Main execution function"""
    print("🎯 Carleton University Production Discovery System")
    print("=" * 60)
    
    # Configuration
    config = {
        'max_workers': 6,  # Balanced performance
        'max_courses_per_subject': 10  # Reasonable limit for full discovery
    }
    
    logger.info(f"🔧 Configuration: {config}")
    
    # Create discovery system
    discovery = ProductionCarletonDiscovery(max_workers=config['max_workers'])
    
    # Run comprehensive discovery
    results = discovery.discover_all_terms(max_courses_per_subject=config['max_courses_per_subject'])
    
    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_filename = f"carleton_comprehensive_discovery_{timestamp}.json"
    
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Comprehensive results saved to {summary_filename}")
    print(f"\n🎉 Discovery complete! Check {summary_filename} for full results.")


if __name__ == "__main__":
    main()