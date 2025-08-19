"""
Command Line Interface for Commit-Gen.
"""

import argparse
import getpass
import os
import subprocess
import sys
import tempfile
import termios
import tty
from typing import List, Optional

from .config import (
    PROVIDERS,
    ensure_config_dir,
    get_api_key,
    get_current_config,
    get_default_model_for_provider,
    get_model,
    get_prompt,
    get_provider,
    list_providers,
    provider_requires_api_key,
    save_api_key,
    save_base_url,
    save_model,
    save_prompt,
    save_provider,
    validate_provider,
)
from .core import check_ollama, debug_log, generate_changelog_by_commit_sha
from .git_utils import (
    create_git_commit,
    get_file_info,
    get_modified_files,
    get_staged_files,
    is_git_repository,
    push_to_origin,
    stage_specific_files,
)


def get_key():
    """Get a single keypress from the user."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == "\x1b":  # Escape sequence
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                if ch3 == "A":
                    return "UP"
                elif ch3 == "B":
                    return "DOWN"
                elif ch3 == "C":
                    return "RIGHT"
                elif ch3 == "D":
                    return "LEFT"
        elif ch == " ":
            return "SPACE"
        elif ch == "\r" or ch == "\n":
            return "ENTER"
        elif ch == "q":
            return "QUIT"
        elif ch == "a":
            return "SELECT_ALL"
        elif ch == "n":
            return "SELECT_NONE"
        elif ch == "s":
            return "SKIP"
        else:
            return ch
    except KeyboardInterrupt:
        return "QUIT"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def clear_screen():
    """Clear the terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")


def edit_commit_message(initial_message: str) -> str:
    """Allow user to edit commit message."""
    print("\n📝 Edit commit message:")
    print("=" * 60)
    print("Current commit message:")
    print("-" * 30)
    print(initial_message)
    print("-" * 30)

    while True:
        try:
            print("\nOptions:")
            print("1. Edit message")
            print("2. Use as-is")
            print("3. Cancel")

            choice = input("\nEnter choice (1-3): ").strip()

            if choice == "1":
                # Use external editor if available, otherwise use input
                editor = os.environ.get("EDITOR", "nano")

                # Create temporary file with current message
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                    f.write(initial_message)
                    temp_file = f.name

                try:
                    # Open editor
                    subprocess.run([editor, temp_file], check=True)

                    # Read edited message
                    with open(temp_file, "r") as f:
                        edited_message = f.read().strip()

                    # Clean up
                    os.unlink(temp_file)

                    if edited_message:
                        print(f"\n✅ Updated commit message:")
                        print("-" * 30)
                        print(edited_message)
                        print("-" * 30)
                        return edited_message
                    else:
                        print("❌ Commit message cannot be empty. Please try again.")

                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Fallback to simple input if editor not available
                    print(f"\nEditor '{editor}' not found. Using simple input mode.")
                    print("Enter your commit message (press Enter twice to finish):")

                    lines = []
                    while True:
                        try:
                            line = input()
                            if line == "" and lines:  # Empty line after content
                                break
                            lines.append(line)
                        except KeyboardInterrupt:
                            print("\n\n👋 Goodbye! Exiting gracefully...")
                            sys.exit(0)

                    edited_message = "\n".join(lines).strip()
                    if edited_message:
                        return edited_message
                    else:
                        print("❌ Commit message cannot be empty. Please try again.")

            elif choice == "2":
                return initial_message
            elif choice == "3":
                print("❌ Commit cancelled.")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Exiting gracefully...")
            sys.exit(0)


