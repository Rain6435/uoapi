#!/usr/bin/env python3
"""
Simple, working CLI for Schedulo API testing.
"""

import argparse
import sys


def cmd_test_comp1005(args):
    """Test COMP 1005 enhanced section parsing."""
    print("Testing COMP 1005 enhanced section parsing...")
    
    try:
        from uoapi.universities.carleton.provider import CarletonProvider
        
        provider = CarletonProvider()
        result = provider.discover_courses('202530', subjects=['COMP'], course_codes=['COMP1005'], max_courses_per_subject=10)
        
        if result.courses:
            course = result.courses[0]
            print(f"\nCourse: {course.course_code} - {course.title}")
            print(f"Total sections: {len(course.sections)}")
            
            lectures = [s for s in course.sections if 'lecture' in s.schedule_type.lower()]
            tutorials = [s for s in course.sections if 'tutorial' in s.schedule_type.lower()]
            
            print(f"Lectures: {len(lectures)}")
            for section in lectures:
                print(f"  {section.section} - CRN {section.crn} - {section.status}")
                
            print(f"Tutorials: {len(tutorials)}")  
            for section in tutorials:
                print(f"  {section.section} - CRN {section.crn} - {section.status}")
        else:
            print("COMP 1005 not found")
            
    except Exception as e:
        print(f"Error: {e}")


def cmd_server(args):
    """Start API server."""
    try:
        import uvicorn
        from uoapi.server.app import create_app
        
        app = create_app()
        print(f"Starting server on port {args.port}...")
        print(f"Docs: http://127.0.0.1:{args.port}/docs")
        
        uvicorn.run(app, host="127.0.0.1", port=args.port)
    except Exception as e:
        print(f"Error starting server: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(prog='schedulo-simple')
    subparsers = parser.add_subparsers(dest='command')
    
    # test-comp1005 command
    test_parser = subparsers.add_parser('test-comp1005', help='Test enhanced COMP 1005 parsing')
    test_parser.set_defaults(func=cmd_test_comp1005)
    
    # server command  
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
        print("\nCancelled")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())