#!/usr/bin/env python
"""
Autonomous Landing Page Generation Script

This script automatically runs the landing page generation flow with configurable
environment variables for Figma integration, output directories, and product increment settings.

Usage:
    python execute_landing_page.py
"""
import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime

# Configure project paths
PROJECT_ROOT = Path(__file__).parent
CREWAI_SWE_DIR = PROJECT_ROOT / "crewai" / "swe"
SRC_DIR = CREWAI_SWE_DIR / "src"

# Add the necessary directories to Python path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CREWAI_SWE_DIR))
sys.path.insert(0, str(SRC_DIR))

# Import the LandingPageFlow after path adjustment
from src.swe.landing_page_flow import LandingPageFlow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("swe-landing-page-executor")

def copy_template_files():
    """Copy template files from source templates to the output directory structure
    and normalize the directory structure for consistency.
    """
    # Define paths
    project_root = Path(__file__).parent
    base_dir = project_root / "projects" / "swe" / "landing-page"
    
    # Standardize on a single template directory structure
    template_dir = base_dir / "templates"
    landing_page_dir = base_dir / "landing-page"
    
    # Create required directories
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(landing_page_dir / "css", exist_ok=True)
    os.makedirs(landing_page_dir / "js", exist_ok=True)
    os.makedirs(landing_page_dir / "images", exist_ok=True)
    
    # Copy from any potential source locations
    potential_sources = [
        base_dir / "templates" / "landing_page",  # old underscore format
        project_root / "crewai" / "swe" / "src" / "swe" / "templates" / "landing_page"
    ]
    
    template_files = [
        ('base.html', template_dir / 'index.html'),
        ('styles.css', template_dir / 'styles.css'),
        ('main.js', template_dir / 'main.js')
    ]
    
    # Try to copy from potential sources
    any_copied = False
    for source_dir in potential_sources:
        if source_dir.exists():
            logger.info(f"Found template source directory: {source_dir}")
            try:
                for src_name, dest_path in template_files:
                    src_path = source_dir / src_name
                    if src_path.exists():
                        shutil.copy2(src_path, dest_path)
                        any_copied = True
                        logger.info(f"Copied template file {src_name} to {dest_path}")
                
                # Also copy any images if they exist
                img_source = source_dir / "images"
                if img_source.exists():
                    for img_file in img_source.glob("*.*"):
                        img_dest = template_dir / "images" / img_file.name
                        os.makedirs(template_dir / "images", exist_ok=True)
                        shutil.copy2(img_file, img_dest)
                        logger.info(f"Copied image file {img_file.name} to {img_dest}")
            except Exception as e:
                logger.error(f"Error copying from {source_dir}: {e}")
    
    if not any_copied:
        logger.warning("No template files were found to copy. Using fallbacks if available.")
    
    # Clean up unused directories
    cleanup_directories = [
        base_dir / "css",
        base_dir / "js",
        base_dir / "templates" / "landing_page"  # old underscore format
    ]
    
    for dir_path in cleanup_directories:
        if dir_path.exists():
            try:
                # Copy any content to the new structure first
                if dir_path.name == "css":
                    for file in dir_path.glob("*.*"):
                        shutil.copy2(file, template_dir / file.name)
                        logger.info(f"Migrated {file} to {template_dir}")
                elif dir_path.name == "js":
                    for file in dir_path.glob("*.*"):
                        shutil.copy2(file, template_dir / file.name)
                        logger.info(f"Migrated {file} to {template_dir}")
                elif dir_path.name == "landing_page":
                    # Already handled in the copy step above
                    pass
                
                # Don't actually delete directories yet to prevent data loss
                # We'll just log that they should be removed
                logger.info(f"Directory {dir_path} is now redundant and could be removed")
            except Exception as e:
                logger.error(f"Error cleaning up directory {dir_path}: {e}")

def main():
    """Run the landing page generation pipeline with environment settings"""
    # Environment configuration with defaults
    figma_file_url = os.getenv("FIGMA_FILE_URL", 
                              "https://www.figma.com/design/4geYG6mUwUdpcHZsfEHaY9/High-fidelity?node-id=1001-61&t=UXzO0BtZ1791xzJi-1")
    
    figma_api_key = os.getenv("FIGMA_API_KEY", 
                             "figd_s0eMNQRon-ZxFhYswaqQ1joLDxqeDK7e8h4gLZ9O")
    
    # Set up the correct output directory path
    projects_dir = PROJECT_ROOT / "projects" / "swe"
    output_dir = str(projects_dir)
    # Create projects directory if it doesn't exist
    os.makedirs(projects_dir, exist_ok=True)
    
    # Create template directories
    template_dir = projects_dir / "landing-page" / "templates" / "landing_page"
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(template_dir / "images", exist_ok=True)
    
    # Ensure our default templates are in place
    copy_template_files()
    
    capability = os.getenv("SWE_CAPABILITY", "landing-page")
    product_increment = os.getenv("SWE_PRODUCT_INCREMENT", "alpha")
    
    # Override environment variables
    os.environ["FIGMA_FILE_URL"] = figma_file_url
    os.environ["FIGMA_API_KEY"] = figma_api_key
    os.environ["SWE_OUTPUT_DIR"] = output_dir
    
    # Log configuration
    logger.info(f"Starting landing page generation with:")
    logger.info(f"  - Output directory: {output_dir}")
    logger.info(f"  - Template directory: {template_dir}")
    logger.info(f"  - Capability: {capability}")
    logger.info(f"  - Product increment: {product_increment}")
    logger.info(f"  - Figma URL: {figma_file_url}")
    logger.info(f"  - Figma integration: {'Enabled' if figma_api_key else 'Disabled'}")
    
    # Initialize the flow
    flow = LandingPageFlow(product_increment=product_increment)
    
    # Run the full generation process
    try:
        logger.info("Starting PDCA Cycle 5...")
        result = flow.run_full_generation()
        logger.info(f"Landing page generation complete. Results: {result}")
        logger.info(f"Files generated at: {output_dir}")
        logger.info(f"PDCA Cycle 5 complete. Analyzing results...")
    except Exception as e:
        logger.error(f"Error in landing page generation: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
