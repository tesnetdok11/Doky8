"""
GITHUB SYNC - Backup & auto-push log ke GitHub
"""

import logging
import os
import json
import asyncio
from datetime import datetime
from github import Github
from github import Auth
from config.settings import settings

class GitHubSync:
    def __init__(self):
        self.github = None
        self.repo = None
        self.enabled = settings.ENABLE_GITHUB_SYNC
        
    async def initialize(self):
        """Initialize GitHub connection"""
        if not self.enabled:
            logging.info("🔕 GitHub sync disabled")
            return
            
        logging.info("🐙 INITIALIZING GITHUB SYNC...")
        
        try:
            # Load from settings - SEKARANG SUDAH ADA
            github_token = settings.GITHUB_TOKEN
            github_repo = settings.GITHUB_REPO
            
            if not github_token or not github_repo:
                logging.warning("⚠️ GitHub token or repository not configured")
                self.enabled = False
                return
                
            # Authenticate with GitHub
            auth = Auth.Token(github_token)
            self.github = Github(auth=auth)
            
            # Get repository
            self.repo = self.github.get_repo(github_repo)
            
            # Test connection
            self.repo.get_branches()
            logging.info("✅ GITHUB SYNC CONNECTED SUCCESSFULLY")
            
        except Exception as e:
            logging.error(f"❌ GitHub sync initialization failed: {e}")
            self.enabled = False
            
    # ... rest of the methods remain the same ...            
    async def sync_logs(self):
        """Sync log files to GitHub"""
        if not self.enabled:
            return
            
        try:
            log_files = [
                "logs/dokyos.log",
                "logs/performance.log", 
                "logs/errors.log"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    await self._upload_file(log_file, f"logs/{os.path.basename(log_file)}")
                    
            logging.info("📝 Log files synced to GitHub")
            
        except Exception as e:
            logging.error(f"❌ Log sync error: {e}")
            
    async def sync_signals(self, signals):
        """Sync signals to GitHub"""
        if not self.enabled or not signals:
            return
            
        try:
            signals_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'signals': signals
            }
            
            # Create signals file
            filename = f"signals/signals_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            await self._upload_content(
                json.dumps(signals_data, indent=2, default=str),
                filename,
                f"Update signals {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
        except Exception as e:
            logging.error(f"❌ Signals sync error: {e}")
            
    async def sync_analysis(self, analysis_data):
        """Sync analysis data to GitHub"""
        if not self.enabled:
            return
            
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis/analysis_{timestamp}.json"
            
            await self._upload_content(
                json.dumps(analysis_data, indent=2, default=str),
                filename,
                f"Update analysis {timestamp}"
            )
            
        except Exception as e:
            logging.error(f"❌ Analysis sync error: {e}")
            
    async def _upload_file(self, local_path, remote_path):
        """Upload local file to GitHub"""
        try:
            with open(local_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            await self._upload_content(content, remote_path, f"Update {remote_path}")
            
        except Exception as e:
            logging.error(f"❌ File upload error for {local_path}: {e}")
            
    async def _upload_content(self, content, path, commit_message):
        """Upload content to GitHub"""
        try:
            # Check if file exists
            try:
                file = self.repo.get_contents(path)
                # Update existing file
                self.repo.update_file(
                    path,
                    commit_message,
                    content,
                    file.sha
                )
            except:
                # Create new file
                self.repo.create_file(
                    path,
                    commit_message, 
                    content
                )
                
        except Exception as e:
            logging.error(f"❌ GitHub upload error for {path}: {e}")
            
    async def backup_system_state(self, system_state):
        """Backup complete system state"""
        if not self.enabled:
            return
            
        try:
            state_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_state': system_state,
                'version': settings.VERSION
            }
            
            await self._upload_content(
                json.dumps(state_data, indent=2, default=str),
                f"backups/system_state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                f"System state backup {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            logging.info("💾 System state backed up to GitHub")
            
        except Exception as e:
            logging.error(f"❌ System state backup error: {e}")
            
    async def get_latest_config(self, config_file):
        """Get latest configuration from GitHub"""
        if not self.enabled:
            return None
            
        try:
            file = self.repo.get_contents(f"config/{config_file}")
            return file.decoded_content.decode('utf-8')
        except Exception as e:
            logging.error(f"❌ Config fetch error for {config_file}: {e}")
            return None
            
    async def cleanup(self):
        """Cleanup GitHub connection"""
        if self.github:
            self.github.close()
        logging.info("🔒 GitHub sync cleanup completed")
