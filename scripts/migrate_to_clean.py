#!/usr/bin/env python3
"""
ARGO Migration Script: v9.0 F1 → v9.0 Clean
Migrates from old architecture to unified clean architecture
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json
import sqlite3


class ARGOMigration:
    """Handles migration from F1 to Clean architecture"""
    
    def __init__(self, source_path: Path, target_path: Path):
        self.source = source_path
        self.target = target_path
        self.backup_path = None
        self.migration_log = []
    
    def migrate(self, backup=True):
        """Execute full migration"""
        print("=" * 70)
        print("ARGO Migration: v9.0 F1 → v9.0 Clean")
        print("=" * 70)
        
        # Step 1: Backup
        if backup:
            print("\n[1/7] Creating backup...")
            self.create_backup()
        
        # Step 2: Migrate data
        print("\n[2/7] Migrating database...")
        self.migrate_database()
        
        # Step 3: Migrate projects
        print("\n[3/7] Migrating projects...")
        self.migrate_projects()
        
        # Step 4: Migrate library
        print("\n[4/7] Migrating library...")
        self.migrate_library()
        
        # Step 5: Migrate configuration
        print("\n[5/7] Migrating configuration...")
        self.migrate_config()
        
        # Step 6: Copy credentials
        print("\n[6/7] Copying credentials...")
        self.copy_credentials()
        
        # Step 7: Generate migration report
        print("\n[7/7] Generating migration report...")
        self.generate_report()
        
        print("\n" + "=" * 70)
        print("Migration completed successfully!")
        print(f"Backup location: {self.backup_path}")
        print("=" * 70)
    
    def create_backup(self):
        """Create full backup of source"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.source.parent / f"ARGO_backup_{timestamp}"
        
        print(f"Backing up to: {self.backup_path}")
        shutil.copytree(self.source, self.backup_path)
        
        self.migration_log.append({
            'step': 'backup',
            'status': 'success',
            'path': str(self.backup_path)
        })
    
    def migrate_database(self):
        """Migrate database from old to unified schema"""
        # Source databases
        old_master_db = self.source / "data" / "projects.db"
        old_unified_db = self.source / "data" / "argo_unified.db"
        
        # Target database
        new_unified_db = self.target / "data" / "argo_unified.db"
        new_unified_db.parent.mkdir(parents=True, exist_ok=True)
        
        if old_unified_db.exists():
            # Copy unified DB directly
            print(f"Copying unified database...")
            shutil.copy2(old_unified_db, new_unified_db)
            
            self.migration_log.append({
                'step': 'database',
                'status': 'success',
                'source': str(old_unified_db),
                'target': str(new_unified_db)
            })
        elif old_master_db.exists():
            # Need to convert old master DB to unified schema
            print(f"Converting master database to unified schema...")
            self._convert_master_to_unified(old_master_db, new_unified_db)
            
            self.migration_log.append({
                'step': 'database',
                'status': 'converted',
                'source': str(old_master_db),
                'target': str(new_unified_db)
            })
        else:
            print("No database found, will create new")
            self.migration_log.append({
                'step': 'database',
                'status': 'new_db'
            })
    
    def _convert_master_to_unified(self, old_db: Path, new_db: Path):
        """Convert old master DB to unified schema"""
        # This is a simplified conversion
        # Real implementation would need to carefully migrate all tables
        
        # For now, just copy and let UnifiedDatabase handle schema update
        shutil.copy2(old_db, new_db)
    
    def migrate_projects(self):
        """Migrate project data"""
        old_projects = self.source / "data" / "projects"
        new_projects = self.target / "data" / "projects"
        
        if not old_projects.exists():
            print("No projects to migrate")
            return
        
        new_projects.mkdir(parents=True, exist_ok=True)
        
        for project_dir in old_projects.iterdir():
            if project_dir.is_dir():
                print(f"Migrating project: {project_dir.name}")
                
                target_project = new_projects / project_dir.name
                shutil.copytree(project_dir, target_project, dirs_exist_ok=True)
                
                self.migration_log.append({
                    'step': 'project_migration',
                    'project': project_dir.name,
                    'status': 'success'
                })
    
    def migrate_library(self):
        """Migrate library files"""
        old_library = self.source / "data" / "library"
        new_library = self.target / "data" / "library_cache"
        
        if not old_library.exists():
            print("No library to migrate")
            return
        
        print(f"Migrating library...")
        shutil.copytree(old_library, new_library, dirs_exist_ok=True)
        
        self.migration_log.append({
            'step': 'library',
            'status': 'success',
            'source': str(old_library),
            'target': str(new_library)
        })
    
    def migrate_config(self):
        """Migrate configuration"""
        # Copy .env
        old_env = self.source / ".env"
        new_env = self.target / ".env"
        
        if old_env.exists():
            print("Copying .env file...")
            shutil.copy2(old_env, new_env)
        else:
            print("Warning: No .env file found. Create one manually.")
        
        # Note: settings.yaml is new, no migration needed
        print("Note: settings.yaml is part of clean architecture (already in place)")
        
        self.migration_log.append({
            'step': 'config',
            'status': 'success' if old_env.exists() else 'manual_required'
        })
    
    def copy_credentials(self):
        """Copy Google credentials"""
        old_creds = self.source / "google_credentials.json"
        new_creds = self.target / "google_credentials.json"
        
        if old_creds.exists():
            print("Copying Google credentials...")
            shutil.copy2(old_creds, new_creds)
            
            self.migration_log.append({
                'step': 'credentials',
                'status': 'success'
            })
        else:
            print("No Google credentials found (optional)")
            self.migration_log.append({
                'step': 'credentials',
                'status': 'not_found'
            })
    
    def generate_report(self):
        """Generate migration report"""
        report = {
            'migration_date': datetime.now().isoformat(),
            'source': str(self.source),
            'target': str(self.target),
            'backup': str(self.backup_path) if self.backup_path else None,
            'log': self.migration_log,
            'status': 'completed'
        }
        
        report_file = self.target / "MIGRATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Migration report saved to: {report_file}")


def main():
    """Main migration execution"""
    if len(sys.argv) < 3:
        print("Usage: python migrate_to_clean.py <source_path> <target_path>")
        print("\nExample:")
        print("  python migrate_to_clean.py ../ARGO_v9.0 ../ARGO_v9.0_CLEAN")
        sys.exit(1)
    
    source = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve()
    
    if not source.exists():
        print(f"Error: Source path does not exist: {source}")
        sys.exit(1)
    
    print(f"Source: {source}")
    print(f"Target: {target}")
    print("\nProceed with migration? (yes/no): ", end='')
    
    response = input().strip().lower()
    if response not in ['yes', 'y']:
        print("Migration cancelled")
        sys.exit(0)
    
    migrator = ARGOMigration(source, target)
    
    try:
        migrator.migrate(backup=True)
    except Exception as e:
        print(f"\nError during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
