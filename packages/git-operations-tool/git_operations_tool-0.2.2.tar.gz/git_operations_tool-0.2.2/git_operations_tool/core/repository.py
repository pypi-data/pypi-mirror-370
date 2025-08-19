import os
import time
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
import fnmatch

class RepositoryManager:
    def __init__(self):
        self.repo = None
        self.repo_url = None
        
    def initialize_or_clone_repo(self, repo_url, local_path="."):
        """Initialize or clone the repository"""
        try:
            # Try to open existing repo
            self.repo = Repo(local_path)
            print(f"✓ Found existing Git repository at {local_path}")
            
            # Add remote if it doesn't exist
            try:
                origin = self.repo.remote('origin')
                if origin.url != repo_url:
                    print(f"Warning: Remote origin URL differs from provided URL")
                    print(f"Existing: {origin.url}")
                    print(f"Provided: {repo_url}")
            except:
                self.repo.create_remote('origin', repo_url)
                print(f"✓ Added remote origin: {repo_url}")
                
            return self.repo
            
        except InvalidGitRepositoryError:
            # Initialize new repo
            print(f"Initializing new Git repository at {local_path}")
            self.repo = Repo.init(local_path)
            self.repo.create_remote('origin', repo_url)
            print(f"✓ Created new repository with remote: {repo_url}")
            return self.repo

    def _load_gitignore_patterns(self):
        """Load gitignore patterns from .gitignore file"""
        gitignore_path = Path(self.repo.working_dir) / '.gitignore'
        patterns = []
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        # Add default patterns for common unwanted files
        default_patterns = [
            '__pycache__/',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.DS_Store',
            'Thumbs.db',
            '*.egg-info/',
            'dist/',
            'build/',
            '.pytest_cache/',
            '.coverage'
        ]
        
        return patterns + default_patterns

    def _is_ignored(self, file_path, patterns):
        """Check if a file matches any gitignore pattern with improved matching"""
        # Normalize path separators for consistent matching
        normalized_path = file_path.replace('\\', '/')
        
        for pattern in patterns:
            # Skip empty patterns
            if not pattern.strip():
                continue
                
            # Handle negation patterns (starting with !)
            if pattern.startswith('!'):
                # TODO: Implement negation logic if needed
                continue
            
            # Normalize pattern separators
            normalized_pattern = pattern.replace('\\', '/')
            
            # Handle directory patterns (ending with /)
            if normalized_pattern.endswith('/'):
                dir_pattern = normalized_pattern.rstrip('/')
                # Check if the file is inside this directory
                if normalized_path.startswith(dir_pattern + '/') or normalized_path == dir_pattern:
                    return True
                # Also check if any parent directory matches
                path_parts = normalized_path.split('/')
                for i in range(len(path_parts)):
                    parent_path = '/'.join(path_parts[:i+1])
                    if fnmatch.fnmatch(parent_path, dir_pattern):
                        return True
            else:
                # Handle file patterns
                # Check exact match
                if fnmatch.fnmatch(normalized_path, normalized_pattern):
                    return True
                
                # Check basename match
                if fnmatch.fnmatch(os.path.basename(normalized_path), normalized_pattern):
                    return True
                
                # Handle patterns with path separators
                if '/' in normalized_pattern:
                    # Check if pattern matches from root
                    if fnmatch.fnmatch(normalized_path, normalized_pattern):
                        return True
                    # Check if pattern matches any subdirectory
                    if fnmatch.fnmatch(normalized_path, '*/' + normalized_pattern):
                        return True
                
        return False

    def get_all_files_and_folders(self, path="."):
        """Get all files and folders that should be tracked by git with safety checks"""
        items = []
        patterns = self._load_gitignore_patterns()
        
        # Additional safety patterns for sensitive files
        sensitive_patterns = [
            '*.key', '*.pem', '*.p12', '*.pfx',  # Certificate/key files
            '*.env', '.env.*',  # Environment files
            '*secret*', '*password*', '*credential*',  # Files with sensitive names
            '*.sql', '*.db', '*.sqlite',  # Database files (might contain sensitive data)
            'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',  # SSH keys
            '.aws/', '.ssh/', '.gnupg/',  # Config directories
        ]
        
        all_patterns = patterns + sensitive_patterns
        
        # Walk through directory tree
        for root, dirs, files in os.walk(path):
            # Skip .git directory and other version control directories
            if any(vcs in root for vcs in ['.git', '.svn', '.hg', '.bzr']):
                continue
                
            # Skip common build/cache directories that might be missed
            if any(skip_dir in root for skip_dir in ['node_modules', '__pycache__', '.pytest_cache', 'dist', 'build']):
                continue
                
            # Add files
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, path).replace('\\', '/')
                
                # Skip files that match gitignore patterns
                if self._is_ignored(relative_path, all_patterns):
                    continue
                
                # Skip hidden files except important ones
                if relative_path.startswith('.'):
                    allowed_hidden = ['.gitignore', '.gitattributes', '.github/', '.vscode/']
                    if not any(relative_path.startswith(allowed) for allowed in allowed_hidden):
                        continue
                
                # Additional safety check for file size (skip very large files)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:  # Skip files larger than 100MB
                        print(f"⚠ Skipping large file: {relative_path} ({file_size/1024/1024:.1f}MB)")
                        continue
                except OSError:
                    # If we can't get file size, skip it
                    continue
                
                # Check for binary files (basic check)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(1024)  # Try to read first 1KB as text
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary files and files we can't read
                    binary_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin', '.img', '.iso']
                    if any(relative_path.lower().endswith(ext) for ext in binary_extensions):
                        print(f"⚠ Skipping binary file: {relative_path}")
                        continue
                
                items.append(('file', relative_path))
        
        # Sort items for consistent ordering
        items.sort(key=lambda x: x[1])
        
        return items

    def commit_all_changes(self, commit_message="Auto commit: Add all files"):
        """Commit all changes at once instead of individual files"""
        try:
            # Check if there are any changes
            if self.repo.is_dirty() or self.repo.untracked_files:
                # Add all files
                self.repo.git.add('.')
                
                # Check if there are staged changes after adding
                # For new repos without any commits, we need to handle the case where HEAD doesn't exist
                try:
                    if self.repo.head.is_valid():
                        # Repository has commits, compare with HEAD
                        has_staged_changes = bool(self.repo.index.diff("HEAD"))
                    else:
                        # New repository, check if index has any files
                        has_staged_changes = bool(list(self.repo.index.entries.keys()))
                except:
                    # Fallback: check if index has any files
                    has_staged_changes = bool(list(self.repo.index.entries.keys()))
                
                if has_staged_changes:
                    # Create commit
                    commit = self.repo.index.commit(commit_message)
                    print(f"✓ Committed all changes (commit: {commit.hexsha[:8]})")
                    return True
                else:
                    print("⚠ No changes to commit")
                    return False
            else:
                print("⚠ No changes to commit")
                return False
                
        except Exception as e:
            print(f"✗ Error committing changes: {str(e)}")
            return False

    def push_to_remote(self, branch='main'):
        """Push changes to remote repository"""
        try:
            # Ensure we're on the correct branch
            try:
                current_branch = self.repo.active_branch.name
                if current_branch != branch:
                    try:
                        self.repo.git.checkout(branch)
                    except:
                        # Create branch if it doesn't exist
                        self.repo.git.checkout('-b', branch)
            except:
                # For new repos, create the main branch
                self.repo.git.checkout('-b', branch)
            
            # Push to remote
            origin = self.repo.remote('origin')
            origin.push(refspec=f'{branch}:{branch}')
            print(f"✓ Pushed changes to remote/{branch}")
            return True
            
        except Exception as e:
            print(f"✗ Error pushing to remote: {str(e)}")
            return False
            
    def push_to_remote_with_retry(self, branch='main', max_retries=3, backoff_factor=2.0):
        """Push changes to remote repository with retry mechanism"""
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Ensure we're on the correct branch
                try:
                    current_branch = self.repo.active_branch.name
                    if current_branch != branch:
                        try:
                            self.repo.git.checkout(branch)
                        except:
                            # Create branch if it doesn't exist
                            self.repo.git.checkout('-b', branch)
                except:
                    # For new repos, create the main branch
                    self.repo.git.checkout('-b', branch)
                
                # Push to remote
                origin = self.repo.remote('origin')
                origin.push(refspec=f'{branch}:{branch}')
                print(f"✓ Pushed changes to remote/{branch}")
                return True
                
            except Exception as e:
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = backoff_factor ** (retry_count - 1)
                    print(f"✗ Error pushing to remote: {str(e)}")
                    print(f"Retrying in {wait_time:.1f} seconds (attempt {retry_count}/{max_retries})...")
                    
                    # Try to pull changes before retrying
                    try:
                        print("Pulling latest changes before retry...")
                        origin = self.repo.remote('origin')
                        origin.pull(branch)
                    except Exception as pull_error:
                        print(f"Warning: Could not pull latest changes: {str(pull_error)}")
                    
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed to push after {max_retries} attempts: {str(e)}")
                    return False
        
        return False

    def commit_and_push_item(self, item_type, item_path, branch='main'):
        """Commit and push a single item"""
        try:
            # Check if item still exists
            full_path = Path(self.repo.working_dir) / item_path
            if not full_path.exists():
                print(f"⚠ Skipping {item_path} - file/folder no longer exists")
                return False
            
            # Add the item to staging
            self.repo.index.add([item_path])
            
            # Check if there are any staged changes for this specific file
            try:
                if self.repo.head.is_valid():
                    # Repository has commits, compare with HEAD
                    staged_files = self.repo.index.diff("HEAD")
                    has_changes = any(item.a_path == item_path for item in staged_files)
                else:
                    # New repository, check if file is in index
                    has_changes = any(item_path in str(key) for key in self.repo.index.entries.keys())
            except:
                # Fallback: assume there are changes if file exists
                has_changes = True
            
            if not has_changes:
                print(f"⚠ No changes to commit for {item_path}")
                return False
            
            # Create commit message
            commit_msg = f"Add {item_type}: {item_path}"
            
            # Commit
            commit = self.repo.index.commit(commit_msg)
            print(f"✓ Committed {item_type}: {item_path} (commit: {commit.hexsha[:8]})")
            
            # Ensure we're on the correct branch
            try:
                current_branch = self.repo.active_branch.name
                if current_branch != branch:
                    try:
                        self.repo.git.checkout(branch)
                    except:
                        # Create branch if it doesn't exist
                        self.repo.git.checkout('-b', branch)
            except:
                # For new repos, create the main branch
                self.repo.git.checkout('-b', branch)
            
            # Push to remote
            origin = self.repo.remote('origin')
            origin.push(refspec=f'{branch}:{branch}')
            print(f"✓ Pushed {item_type}: {item_path} to remote/{branch}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing {item_path}: {str(e)}")
            return False
            
    def commit_and_push_item_with_retry(self, item_type, item_path, branch='main', max_retries=3, backoff_factor=2.0):
        """Commit and push a single item with retry mechanism"""
        try:
            # Check if item still exists
            full_path = Path(self.repo.working_dir) / item_path
            if not full_path.exists():
                print(f"⚠ Skipping {item_path} - file/folder no longer exists")
                return False
            
            # Ensure we're on the correct branch before committing
            try:
                current_branch = self.repo.active_branch.name
                if current_branch != branch:
                    try:
                        self.repo.git.checkout(branch)
                        print(f"✓ Switched to branch '{branch}'")
                    except Exception as checkout_error:
                        # Create branch if it doesn't exist
                        try:
                            self.repo.git.checkout('-b', branch)
                            print(f"✓ Created and switched to new branch '{branch}'")
                        except Exception as create_error:
                            print(f"✗ Failed to switch/create branch '{branch}': {str(create_error)}")
                            return False
            except Exception as branch_error:
                # For new repos, create the main branch
                try:
                    self.repo.git.checkout('-b', branch)
                    print(f"✓ Created initial branch '{branch}'")
                except Exception as initial_error:
                    print(f"✗ Failed to create initial branch '{branch}': {str(initial_error)}")
                    return False
            
            # Add the item to staging
            self.repo.index.add([item_path])
            
            # Check if there are any staged changes for this specific file
            try:
                if self.repo.head.is_valid():
                    # Repository has commits, compare with HEAD
                    staged_files = self.repo.index.diff("HEAD")
                    has_changes = any(item.a_path == item_path for item in staged_files)
                else:
                    # New repository, check if file is in index
                    has_changes = any(item_path in str(key) for key in self.repo.index.entries.keys())
            except:
                # Fallback: assume there are changes if file exists
                has_changes = True
            
            if not has_changes:
                print(f"⚠ No changes to commit for {item_path}")
                return False
            
            # Create commit message with timestamp for uniqueness
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            commit_msg = f"Add {item_type}: {item_path} [{timestamp}]"
            
            # Commit
            commit = self.repo.index.commit(commit_msg)
            print(f"✓ Committed {item_type}: {item_path} (commit: {commit.hexsha[:8]})")
            
            # Push with retry and improved error handling
            retry_count = 0
            while retry_count <= max_retries:
                try:
                    # Verify we're still on the correct branch
                    current_branch = self.repo.active_branch.name
                    if current_branch != branch:
                        print(f"Warning: Branch mismatch. Expected '{branch}', got '{current_branch}'")
                        self.repo.git.checkout(branch)
                    
                    # Try to pull latest changes first to minimize conflicts
                    origin = self.repo.remote('origin')
                    try:
                        origin.pull(branch)
                    except Exception as pull_error:
                        # If pull fails, it's likely because remote doesn't exist yet or other issues
                        # We'll proceed with push and handle conflicts there
                        pass
                    
                    # First try normal push
                    try:
                        origin.push(refspec=f'{branch}:{branch}')
                        print(f"✓ Pushed {item_type}: {item_path} to remote/{branch}")
                        return True
                    except Exception as push_error:
                        # If normal push fails, try force push (for individual commits this is generally safe)
                        if "rejected" in str(push_error).lower() or "non-fast-forward" in str(push_error).lower() or "failed to push some refs" in str(push_error).lower():
                            try:
                                print(f"⚠ Resolving push conflict with force push...")
                                origin.push(refspec=f'{branch}:{branch}', force=True)
                                print(f"✓ Successfully pushed {item_type}: {item_path} to remote/{branch}")
                                return True
                            except Exception as force_error:
                                print(f"✗ Force push also failed: {str(force_error)}")
                                raise force_error
                        else:
                            raise push_error
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        wait_time = backoff_factor ** (retry_count - 1)
                        print(f"✗ Error pushing to remote: {str(e)}")
                        print(f"Retrying in {wait_time:.1f} seconds (attempt {retry_count}/{max_retries})...")
                        
                        # Try to pull changes before retrying (only for non-force scenarios)
                        if "rejected" not in str(e).lower():
                            try:
                                print("Pulling latest changes before retry...")
                                origin = self.repo.remote('origin')
                                origin.pull(branch)
                            except Exception as pull_error:
                                print(f"Warning: Could not pull latest changes: {str(pull_error)}")
                        
                        time.sleep(wait_time)
                    else:
                        print(f"✗ Failed to push after {max_retries} attempts: {str(e)}")
                        return False
            
            return False
            
        except Exception as e:
            print(f"✗ Error processing {item_path}: {str(e)}")
            import traceback
            print(f"Debug: Full error traceback:")
            traceback.print_exc()
            return False

    def auto_commit_and_push_all(self, branch='main'):
        """Improved auto commit and push functionality"""
        print("\nAnalyzing repository status...")
        
        # Check repository status
        has_untracked = bool(self.repo.untracked_files)
        has_modified = self.repo.is_dirty()
        
        if not has_untracked and not has_modified:
            print("✓ Repository is clean - no changes to commit")
            return True
        
        # Show what will be committed
        if has_untracked:
            print(f"Untracked files ({len(self.repo.untracked_files)}):")
            for file in self.repo.untracked_files[:10]:  # Show first 10
                print(f"  + {file}")
            if len(self.repo.untracked_files) > 10:
                print(f"  ... and {len(self.repo.untracked_files) - 10} more files")
        
        if has_modified:
            print("Modified files:")
            try:
                if self.repo.head.is_valid():
                    for item in self.repo.index.diff(None):
                        print(f"  M {item.a_path}")
                else:
                    print("  (New repository - all files will be added)")
            except:
                print("  (New repository - all files will be added)")
        
        # Check if this is the first commit
        is_first_commit = False
        try:
            is_first_commit = not self.repo.head.is_valid()
        except:
            is_first_commit = True
        
        if is_first_commit:
            print("\n🎉 This appears to be the first commit to this repository!")
        
        # Confirm before proceeding
        print(f"\nThis will commit and push all changes to the '{branch}' branch.")
        confirm = input("Do you want to proceed? (y/N): ").strip().lower()
        
        if confirm != 'y':
            print("Operation cancelled.")
            return False
        
        # Commit and push all changes
        if self.commit_all_changes("Initial commit" if is_first_commit else "Auto commit: Add all files"):
            return self.push_to_remote(branch)
        else:
            return False