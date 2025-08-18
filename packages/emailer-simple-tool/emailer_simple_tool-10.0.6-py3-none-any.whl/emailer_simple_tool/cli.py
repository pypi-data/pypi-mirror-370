#!/usr/bin/env python3
"""
Main CLI entry point for emailer-simple-tool application.
Provides RClone-inspired command-line interface.
"""

import argparse
import sys
import os
from pathlib import Path

from .core.campaign_manager import CampaignManager
from .core.email_sender import EmailSender
from .utils.logger import setup_logger
from .utils.validators import validate_campaign_folder
from . import __version__


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='emailer-simple-tool',
        description='Personalized email campaign management tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  emailer-simple-tool config create /path/to/campaign
  emailer-simple-tool config smtp
  emailer-simple-tool config show
  emailer-simple-tool picture generate
  emailer-simple-tool picture generate project-name
  emailer-simple-tool send --dry-run
  emailer-simple-tool send --dry-run-name "final-test"
  emailer-simple-tool send
  emailer-simple-tool send --no-report
  emailer-simple-tool gui
        """
    )
    
    parser.add_argument('--version', action='version', version=f'emailer-simple-tool {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config subcommand
    config_parser = subparsers.add_parser('config', help='Campaign configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    # config create
    create_parser = config_subparsers.add_parser('create', help='Create or load a campaign')
    create_parser.add_argument('folder', help='Path to campaign folder')
    
    # config smtp
    smtp_parser = config_subparsers.add_parser('smtp', help='Configure SMTP settings')
    
    # config show
    show_parser = config_subparsers.add_parser('show', help='Show current campaign configuration')
    
    # Send subcommand
    send_parser = subparsers.add_parser('send', help='Send email campaign')
    send_parser.add_argument('--dry-run', action='store_true', help='Generate emails without sending')
    send_parser.add_argument('--dry-run-name', help='Custom name for dry run folder')
    send_parser.add_argument('--generate-report', action='store_true', default=True, help='Generate JSON report after sending (default: enabled)')
    send_parser.add_argument('--no-report', action='store_true', help='Disable report generation')
    
    # Picture generator subcommand
    picture_parser = subparsers.add_parser('picture', help='Picture generator operations')
    picture_subparsers = picture_parser.add_subparsers(dest='picture_action', help='Picture actions')
    
    # picture generate
    generate_parser = picture_subparsers.add_parser('generate', help='Generate personalized pictures')
    generate_parser.add_argument('project', nargs='?', help='Project name (optional, will prompt if not provided)')
    
    # GUI subcommand
    gui_parser = subparsers.add_parser('gui', help='Launch graphical user interface')
    
    return parser


def main():
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize campaign manager
        campaign_manager = CampaignManager()
        
        if args.command == 'config':
            return handle_config_command(args, campaign_manager)
        elif args.command == 'send':
            return handle_send_command(args, campaign_manager)
        elif args.command == 'picture':
            return handle_picture_command(args, campaign_manager)
        elif args.command == 'gui':
            return handle_gui_command(args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_config_command(args, campaign_manager):
    """Handle config subcommands."""
    if args.config_action == 'create':
        return campaign_manager.create_or_load_campaign(args.folder)
    elif args.config_action == 'smtp':
        return campaign_manager.configure_smtp()
    elif args.config_action == 'show':
        return campaign_manager.show_configuration()
    else:
        print("Available config actions: create, smtp, show")
        return 1


def handle_send_command(args, campaign_manager):
    """Handle send command."""
    if not campaign_manager.has_active_campaign():
        print("No active campaign. Use 'emailer-simple-tool config create <folder>' first.")
        return 1
    
    email_sender = EmailSender(campaign_manager.get_active_campaign())
    
    if args.dry_run:
        return email_sender.dry_run(args.dry_run_name)
    else:
        # Determine if report should be generated
        generate_report = args.generate_report and not args.no_report
        
        if not generate_report:
            print("📊 Report generation disabled")
        
        return email_sender.send_campaign(generate_report=generate_report)


def handle_picture_command(args, campaign_manager):
    """Handle picture subcommands."""
    if args.picture_action == 'generate':
        return campaign_manager.run_picture_generator(args.project)
    else:
        print("Available picture actions: generate")
        return 1


def handle_gui_command(args):
    """Handle GUI command."""
    try:
        from .gui import launch_gui
        print("🚀 Launching Emailer Simple Tool GUI...")
        return launch_gui()
    except ImportError as e:
        print("❌ GUI dependencies not available.")
        print("📦 Install GUI support with: pip install emailer-simple-tool[gui]")
        print(f"   Error details: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
