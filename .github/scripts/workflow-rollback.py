#!/usr/bin/env python3
"""
Workflow Rollback System

Provides automated rollback capabilities for GitHub Actions workflows
when issues are detected after deployment.

Requirements addressed:
- 10.5: Create workflow rollback procedures for issues
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml


class WorkflowRollbackManager:
    """Manages workflow rollback operations."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the rollback manager.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.backup_dir = self.repo_root / ".github" / "workflow-backups"
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ValueError("Could not find repository root (.git directory)")
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of all current workflows.
        
        Args:
            backup_name: Optional custom backup name.
            
        Returns:
            Backup identifier.
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating workflow backup: {backup_name}")
        
        if backup_path.exists():
            print(f"⚠️ Backup already exists: {backup_name}")
            return backup_name
        
        try:
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all workflow files
            workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
            
            if not workflow_files:
                print("⚠️ No workflow files found to backup")
                return backup_name
            
            backup_info = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "git_commit": self._get_current_commit(),
                "git_branch": self._get_current_branch(),
                "workflow_files": []
            }
            
            for workflow_file in workflow_files:
                # Copy workflow file
                backup_file = backup_path / workflow_file.name
                shutil.copy2(workflow_file, backup_file)
                
                # Record file info
                backup_info["workflow_files"].append({
                    "name": workflow_file.name,
                    "size": workflow_file.stat().st_size,
                    "modified": datetime.fromtimestamp(workflow_file.stat().st_mtime).isoformat()
                })
                
                print(f"  ✅ Backed up: {workflow_file.name}")
            
            # Save backup metadata
            with open(backup_path / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"✅ Backup created successfully: {backup_name}")
            print(f"   Location: {backup_path}")
            print(f"   Files: {len(workflow_files)}")
            
            return backup_name
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            # Clean up partial backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups.
        
        Returns:
            List of backup information dictionaries.
        """
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_path in self.backup_dir.iterdir():
            if backup_path.is_dir():
                info_file = backup_path / "backup_info.json"
                
                if info_file.exists():
                    try:
                        with open(info_file, 'r') as f:
                            backup_info = json.load(f)
                        
                        # Add computed fields
                        backup_info["backup_path"] = str(backup_path)
                        backup_info["file_count"] = len(backup_info.get("workflow_files", []))
                        
                        backups.append(backup_info)
                    except Exception as e:
                        print(f"⚠️ Could not read backup info for {backup_path.name}: {e}")
                else:
                    # Legacy backup without metadata
                    workflow_files = list(backup_path.glob("*.yml")) + list(backup_path.glob("*.yaml"))
                    backups.append({
                        "backup_name": backup_path.name,
                        "backup_path": str(backup_path),
                        "file_count": len(workflow_files),
                        "created_at": datetime.fromtimestamp(backup_path.stat().st_mtime).isoformat(),
                        "legacy": True
                    })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    def rollback_to_backup(self, backup_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Rollback workflows to a specific backup.
        
        Args:
            backup_name: Name of the backup to restore.
            dry_run: If True, only simulate the rollback.
            
        Returns:
            Dictionary containing rollback results.
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            raise ValueError(f"Backup not found: {backup_name}")
        
        print(f"🔄 {'Simulating' if dry_run else 'Performing'} rollback to: {backup_name}")
        
        result = {
            "backup_name": backup_name,
            "dry_run": dry_run,
            "start_time": datetime.now().isoformat(),
            "operations": [],
            "status": "in_progress"
        }
        
        try:
            # Load backup info if available
            info_file = backup_path / "backup_info.json"
            backup_info = {}
            if info_file.exists():
                with open(info_file, 'r') as f:
                    backup_info = json.load(f)
            
            # Get backup files
            backup_files = list(backup_path.glob("*.yml")) + list(backup_path.glob("*.yaml"))
            
            if not backup_files:
                raise ValueError(f"No workflow files found in backup: {backup_name}")
            
            print(f"📋 Found {len(backup_files)} workflow files in backup")
            
            # Create current backup before rollback
            if not dry_run:
                current_backup = self.create_backup(f"pre_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                result["current_backup"] = current_backup
                print(f"📦 Created pre-rollback backup: {current_backup}")
            
            # Process each backup file
            for backup_file in backup_files:
                target_file = self.workflows_dir / backup_file.name
                
                operation = {
                    "file": backup_file.name,
                    "action": "restore",
                    "status": "pending"
                }
                
                try:
                    if target_file.exists():
                        operation["previous_exists"] = True
                        operation["previous_size"] = target_file.stat().st_size
                    else:
                        operation["previous_exists"] = False
                    
                    operation["backup_size"] = backup_file.stat().st_size
                    
                    if not dry_run:
                        # Restore the file
                        shutil.copy2(backup_file, target_file)
                        print(f"  ✅ Restored: {backup_file.name}")
                    else:
                        print(f"  🔍 Would restore: {backup_file.name}")
                    
                    operation["status"] = "completed"
                    
                except Exception as e:
                    operation["status"] = "failed"
                    operation["error"] = str(e)
                    print(f"  ❌ Failed to restore {backup_file.name}: {e}")
                
                result["operations"].append(operation)
            
            # Check for workflows that exist now but not in backup (should be removed)
            current_workflows = set(f.name for f in self.workflows_dir.glob("*.yml")) | set(f.name for f in self.workflows_dir.glob("*.yaml"))
            backup_workflows = set(f.name for f in backup_files)
            extra_workflows = current_workflows - backup_workflows
            
            for extra_workflow in extra_workflows:
                operation = {
                    "file": extra_workflow,
                    "action": "remove",
                    "status": "pending"
                }
                
                try:
                    extra_file = self.workflows_dir / extra_workflow
                    
                    if not dry_run:
                        extra_file.unlink()
                        print(f"  🗑️ Removed extra workflow: {extra_workflow}")
                    else:
                        print(f"  🔍 Would remove extra workflow: {extra_workflow}")
                    
                    operation["status"] = "completed"
                    
                except Exception as e:
                    operation["status"] = "failed"
                    operation["error"] = str(e)
                    print(f"  ❌ Failed to remove {extra_workflow}: {e}")
                
                result["operations"].append(operation)
            
            # Summary
            completed_ops = [op for op in result["operations"] if op["status"] == "completed"]
            failed_ops = [op for op in result["operations"] if op["status"] == "failed"]
            
            result["summary"] = {
                "total_operations": len(result["operations"]),
                "completed": len(completed_ops),
                "failed": len(failed_ops)
            }
            
            if failed_ops:
                result["status"] = "partial_failure"
                print(f"⚠️ Rollback completed with {len(failed_ops)} failures")
            else:
                result["status"] = "success"
                print(f"✅ Rollback {'simulation' if dry_run else 'completed'} successfully")
            
            result["end_time"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            print(f"❌ Rollback failed: {e}")
            raise
    
    def rollback_to_commit(self, commit_hash: str, dry_run: bool = False) -> Dict[str, Any]:
        """Rollback workflows to a specific git commit.
        
        Args:
            commit_hash: Git commit hash to rollback to.
            dry_run: If True, only simulate the rollback.
            
        Returns:
            Dictionary containing rollback results.
        """
        print(f"🔄 {'Simulating' if dry_run else 'Performing'} rollback to commit: {commit_hash}")
        
        result = {
            "commit_hash": commit_hash,
            "dry_run": dry_run,
            "start_time": datetime.now().isoformat(),
            "operations": [],
            "status": "in_progress"
        }
        
        try:
            # Verify commit exists
            try:
                subprocess.run(
                    ["git", "cat-file", "-e", commit_hash],
                    cwd=self.repo_root,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                raise ValueError(f"Commit not found: {commit_hash}")
            
            # Create current backup before rollback
            if not dry_run:
                current_backup = self.create_backup(f"pre_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                result["current_backup"] = current_backup
                print(f"📦 Created pre-rollback backup: {current_backup}")
            
            # Get workflow files at the target commit
            try:
                git_result = subprocess.run(
                    ["git", "ls-tree", "-r", "--name-only", commit_hash, ".github/workflows/"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                target_workflows = [
                    line.strip() for line in git_result.stdout.split('\n')
                    if line.strip() and (line.endswith('.yml') or line.endswith('.yaml'))
                ]
                
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Failed to get workflow files from commit {commit_hash}: {e}")
            
            print(f"📋 Found {len(target_workflows)} workflow files in target commit")
            
            # Restore each workflow file from the commit
            for workflow_path in target_workflows:
                workflow_name = Path(workflow_path).name
                target_file = self.workflows_dir / workflow_name
                
                operation = {
                    "file": workflow_name,
                    "action": "restore_from_commit",
                    "status": "pending"
                }
                
                try:
                    if target_file.exists():
                        operation["previous_exists"] = True
                        operation["previous_size"] = target_file.stat().st_size
                    else:
                        operation["previous_exists"] = False
                    
                    if not dry_run:
                        # Get file content from commit
                        git_show_result = subprocess.run(
                            ["git", "show", f"{commit_hash}:{workflow_path}"],
                            cwd=self.repo_root,
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        
                        # Write content to file
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(git_show_result.stdout)
                        
                        print(f"  ✅ Restored from commit: {workflow_name}")
                    else:
                        print(f"  🔍 Would restore from commit: {workflow_name}")
                    
                    operation["status"] = "completed"
                    
                except subprocess.CalledProcessError as e:
                    operation["status"] = "failed"
                    operation["error"] = f"Git error: {e}"
                    print(f"  ❌ Failed to restore {workflow_name} from commit: {e}")
                except Exception as e:
                    operation["status"] = "failed"
                    operation["error"] = str(e)
                    print(f"  ❌ Failed to restore {workflow_name}: {e}")
                
                result["operations"].append(operation)
            
            # Remove workflows that don't exist in the target commit
            current_workflows = set(f.name for f in self.workflows_dir.glob("*.yml")) | set(f.name for f in self.workflows_dir.glob("*.yaml"))
            target_workflow_names = set(Path(wp).name for wp in target_workflows)
            extra_workflows = current_workflows - target_workflow_names
            
            for extra_workflow in extra_workflows:
                operation = {
                    "file": extra_workflow,
                    "action": "remove",
                    "status": "pending"
                }
                
                try:
                    extra_file = self.workflows_dir / extra_workflow
                    
                    if not dry_run:
                        extra_file.unlink()
                        print(f"  🗑️ Removed extra workflow: {extra_workflow}")
                    else:
                        print(f"  🔍 Would remove extra workflow: {extra_workflow}")
                    
                    operation["status"] = "completed"
                    
                except Exception as e:
                    operation["status"] = "failed"
                    operation["error"] = str(e)
                    print(f"  ❌ Failed to remove {extra_workflow}: {e}")
                
                result["operations"].append(operation)
            
            # Summary
            completed_ops = [op for op in result["operations"] if op["status"] == "completed"]
            failed_ops = [op for op in result["operations"] if op["status"] == "failed"]
            
            result["summary"] = {
                "total_operations": len(result["operations"]),
                "completed": len(completed_ops),
                "failed": len(failed_ops)
            }
            
            if failed_ops:
                result["status"] = "partial_failure"
                print(f"⚠️ Rollback completed with {len(failed_ops)} failures")
            else:
                result["status"] = "success"
                print(f"✅ Rollback {'simulation' if dry_run else 'completed'} successfully")
            
            result["end_time"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            print(f"❌ Rollback failed: {e}")
            raise
    
    def cleanup_old_backups(self, keep_count: int = 10, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up old backup files.
        
        Args:
            keep_count: Number of recent backups to keep.
            keep_days: Number of days to keep backups.
            
        Returns:
            Dictionary containing cleanup results.
        """
        print(f"🧹 Cleaning up old backups (keep {keep_count} recent, {keep_days} days)")
        
        backups = self.list_backups()
        
        if not backups:
            print("📭 No backups found to clean up")
            return {"removed": 0, "kept": 0}
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Determine which backups to remove
        to_remove = []
        
        # Keep recent backups by count
        recent_backups = backups[:keep_count]
        old_backups = backups[keep_count:]
        
        for backup in old_backups:
            backup_date = datetime.fromisoformat(backup["created_at"].replace('Z', '+00:00').replace('+00:00', ''))
            
            if backup_date < cutoff_date:
                to_remove.append(backup)
        
        # Remove old backups
        removed_count = 0
        for backup in to_remove:
            try:
                backup_path = Path(backup["backup_path"])
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                    print(f"  🗑️ Removed old backup: {backup['backup_name']}")
                    removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove backup {backup['backup_name']}: {e}")
        
        kept_count = len(backups) - removed_count
        
        print(f"✅ Cleanup completed: removed {removed_count}, kept {kept_count}")
        
        return {
            "removed": removed_count,
            "kept": kept_count,
            "total_backups": len(backups)
        }
    
    def _get_current_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"


