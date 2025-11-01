"""
GITHUB CONFIG - Konfigurasi sinkronisasi GitHub
"""

import os
from config.settings import settings

class GitHubConfig:
    # Repository configuration
    REPOSITORY = settings.GITHUB_REPO
    BRANCH = "main"
    
    # Sync intervals (seconds)
    AUTO_SYNC_INTERVAL = 3600  # 1 hour
    BACKUP_INTERVAL = 86400    # 24 hours
    
    # Files and directories to sync
    SYNC_PATHS = [
        "logs/",
        "data/historical/",
        "learning_memory/",
        "config/",
        "reports/"
    ]
    
    # File patterns to exclude
    EXCLUDE_PATTERNS = [
        "*.tmp",
        "*.cache",
        "*.key",
        "*.salt"
    ]
    
    # Commit messages
    COMMIT_MESSAGES = {
        "auto_sync": "🤖 Auto-sync: System data backup",
        "manual_backup": "💾 Manual backup: System state",
        "error_report": "📋 Error report: System issues"
    }
