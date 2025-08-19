"""
Main module for the Git Operations Tool application.
This module serves as the entry point for the application and contains the main
GitOperationsTool class that orchestrates the various components of the tool.
It handles initialization, user interaction, and execution of Git operations.
"""
import sys
from git import Repo, InvalidGitRepositoryError
from git_operations_tool.core.repository import RepositoryManager
from git_operations_tool.core.branches import BranchManager
from git_operations_tool.core.operations import GitOperations
from git_operations_tool.core.pull_requests import PullRequestManager
from git_operations_tool.interface.prompts import get_repo_url
from git_operations_tool.interface.menu import MenuSystem
import time


class GitOperationsTool:
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.branch_manager = None
        self.operations = None
        self.pr_manager = None
        self.menu = None

    def auto_commit_and_push(self):
        """Auto commit and push with options for bulk or individual commits"""
        print("\nAnalyzing repository status...")
        
        # Check if repository is in a clean state
        try:
            if not self.repo_manager.repo.is_dirty() and not self.repo_manager.repo.untracked_files:
                print("✓ Repository is already clean - no changes to commit.")
                return
        except Exception as e:
            print(f"Warning: Could not check repository status: {str(e)}")
        
        print("Discovering files and folders...")
        items = self.repo_manager.get_all_files_and_folders()

        if not items:
            print("No files or folders found to commit.")
            return

        print(f"Found {len(items)} items to process:")
        for i, (item_type, item_path) in enumerate(items[:10]):  # Show first 10
            print(f"  - {item_type}: {item_path}")
        
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more items")

        # Ask for commit mode
        print("\n" + "="*60)
        print("COMMIT MODE OPTIONS:")
        print("="*60)
        print("1. 🚀 Bulk commit (all changes in one commit)")
        print("   ├─ Faster execution")
        print("   ├─ Single commit message")
        print("   └─ Recommended for large projects")
        print()
        print("2. 📁 Individual file commits (each file separately)")
        print("   ├─ Detailed commit history")
        print("   ├─ Better tracking per file")
        print("   ├─ Configurable delay between commits")
        print("   └─ Recommended for careful version control")
        print("="*60)

        while True:
            mode_choice = input("\nSelect commit mode (1-2): ").strip()
            if mode_choice in ['1', '2']:
                break
            print("❌ Invalid choice. Please enter 1 or 2.")

        # Handle based on mode choice
        if mode_choice == '1':
            self._handle_bulk_commit()
        else:
            self._handle_individual_commits(items)

    def _handle_bulk_commit(self):
        """Handle bulk commit mode"""
        print("\n🚀 BULK COMMIT MODE")
        print("="*50)
        print("All changes will be committed together in a single commit.")
        
        # Show what will be committed
        try:
            untracked = self.repo_manager.repo.untracked_files
            modified = [item.a_path for item in self.repo_manager.repo.index.diff(None)]
            
            if untracked:
                print(f"\n📄 Untracked files ({len(untracked)}):")
                for file in untracked[:5]:
                    print(f"   + {file}")
                if len(untracked) > 5:
                    print(f"   ... and {len(untracked) - 5} more files")
            
            if modified:
                print(f"\n✏️  Modified files ({len(modified)}):")
                for file in modified[:5]:
                    print(f"   M {file}")
                if len(modified) > 5:
                    print(f"   ... and {len(modified) - 5} more files")
                    
        except Exception as e:
            print(f"Warning: Could not analyze changes: {str(e)}")
        
        print("="*50)
        confirm = input("\n❓ Do you want to proceed with bulk commit? (y/N): ").strip().lower()

        if confirm != 'y':
            print("❌ Operation cancelled.")
            return

        print("\n⏳ Processing bulk commit...")
        if self.repo_manager.commit_all_changes("Bulk commit: Add all files"):
            print("✅ Successfully created bulk commit.")
            print("⏳ Pushing changes to remote...")
            if self.repo_manager.push_to_remote_with_retry():
                print("🎉 Successfully committed and pushed all changes!")
            else:
                print("❌ Failed to push changes to remote.")
        else:
            print("❌ Failed to commit changes.")

    def _handle_individual_commits(self, items):
        """Handle individual file commits mode"""
        print(f"\n📁 INDIVIDUAL FILE COMMIT MODE")
        print("="*50)
        print(f"This will create {len(items)} separate commits.")
        print("Each file will be committed and pushed individually.")
        
        # Ask for delay between commits
        delay = 1.5  # Increased default delay for better reliability
        print(f"\n⏱️  TIMING CONFIGURATION:")
        print(f"Recommended delay: 1.5-3.0 seconds (prevents rate limiting)")
        
        try:
            delay_input = input(
                f"Enter delay between commits in seconds (default: {delay}): ").strip()
            if delay_input:
                delay = float(delay_input)
                if delay < 0:
                    delay = 0
                elif delay > 10:
                    print("⚠️  Large delay detected. This will take a while.")
        except ValueError:
            print(f"❌ Invalid delay value. Using default delay of {delay} seconds.")

        # Estimate total time
        estimated_time = len(items) * (delay + 2)  # 2 seconds per commit operation
        print(f"\n📊 OPERATION SUMMARY:")
        print(f"   Items to process: {len(items)}")
        print(f"   Delay per commit: {delay} seconds")
        print(f"   Estimated time: {estimated_time/60:.1f} minutes")
        print("="*50)
        
        confirm = input(
            f"\n❓ Do you want to proceed? (y/N): ").strip().lower()

        if confirm != 'y':
            print("❌ Operation cancelled.")
            return

        # Process each item
        print(f"\n🔄 Processing {len(items)} items...")
        print("="*50)
        success_count = 0
        failed_items = []

        for i, (item_type, item_path) in enumerate(items, 1):
            print(f"\n[{i:3d}/{len(items)}] 📄 {item_type}: {item_path}")
            
            try:
                if self.repo_manager.commit_and_push_item_with_retry(item_type, item_path):
                    success_count += 1
                    print(f"            ✅ Successfully processed")
                else:
                    failed_items.append((item_type, item_path))
                    print(f"            ❌ Failed to process")
                    
            except Exception as e:
                failed_items.append((item_type, item_path))
                print(f"            💥 Error: {str(e)}")

            # Apply delay between operations (except for last item)
            if i < len(items) and delay > 0:
                print(f"            ⏳ Waiting {delay} seconds...")
                time.sleep(delay)

        # Summary
        print("\n" + "="*60)
        print("📊 OPERATION SUMMARY")
        print("="*60)
        print(f"✅ Successfully processed: {success_count}/{len(items)} items")
        print(f"❌ Failed: {len(failed_items)}/{len(items)} items")
        
        if failed_items:
            print(f"\n💥 FAILED ITEMS:")
            for item_type, item_path in failed_items[:10]:  # Show first 10 failures
                print(f"   - {item_type}: {item_path}")
            if len(failed_items) > 10:
                print(f"   ... and {len(failed_items) - 10} more items")
        
        if success_count == len(items):
            print(f"\n🎉 All items processed successfully!")
        elif success_count > 0:
            print(f"\n⚠️  Partial success. {success_count} items processed.")
        else:
            print(f"\n💥 No items were processed successfully.")
        print("="*60)

    def run(self):
        """Main application loop"""
        print("Git Operations Tool")
        print("=" * 50)

        # Get repository URL and initialize
        repo_url = get_repo_url()

        try:
            self.repo_manager.initialize_or_clone_repo(repo_url)
            self.branch_manager = BranchManager(self.repo_manager.repo)
            self.operations = GitOperations(self.repo_manager.repo)
            self.pr_manager = PullRequestManager(
                self.repo_manager.repo, repo_url)
            self.menu = MenuSystem(self)
        except Exception as e:
            print(f"✗ Error initializing repository: {str(e)}")
            sys.exit(1)

        # Main menu loop
        while True:
            self.menu.show_menu()

            try:
                choice = input("\nEnter your choice (1-14): ").strip()
                if not self.menu.handle_choice(choice):
                    break

            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"✗ Error: {str(e)}")


def run_tool():
    """Entry point for the console script"""
    tool = GitOperationsTool()
    tool.run()


if __name__ == "__main__":
    tool = GitOperationsTool()
    tool.run()