def main():
    """Main entry point for the workflow rollback manager."""
    parser = argparse.ArgumentParser(
        description="Manage workflow rollbacks and backups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s backup                           # Create backup
  %(prog)s list                            # List backups
  %(prog)s rollback --backup backup_name   # Rollback to backup
  %(prog)s rollback --commit abc123        # Rollback to commit
  %(prog)s cleanup                         # Clean old backups
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create workflow backup")
    backup_parser.add_argument(
        "--name",
        type=str,
        help="Custom backup name"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format"
    )
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback workflows")
    rollback_group = rollback_parser.add_mutually_exclusive_group(required=True)
    rollback_group.add_argument(
        "--backup",
        type=str,
        help="Backup name to rollback to"
    )
    rollback_group.add_argument(
        "--commit",
        type=str,
        help="Git commit hash to rollback to"
    )
    rollback_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate rollback without making changes"
    )
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old backups")
    cleanup_parser.add_argument(
        "--keep-count",
        type=int,
        default=10,
        help="Number of recent backups to keep (default: 10)"
    )
    cleanup_parser.add_argument(
        "--keep-days",
        type=int,
        default=30,
        help="Number of days to keep backups (default: 30)"
    )
    
    # Global options
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root path (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = WorkflowRollbackManager(args.repo_root)
        
        if args.command == "backup":
            backup_name = manager.create_backup(args.name)
            print(f"\n✅ Backup created: {backup_name}")
            
        elif args.command == "list":
            backups = manager.list_backups()
            
            if args.format == "json":
                print(json.dumps(backups, indent=2))
            else:
                if not backups:
                    print("📭 No backups found")
                else:
                    print(f"\n📋 Available Backups ({len(backups)} total)")
                    print("=" * 80)
                    
                    for backup in backups:
                        created = backup.get("created_at", "Unknown")
                        if created != "Unknown":
                            try:
                                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00').replace('+00:00', ''))
                                created = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        
                        print(f"📦 {backup['backup_name']}")
                        print(f"   Created: {created}")
                        print(f"   Files: {backup['file_count']}")
                        
                        if backup.get("git_commit"):
                            print(f"   Commit: {backup['git_commit'][:8]}")
                        if backup.get("git_branch"):
                            print(f"   Branch: {backup['git_branch']}")
                        
                        print()
            
        elif args.command == "rollback":
            if args.backup:
                result = manager.rollback_to_backup(args.backup, args.dry_run)
            else:
                result = manager.rollback_to_commit(args.commit, args.dry_run)
            
            print(f"\n📊 Rollback Summary:")
            print(f"   Status: {result['status']}")
            print(f"   Operations: {result['summary']['total_operations']}")
            print(f"   Completed: {result['summary']['completed']}")
            print(f"   Failed: {result['summary']['failed']}")
            
            if result["status"] != "success":
                sys.exit(1)
            
        elif args.command == "cleanup":
            result = manager.cleanup_old_backups(args.keep_count, args.keep_days)
            print(f"\n📊 Cleanup Summary:")
            print(f"   Removed: {result['removed']}")
            print(f"   Kept: {result['kept']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()