def confirm_commit(commit_message: str, auto_push: bool = False) -> str:
    """Confirm commit with user. Returns: 'commit', 'commit_and_push', 'edit', or 'cancel'."""
    print("\n🔍 Commit Review:")
    print("=" * 60)
    print("Commit message:")
    print("-" * 30)
    print(commit_message)
    print("-" * 30)

    if auto_push:
        return "commit_and_push"
        # print("\nOptions:")
        # print("1. ✅ Yes, commit and push")
        # print("2. ❌ No, go back to editing")
        # print("3. 🚪 Cancel")

        # while True:
        #     try:
        #         choice = input("\nEnter choice (1-3): ").strip()

        #         if choice == "1":
        #             return "commit_and_push"
        #         elif choice == "2":
        #             return "edit"
        #         elif choice == "3":
        #             print("❌ Commit cancelled.")
        #             sys.exit(0)
        #         else:
        #             print("❌ Invalid choice. Please enter 1, 2, or 3.")
        #     except KeyboardInterrupt:
        #         print("\n\n👋 Goodbye! Exiting gracefully...")
        #         sys.exit(0)
    else:
        print("\nOptions:")
        print("1. ✅ Yes, commit")
        print("2. 🚀 Yes, commit and push")
        print("3. ❌ No, go back to editing")
        print("4. 🚪 Cancel")

        while True:
            try:
                choice = input("\nEnter choice (1-4): ").strip()

                if choice == "1":
                    return "commit"
                elif choice == "2":
                    return "commit_and_push"
                elif choice == "3":
                    return "edit"
                elif choice == "4":
                    print("❌ Commit cancelled.")
                    sys.exit(0)
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Exiting gracefully...")
                sys.exit(0)


def interactive_file_selection() -> List[str]:
    """Interactive file selection for staging with arrow keys."""
    if not is_git_repository():
        print("❌ Not in a git repository. Please run this command in a git repository.")
        sys.exit(1)

    # Get modified files
    modified_files = get_modified_files()

    if not modified_files:
        print("📁 No modified files found.")
        print("💡 Make some changes to files first, then run commit-gen again.")
        return []

    # Get already staged files
    staged_files = get_staged_files()

    # Sort files alphabetically for simple navigation
    modified_files.sort(key=lambda x: x["filename"])

    # Prepare simple file list
    display_files = []
    file_to_display_index = {}

    for i, file_info in enumerate(modified_files):
        filename = file_info["filename"]
        status = file_info["status"]

        # Get additional file info
        file_details = get_file_info(filename)

        # Add to display_files list
        display_files.append(
            {
                "display_index": i,
                "filename": filename,
                "status": status,
                "size": file_details["size"],
                "staged": filename in staged_files,
            }
        )
        file_to_display_index[filename] = i

    # Initialize selection state
    selected_files = set()
    current_index = 0

    # Auto-select already staged files
    for filename in staged_files:
        if filename in file_to_display_index:
            selected_files.add(filename)

    while True:
        clear_screen()

        print("📁 Files to commit:")
        print("=" * 60)
        print("Use ↑/↓ to navigate, SPACE to toggle, ENTER to confirm")
        print("a=select all, n=select none, s=skip (stage all), q=quit")
        print()

        # Display files in simple list
        for i, file_info in enumerate(display_files):
            filename = file_info["filename"]
            status = file_info["status"]
            size = file_info["size"]

            # Check if selected
            is_selected = filename in selected_files
            checkbox = "[x]" if is_selected else "[ ]"

            # Check if current selection
            cursor = "→" if i == current_index else " "

            # Check if already staged
            staged_marker = " ✅" if filename in staged_files else ""

            print(f"{cursor} {checkbox} {filename} ({status}, {size}){staged_marker}")

        print()

        # Show selection summary
        selected_count = len(selected_files)
        total_count = len(display_files)
        print(f"Selected: {selected_count}/{total_count} files")
        print()

        # Get user input
        key = get_key()

        if key == "UP":
            current_index = max(0, current_index - 1)
        elif key == "DOWN":
            current_index = min(len(display_files) - 1, current_index + 1)
        elif key == "SPACE":
            # Toggle selection
            current_file = display_files[current_index]["filename"]
            if current_file in selected_files:
                selected_files.remove(current_file)
            else:
                selected_files.add(current_file)
        elif key == "SELECT_ALL":
            # Select all files
            selected_files = set(file["filename"] for file in display_files)
        elif key == "SELECT_NONE":
            # Select none (use already staged)
            if staged_files:
                selected_files = set(staged_files)
            else:
                selected_files = set()
        elif key == "SKIP":
            # Skip selection - stage all files
            all_file_names = [file["filename"] for file in display_files]
            print(f"✅ Skipping selection - staging all {len(all_file_names)} files")
            return all_file_names
        elif key == "QUIT":
            print("👋 Goodbye!")
            sys.exit(0)
        elif key == "ENTER":
            # Confirm selection
            if selected_files:
                selected_list = list(selected_files)
                print(f"✅ Selected {len(selected_list)} files")
                return selected_list
            else:
                print("❌ No files selected. Please select at least one file.")
                input("Press Enter to continue...")

    return []


