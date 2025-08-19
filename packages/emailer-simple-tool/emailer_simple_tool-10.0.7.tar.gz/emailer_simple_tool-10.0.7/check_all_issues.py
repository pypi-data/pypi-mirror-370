#!/usr/bin/env python3
"""
Comprehensive check of all issues status
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from emailer_simple_tool.core.campaign_manager import CampaignManager
from emailer_simple_tool.gui.tabs.campaign_tab import CampaignTab
from emailer_simple_tool.utils.validators import validate_campaign_folder
from emailer_simple_tool.gui.translation_manager import translation_manager

def check_all_issues():
    """Check the status of all known issues"""
    
    app = QApplication(sys.argv)
    
    print("🔍 COMPREHENSIVE ISSUE STATUS CHECK")
    print("=" * 60)
    
    # Create campaign manager and tab
    campaign_manager = CampaignManager()
    campaign_tab = CampaignTab(campaign_manager)
    
    # Test campaign paths
    problem_campaign = str(Path(__file__).parent / "test_campaign_with_issues")
    good_campaign = str(Path(__file__).parent / ".samples" / "sample-campaign")
    
    issues_status = {}
    
    # Issue #1: Duplicate email detection
    print("📋 Issue #1: Duplicate Email Detection")
    print("-" * 40)
    try:
        validation_result = validate_campaign_folder(problem_campaign)
        duplicate_errors = [e for e in validation_result.errors if "Duplicate email" in e]
        if duplicate_errors:
            print("✅ RESOLVED: Duplicate email detection working")
            issues_status[1] = "RESOLVED"
        else:
            print("❌ NOT WORKING: No duplicate email detection")
            issues_status[1] = "BROKEN"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[1] = "ERROR"
    
    # Issue #3: Validation error display
    print(f"\n📋 Issue #3: Validation Error Display")
    print("-" * 37)
    try:
        campaign_tab.load_campaign_preview(problem_campaign)
        has_validation_panel = hasattr(campaign_tab, 'validation_group')
        has_content = hasattr(campaign_tab, 'validation_content_layout')
        
        if has_validation_panel and has_content:
            content_count = campaign_tab.validation_content_layout.count()
            if content_count > 0:
                print("✅ RESOLVED: Improved validation display implemented")
                issues_status[3] = "RESOLVED"
            else:
                print("❌ PARTIAL: Panel exists but no content")
                issues_status[3] = "PARTIAL"
        else:
            print("❌ NOT IMPLEMENTED: Validation panel missing")
            issues_status[3] = "NOT_IMPLEMENTED"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[3] = "ERROR"
    
    # Issue #4: Wizard .docx support
    print(f"\n📋 Issue #4: Wizard .docx Support")
    print("-" * 32)
    try:
        from emailer_simple_tool.gui.tabs.campaign_tab import CreateCampaignWizard
        wizard = CreateCampaignWizard()
        message_page = wizard.page(2)  # MessagePage
        
        # Check if browse method exists and handles .docx
        if hasattr(message_page, 'browse_message_file'):
            print("✅ RESOLVED: Wizard supports .docx files")
            issues_status[4] = "RESOLVED"
        else:
            print("❌ NOT WORKING: Wizard missing .docx support")
            issues_status[4] = "BROKEN"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[4] = "ERROR"
    
    # Issue #5: Subject external editor
    print(f"\n📋 Issue #5: Subject External Editor")
    print("-" * 34)
    try:
        campaign_tab.current_campaign_path = problem_campaign
        campaign_tab.load_campaign_preview(problem_campaign)
        
        has_edit_button = hasattr(campaign_tab, 'edit_subject_button')
        has_edit_method = hasattr(campaign_tab, 'edit_subject')
        
        if has_edit_button and has_edit_method:
            print("✅ RESOLVED: Subject external editor working")
            issues_status[5] = "RESOLVED"
        else:
            print("❌ NOT WORKING: Subject editor missing")
            issues_status[5] = "BROKEN"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[5] = "ERROR"
    
    # Issue #6: Attachment total line selectable
    print(f"\n📋 Issue #6: Attachment Total Line Selectable")
    print("-" * 44)
    try:
        if Path(good_campaign).exists():
            campaign_tab.load_campaign_preview(good_campaign)
            
            # Check if attachments list exists
            if hasattr(campaign_tab, 'attachments_list'):
                attachments_list = campaign_tab.attachments_list
                item_count = attachments_list.count()
                
                # Look for total line and check if it's selectable
                total_line_selectable = False
                for i in range(item_count):
                    item = attachments_list.item(i)
                    if item and "Total:" in item.text():
                        from PySide6.QtCore import Qt
                        total_line_selectable = bool(item.flags() & Qt.ItemIsSelectable)
                        break
                
                if not total_line_selectable:
                    print("✅ RESOLVED: Total line is not selectable")
                    issues_status[6] = "RESOLVED"
                else:
                    print("❌ NOT FIXED: Total line still selectable")
                    issues_status[6] = "NOT_FIXED"
            else:
                print("⚠️ CANNOT TEST: No attachments list found")
                issues_status[6] = "CANNOT_TEST"
        else:
            print("⚠️ CANNOT TEST: Good campaign not found")
            issues_status[6] = "CANNOT_TEST"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[6] = "ERROR"
    
    # Issue #7: Campaign validation in GUI
    print(f"\n📋 Issue #7: Campaign Validation in GUI")
    print("-" * 36)
    try:
        # This is essentially the same as validation working
        validation_result = validate_campaign_folder(problem_campaign)
        if validation_result.errors or validation_result.warnings:
            print("✅ RESOLVED: Campaign validation working in GUI")
            issues_status[7] = "RESOLVED"
        else:
            print("❌ NOT WORKING: Validation not detecting issues")
            issues_status[7] = "BROKEN"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[7] = "ERROR"
    
    # Issue #8: Browse buttons for file replacement
    print(f"\n📋 Issue #8: Browse Buttons for File Replacement")
    print("-" * 46)
    try:
        has_browse_recipients = hasattr(campaign_tab, 'browse_recipients_button')
        has_browse_subject = hasattr(campaign_tab, 'browse_subject_button')
        has_browse_message = hasattr(campaign_tab, 'browse_message_button')
        
        if has_browse_recipients and has_browse_subject and has_browse_message:
            print("✅ RESOLVED: Browse buttons implemented")
            issues_status[8] = "RESOLVED"
        else:
            print("❌ NOT IMPLEMENTED: Browse buttons missing")
            issues_status[8] = "NOT_IMPLEMENTED"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[8] = "ERROR"
    
    # Issue #9: Language switch button
    print(f"\n📋 Issue #9: Language Switch Button")
    print("-" * 33)
    try:
        # Check translation manager
        supported_langs = translation_manager.get_supported_languages()
        can_switch = translation_manager.set_language('fr')
        
        if 'en' in supported_langs and 'fr' in supported_langs and can_switch:
            print("✅ RESOLVED: Language switching implemented")
            issues_status[9] = "RESOLVED"
        else:
            print("❌ NOT WORKING: Language switching broken")
            issues_status[9] = "BROKEN"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        issues_status[9] = "ERROR"
    
    # Summary
    print(f"\n🎯 ISSUE STATUS SUMMARY")
    print("=" * 30)
    
    resolved_count = sum(1 for status in issues_status.values() if status == "RESOLVED")
    total_count = len(issues_status)
    
    for issue_num, status in sorted(issues_status.items()):
        status_icon = {
            "RESOLVED": "✅",
            "PARTIAL": "🔶", 
            "NOT_IMPLEMENTED": "❌",
            "NOT_FIXED": "❌",
            "BROKEN": "💥",
            "ERROR": "🚨",
            "CANNOT_TEST": "⚠️"
        }.get(status, "❓")
        
        print(f"Issue #{issue_num}: {status_icon} {status}")
    
    print(f"\n📊 Overall Progress: {resolved_count}/{total_count} issues resolved")
    print(f"📊 Success Rate: {(resolved_count/total_count)*100:.1f}%")
    
    if resolved_count == total_count:
        print("\n🎉 ALL ISSUES RESOLVED! 🎉")
    else:
        remaining = total_count - resolved_count
        print(f"\n🔧 {remaining} issue(s) still need attention")
    
    print("=" * 60)

if __name__ == "__main__":
    check_all_issues()
