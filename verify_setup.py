#!/usr/bin/env python
"""
Construction AI Landing Page - Setup Verification Script

This script verifies that all dependencies are installed and configured correctly.
Run this after installing requirements.txt to ensure everything is set up properly.

Usage:
    python verify_setup.py
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python 3.9+ required (you have {version.major}.{version.minor})")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print_header("Dependency Check")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'email_validator': 'Email Validator',
    }
    
    all_installed = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{name} is installed")
        except ImportError:
            print_error(f"{name} is NOT installed")
            all_installed = False
    
    return all_installed


def check_env_file():
    """Check if .env file exists."""
    print_header("Environment Configuration Check")
    
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if env_path.exists():
        print_success(".env file exists")
        
        # Check for required variables
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        required_vars = [
            'DATABASE_URL',
            'DEBUG',
            'SECRET_KEY',
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_content or f'{var}=' not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print_warning(f"Missing or empty variables: {', '.join(missing_vars)}")
            return False
        else:
            print_success("All required variables are configured")
            return True
    else:
        print_error(".env file does NOT exist")
        
        if env_example_path.exists():
            print_info("Creating .env from .env.example...")
            try:
                with open(env_example_path, 'r') as f:
                    content = f.read()
                with open(env_path, 'w') as f:
                    f.write(content)
                print_success(".env file created from .env.example")
                print_warning("Please edit .env with your configuration")
                return False
            except Exception as e:
                print_error(f"Failed to create .env: {str(e)}")
                return False
        else:
            print_error(".env.example file does NOT exist")
            return False


def check_project_structure():
    """Check if all required directories and files exist."""
    print_header("Project Structure Check")
    
    required_paths = {
        'app': 'Application directory',
        'app/routes': 'Routes directory',
        'app/models': 'Models directory',
        'app/schemas': 'Schemas directory',
        'app/utils': 'Utils directory',
        'app/templates': 'Templates directory',
        'app/static': 'Static files directory',
        'app/main.py': 'Main application file',
        'app/config.py': 'Configuration file',
        'app/database.py': 'Database file',
        'requirements.txt': 'Requirements file',
    }
    
    all_exist = True
    
    for path, description in required_paths.items():
        if Path(path).exists():
            print_success(f"{description} exists")
        else:
            print_error(f"{description} does NOT exist: {path}")
            all_exist = False
    
    return all_exist


def check_database():
    """Check if database can be initialized."""
    print_header("Database Check")
    
    try:
        from app.database import init_db
        
        print_info("Attempting to initialize database...")
        init_db()
        print_success("Database initialized successfully")
        
        # Check if database file exists
        if Path('contractors.db').exists():
            print_success("Database file created: contractors.db")
            return True
        else:
            print_warning("Database file not created (may be using different database)")
            return True
            
    except Exception as e:
        print_error(f"Database initialization failed: {str(e)}")
        return False


def check_imports():
    """Check if all application modules can be imported."""
    print_header("Import Check")
    
    modules_to_check = [
        ('app.config', 'Configuration'),
        ('app.database', 'Database'),
        ('app.models.contractor', 'Contractor Model'),
        ('app.schemas.contractor', 'Contractor Schema'),
        ('app.routes.forms', 'Forms Routes'),
        ('app.routes.roi', 'ROI Routes'),
        ('app.routes.booking', 'Booking Routes'),
        ('app.utils.email', 'Email Utils'),
        ('app.main', 'Main Application'),
    ]
    
    all_imported = True
    
    for module_name, description in modules_to_check:
        try:
            __import__(module_name)
            print_success(f"{description} imported successfully")
        except Exception as e:
            print_error(f"{description} import failed: {str(e)}")
            all_imported = False
    
    return all_imported


def check_fastapi_app():
    """Check if FastAPI app can be created."""
    print_header("FastAPI Application Check")
    
    try:
        from app.main import app
        
        print_success("FastAPI application created successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print_info(f"Total routes registered: {len(routes)}")
        
        expected_routes = [
            '/api/forms/contact',
            '/api/roi/calculate',
            '/api/booking/schedule-demo',
            '/api/booking/available-slots',
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print_success(f"Route {route} is registered")
            else:
                print_warning(f"Route {route} not found")
        
        return True
        
    except Exception as e:
        print_error(f"FastAPI application creation failed: {str(e)}")
        return False


def run_all_checks():
    """Run all verification checks."""
    print(f"\n{BOLD}{BLUE}Construction AI Landing Page - Setup Verification{RESET}\n")
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Environment Configuration': check_env_file(),
        'Project Structure': check_project_structure(),
        'Imports': check_imports(),
        'Database': check_database(),
        'FastAPI Application': check_fastapi_app(),
    }
    
    # Print summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{check_name}: {status}")
    
    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print_success("All checks passed! Your setup is ready.")
        print_info("Next steps:")
        print_info("1. Start the development server: uvicorn app.main:app --reload")
        print_info("2. Visit http://localhost:8000 in your browser")
        print_info("3. View API docs at http://localhost:8000/api/docs")
        return 0
    else:
        print_error(f"Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_checks())