def print_config():
    """Print current configuration."""
    config = get_current_config()

    print("🔧 Current Configuration")
    print("=" * 50)
    print(f"Provider: {config['provider_name']} ({config['provider']})")
    print(f"Model: {config['model']}")
    print(f"Base URL: {config['base_url']}")
    print(f"API Key: {'✅ Set' if config['api_key_set'] else '❌ Not set'}")
    print(f"Custom Prompt: {'✅ Set' if config['custom_prompt_set'] else '❌ Not set'}")
    print()


def print_providers():
    """Print available providers."""
    providers = list_providers()

    print("🤖 Available Providers")
    print("=" * 50)
    for i, (key, provider) in enumerate(providers.items(), 1):
        print(f"{i}. {provider['name']}")
        print(f"   Description: {provider['description']}")
        print(f"   Default Model: {provider['default_model']}")
        print(f"   Requires API Key: {'Yes' if provider['requires_api_key'] else 'No'}")
        print()


def interactive_setup():
    """Interactive setup wizard."""
    try:
        print("🤖 Commit-Gen Setup Wizard")
        print("=" * 50)

        # Show current config
        config = get_current_config()
        print(f"Current provider: {config['provider_name']}")
        print()

        # Show available providers
        providers = list_providers()
        provider_keys = list(providers.keys())

        print("Available providers:")
        for i, (key, provider) in enumerate(providers.items(), 1):
            print(f"{i}. {provider['name']} - {provider['description']}")

        # Get provider choice
        while True:
            try:
                choice = input(f"\nSelect provider (1-{len(providers)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(providers):
                    selected_provider = provider_keys[choice_idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Exiting gracefully...")
                sys.exit(0)

        provider_info = providers[selected_provider]
        print(f"\nSetting up {provider_info['name']}...")

        # Set provider
        save_provider(selected_provider)
        save_base_url(provider_info["base_url"])

        # Clear existing model to avoid conflicts
        save_model("")

        # Handle model configuration
        default_model = provider_info["default_model"]
        print(f"\n📋 Model Configuration")
        print(f"Default model: {default_model}")

        while True:
            try:
                model_choice = input(f"Use default model '{default_model}'? (y/n): ").strip().lower()
                if model_choice in ["y", "yes"]:
                    save_model(default_model)
                    print(f"✅ Using default model: {default_model}")
                    break
                elif model_choice in ["n", "no"]:
                    while True:
                        try:
                            custom_model = input(f"Enter custom model name: ").strip()
                            if custom_model:
                                save_model(custom_model)
                                print(f"✅ Using custom model: {custom_model}")
                                break
                            else:
                                print("❌ Model name cannot be empty. Please try again.")
                        except KeyboardInterrupt:
                            print("\n\n👋 Goodbye! Exiting gracefully...")
                            sys.exit(0)
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Exiting gracefully...")
                sys.exit(0)

        # Handle base URL for custom provider
        if selected_provider == "custom":
            print(f"\n🌐 Base URL Configuration")
            print(f"Default base URL: {provider_info['base_url']}")

            while True:
                try:
                    url_choice = input(f"Use default base URL '{provider_info['base_url']}'? (y/n): ").strip().lower()
                    if url_choice in ["y", "yes"]:
                        save_base_url(provider_info["base_url"])
                        print(f"✅ Using default base URL: {provider_info['base_url']}")
                        break
                    elif url_choice in ["n", "no"]:
                        while True:
                            try:
                                custom_url = input(f"Enter custom base URL: ").strip()
                                if custom_url:
                                    if custom_url.startswith(("http://", "https://")):
                                        save_base_url(custom_url)
                                        print(f"✅ Using custom base URL: {custom_url}")
                                        break
                                    else:
                                        print("❌ URL must start with http:// or https://")
                                else:
                                    print("❌ Base URL cannot be empty. Please try again.")
                            except KeyboardInterrupt:
                                print("\n\n👋 Goodbye! Exiting gracefully...")
                                sys.exit(0)
                        break
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye! Exiting gracefully...")
                    sys.exit(0)

        # Handle API key if required
        if provider_info["requires_api_key"]:
            print(f"\n🔑 API Key Configuration")
            try:
                api_key = getpass.getpass(f"Enter your {provider_info['name']} API key: ").strip()
                if api_key:
                    save_api_key(api_key)
                    print("✅ API key saved successfully!")
                else:
                    print("❌ API key cannot be empty.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Exiting gracefully...")
                sys.exit(0)

        print("\n✅ Setup completed successfully!")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Exiting gracefully...")
        sys.exit(0)


def set_provider_command(provider: str):
    """Set provider via command line."""
    if not validate_provider(provider):
        print(f"Error: Invalid provider '{provider}'")
        print("Available providers:")
        for key, info in PROVIDERS.items():
            print(f"  - {key}: {info['name']}")
        sys.exit(1)

    provider_info = PROVIDERS[provider]
    save_provider(provider)
    save_base_url(provider_info["base_url"])

    # Clear existing model to avoid conflicts
    save_model("")

    # Don't automatically set model - let user decide
    print(f"✅ Provider set to {provider_info['name']}")
    print(f"Base URL: {provider_info['base_url']}")
    print(f"Default model: {provider_info['default_model']}")

    # Check if model is already set
    current_model = get_model()
    if current_model:
        print(f"Current model: {current_model}")
    else:
        print(f"Model not set. Use default or set custom model:")
        print(f"  commit-gen --set-model {provider_info['default_model']}")

    if provider_info["requires_api_key"]:
        current_api_key = get_api_key()
        if current_api_key:
            print(f"API Key: ✅ Set")
        else:
            print(f"⚠️  Don't forget to set your API key: commit-gen set-api-key YOUR_KEY")


def set_api_key_command(api_key: str):
    """Set API key via command line."""
    if not api_key:
        # If no API key provided via command line, prompt securely
        api_key = getpass.getpass("Enter your API key: ").strip()
        if not api_key:
            print("❌ No API key provided.")
            return

    save_api_key(api_key)
    print("✅ API key saved")


def set_model_command(model: str):
    """Set model via command line."""
    save_model(model)
    print(f"✅ Model set to {model}")


def set_base_url_command(base_url: str):
    """Set base URL via command line."""
    save_base_url(base_url)
    print(f"✅ Base URL set to {base_url}")


def process_commit_with_confirmation(
    provider: str, api_key: str, model: str, custom_prompt: Optional[str], auto_push: bool = False
):
    """Process commit generation with confirmation steps."""
    from .core import generate_commit_message
    from .git_utils import get_git_diff

    print("🤖 Generating commit message...")

    # Get git diff content
    diff_content = get_git_diff()
    if not diff_content:
        print("❌ No changes found to commit.")
        sys.exit(1)

    # Generate commit message
    commit_message = generate_commit_message(provider, api_key, model, custom_prompt, diff_content)

    if not commit_message:
        print("❌ Failed to generate commit message.")
        sys.exit(1)

    if auto_push:
        final_message = commit_message
    else:
        # Allow user to edit commit message
        final_message = edit_commit_message(commit_message)

    # Confirm commit
    while True:
        choice = confirm_commit(final_message, auto_push)

        if choice == "commit" or choice == "commit_and_push":
            # Perform commit
            try:
                create_git_commit(final_message)
                print("✅ Commit successful!")

                # Handle push if requested
                if choice == "commit_and_push" or auto_push:
                    print("🚀 Pushing to remote...")
                    push_to_origin()
                    print("✅ Push successful!")
                else:
                    print("💡 To push changes, run: git push")

                break
            except Exception as e:
                print(f"❌ Commit failed: {str(e)}")
                sys.exit(1)
        elif choice == "edit":
            # Go back to editing
            final_message = edit_commit_message(final_message)
        else:
            # Should not reach here, but just in case
            print("❌ Invalid choice.")
            sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    try:
        parser = argparse.ArgumentParser(description="Generate commit messages using AI.")

        # Main functionality
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument("--push", action="store_true", help="Push changes after commit", default=False)
        parser.add_argument("--changelog", action="store_true", help="Generate a changelog")
        parser.add_argument("--change-log", action="store_true", help="Generate a changelog (legacy option)")
        parser.add_argument(
            "--compare-branch", default="master", help="Branch to compare against when generating changelog"
        )
        parser.add_argument("--changelog-file", default="CHANGELOG.md", help="Filename for the changelog")
        parser.add_argument("--compare-tag", help="Tag to compare against when generating changelog")
        parser.add_argument("--from-tag", help="Starting tag for comparison (use with --to-tag)")
        parser.add_argument("--to-tag", help="Ending tag for comparison (use with --from-tag)")

        # File selection options
        parser.add_argument("--all", action="store_true", help="Stage all files (default behavior)")
        parser.add_argument("--files", nargs="+", help="Stage specific files")
        parser.add_argument("--interactive", action="store_true", help="Interactive file selection")

        # Configuration commands
        parser.add_argument("--setup", action="store_true", help="Interactive setup wizard")
        parser.add_argument("--config", action="store_true", help="Show current configuration")
        parser.add_argument("--providers", action="store_true", help="Show available providers")

        # Provider and model settings
        parser.add_argument("--set-provider", help="Set provider (openrouter, ollama, gemini, mistral, custom)")
        parser.add_argument("--set-api-key", nargs="?", const="", help="Set API key (leave empty for secure input)")
        parser.add_argument("--set-model", help="Set model name")
        parser.add_argument("--set-base-url", help="Set base URL for custom provider")

        # Legacy options (for backward compatibility)
        parser.add_argument("--provider", choices=list(PROVIDERS.keys()), help="Set the provider (legacy)")
        parser.add_argument("--model", help="Set the model name (legacy)")
        parser.add_argument("--api-key", help="Set the API key (legacy)")
        parser.add_argument("--base-url", help="Set the base URL for custom provider (legacy)")
        parser.add_argument("--prompt", help="Set a custom prompt")
        parser.add_argument("--save-prompt", help="Save custom prompt to file")

        # Prompt options
        parser.add_argument("--prompt-file", help="Load custom prompt from file")
        parser.add_argument("--save-prompt-file", help="Save current prompt to file")

        # Legacy provider flags
        parser.add_argument("--use-ollama", action="store_true", help="Use Ollama as the provider (legacy)")
        parser.add_argument("--use-openrouter", action="store_true", help="Use OpenRouter as the provider (legacy)")
        parser.add_argument("--use-custom", action="store_true", help="Use custom provider with base URL (legacy)")

        args = parser.parse_args()

        # Set debug mode
        global DEBUG
        DEBUG = args.debug

        # Handle configuration commands
        if args.config:
            print_config()
            return

        if args.providers:
            print_providers()
            return

        if args.setup:
            interactive_setup()
            return

        # Handle new configuration commands
        if args.set_provider:
            set_provider_command(args.set_provider)
            return

        if args.set_api_key is not None:
            set_api_key_command(args.set_api_key)
            return

        if args.set_model:
            set_model_command(args.set_model)
            return

        if args.set_base_url:
            set_base_url_command(args.set_base_url)
            return

        # Handle changelog generation
        if args.changelog:
            generate_changelog_by_commit_sha(args.compare_branch, args.changelog_file)
            return
        if args.compare_tag:
            if args.from_tag and args.to_tag:
                from .core import generate_changelog_between_tags

                generate_changelog_between_tags(args.from_tag, args.to_tag, args.changelog_file)
                return
            elif not args.from_tag or not args.to_tag:
                print("❌ Both --from-tag and --to-tag must be specified together")
                sys.exit(1)

        # Ensure configuration directory exists
        ensure_config_dir()

        # Handle legacy provider changes
        if args.use_ollama:
            set_provider_command("ollama")
        elif args.use_openrouter:
            set_provider_command("openrouter")
        elif args.use_custom:
            if not args.base_url:
                print("Error: --base-url is required when using --use-custom")
                sys.exit(1)
            set_provider_command("custom")
            set_base_url_command(args.base_url)

        # Handle legacy model change
        if args.model:
            set_model_command(args.model.strip('"'))

        # Handle legacy API key change
        if args.api_key:
            set_api_key_command(args.api_key)

        # Handle custom prompt
        custom_prompt = None

        # Handle prompt file operations
        if args.save_prompt_file:
            try:
                current_prompt = get_prompt()
                if current_prompt:
                    with open(args.save_prompt_file, "w") as f:
                        f.write(current_prompt)
                    print(f"✅ Current prompt saved to {args.save_prompt_file}")
                else:
                    print("❌ No current prompt to save")
            except Exception as e:
                print(f"❌ Error saving prompt to file: {str(e)}")
                sys.exit(1)
            return

        # Load prompt from file
        if args.prompt_file:
            try:
                with open(args.prompt_file, "r") as f:
                    custom_prompt = f.read().strip()
                print(f"✅ Loaded custom prompt from {args.prompt_file}")
            except FileNotFoundError:
                print(f"❌ Prompt file not found: {args.prompt_file}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Error reading prompt file: {str(e)}")
                sys.exit(1)
        # Legacy prompt handling
        elif args.save_prompt:
            try:
                with open(args.save_prompt, "r") as f:
                    prompt_content = f.read()
                    save_prompt(prompt_content)
                    print(f"Custom prompt saved from {args.save_prompt}")
            except Exception as e:
                print(f"Error reading prompt file: {str(e)}")
                sys.exit(1)
        elif args.prompt:
            custom_prompt = args.prompt

        # Handle file staging
        files_staged = False

        if args.files:
            # Stage specific files
            stage_specific_files(args.files)
            files_staged = True
        elif args.interactive:
            # Interactive file selection
            selected_files = interactive_file_selection()
            if selected_files:
                stage_specific_files(selected_files)
                files_staged = True
        elif args.all:
            # Stage all files (legacy behavior)
            from .git_utils import stage_all_changes

            stage_all_changes()
            print("✅ Staged all files")
            files_staged = True
        else:
            # Default: interactive file selection
            selected_files = interactive_file_selection()
            if selected_files:
                stage_specific_files(selected_files)
                files_staged = True

        # Check if any files were successfully staged
        if not files_staged:
            print("❌ No files were staged. Please check your file selection.")
            sys.exit(1)

        # Get configuration
        provider = get_provider()
        api_key = get_api_key()
        model = get_model()

        # Set default model based on provider only if no model is set
        if not model:
            model = get_default_model_for_provider(provider)
            debug_log(f"Using default model for {provider}: {model}")
        else:
            debug_log(f"Using custom model: {model}")

        debug_log(f"Using provider: {provider}")
        debug_log(f"Using model: {model}")

        # Check for API key if required
        if provider_requires_api_key(provider) and not api_key:
            print(f"No API key found for {provider}. Please set it using:")
            print(f"commit-gen set-api-key YOUR_API_KEY")
            print(f"Or run: commit-gen setup")
            sys.exit(1)

        # Check Ollama if using it
        if provider == "ollama":
            check_ollama()

        # Process commit generation with confirmation
        process_commit_with_confirmation(provider, api_key, model, custom_prompt, args.push)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        if DEBUG:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
