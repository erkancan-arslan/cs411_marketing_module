"""
Phase 2 Services Integration Test
End-to-end test verifying Segmentation, Campaign, and Email Strategy services.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.customer import Customer
from src.models.campaign import Campaign
from src.repository.json_repo import JsonRepository
from src.services.segmentation import SegmentationService
from src.services.campaign import CampaignService


def test_phase2_services():
    """
    End-to-End integration test for Phase 2 services.
    Tests the complete flow: Segmentation -> Campaign Creation -> Launch -> Verification
    """
    print("=" * 80)
    print("PHASE 2 SERVICE INTEGRATION TEST - END-TO-END FLOW")
    print("=" * 80)
    
    # =====================================================================
    # STEP 1: TEST SEGMENTATION SERVICE
    # =====================================================================
    print("\n📋 STEP 1: Testing Segmentation Service")
    print("-" * 80)
    
    # Initialize customer repository
    customer_repo = JsonRepository(
        'data/customers.json',
        Customer.from_dict,
        lambda c: c.to_dict()
    )
    
    # Initialize segmentation service
    segmentation_service = SegmentationService(customer_repo)
    
    # Test filtering by city
    print("   🔍 Filtering customers by city='Ankara'...")
    ankara_criteria = {'city': 'Ankara'}
    ankara_customers = segmentation_service.filter_customers(ankara_criteria)
    
    print(f"   ✅ Found {len(ankara_customers)} users in Ankara")
    
    # Display first few customer names for verification
    if ankara_customers:
        print(f"   📊 Sample customers:")
        for i, customer in enumerate(ankara_customers[:3], 1):
            print(f"      {i}. {customer.name} ({customer.email})")
    
    # Test with age range criteria
    print("\n   🔍 Filtering customers by city='Istanbul', age >= 30, active=True...")
    complex_criteria = {
        'city': 'Istanbul',
        'min_age': 30,
        'is_active': True
    }
    filtered_customers = segmentation_service.filter_customers(complex_criteria)
    print(f"   ✅ Found {len(filtered_customers)} users matching complex criteria")
    
    # Get segment statistics
    stats = segmentation_service.get_segment_statistics(ankara_customers)
    print(f"   📈 Ankara segment statistics:")
    print(f"      • Total Count: {stats['total_count']}")
    print(f"      • Active Count: {stats['active_count']}")
    print(f"      • Average Age: {stats['avg_age']}")
    print(f"      • Average Spending Score: {stats['avg_spending_score']}")
    
    # =====================================================================
    # STEP 2: TEST CAMPAIGN CREATION
    # =====================================================================
    print("\n📋 STEP 2: Testing Campaign Creation")
    print("-" * 80)
    
    # Initialize campaign repository
    campaign_repo = JsonRepository(
        'data/campaigns.json',
        Campaign.from_dict,
        lambda c: c.to_dict()
    )
    
    # Initialize campaign service
    campaign_service = CampaignService(campaign_repo, segmentation_service)
    
    # Create a test campaign targeting Ankara customers
    print("   🆕 Creating campaign: 'Test Campaign Phase 2'...")
    test_campaign = campaign_service.create_campaign(
        title="Test Campaign Phase 2",
        content_template="Hello {name} from {city}! This is a test campaign to verify our system works correctly. Thank you for being a valued customer!",
        target_segment_criteria=ankara_criteria
    )
    
    print(f"   ✅ Campaign created successfully!")
    print(f"      • Campaign ID: {test_campaign.id}")
    print(f"      • Title: {test_campaign.title}")
    print(f"      • Status: {test_campaign.status}")
    print(f"      • Target Criteria: {test_campaign.target_segment_criteria}")
    print(f"      • Initial Stats: {test_campaign.stats}")
    
    # =====================================================================
    # STEP 3: TEST CAMPAIGN EXECUTION (STRATEGY PATTERN)
    # =====================================================================
    print("\n📋 STEP 3: Testing Campaign Launch with Mock Email Strategy")
    print("-" * 80)
    
    print(f"   🚀 Launching campaign '{test_campaign.title}'...")
    print(f"   📧 Using Mock Email Provider (use_real_email=False)")
    print()
    
    # Launch campaign with Mock strategy
    launch_result = campaign_service.launch_campaign(
        campaign_id=test_campaign.id,
        use_real_email=False
    )
    
    print()
    print(f"   ✅ Campaign launch completed!")
    print(f"      • Success: {launch_result['success']}")
    print(f"      • Message: {launch_result['message']}")
    print(f"      • Emails Sent: {launch_result['emails_sent']}")
    print(f"      • Emails Failed: {launch_result['emails_failed']}")
    print(f"      • Target Audience Size: {launch_result['target_audience_size']}")
    
    # =====================================================================
    # STEP 4: VERIFICATION
    # =====================================================================
    print("\n📋 STEP 4: Verification - Checking Campaign Status and Statistics")
    print("-" * 80)
    
    # Retrieve the campaign again to verify persistence
    print("   🔍 Retrieving campaign from repository...")
    verified_campaign = campaign_service.get_campaign_by_id(test_campaign.id)
    
    if not verified_campaign:
        print("   ❌ ERROR: Campaign not found in repository!")
        return False
    
    print(f"   ✅ Campaign retrieved successfully")
    print(f"      • Campaign ID: {verified_campaign.id}")
    print(f"      • Status: {verified_campaign.status}")
    print(f"      • Emails Sent: {verified_campaign.stats['sent']}")
    print(f"      • Emails Opened: {verified_campaign.stats['opened']}")
    print(f"      • Emails Clicked: {verified_campaign.stats['clicked']}")
    
    # Perform assertions
    print("\n   🧪 Running Assertions...")
    
    test_passed = True
    
    # Assertion 1: Status should be 'Sent'
    if verified_campaign.status == 'Sent':
        print("   ✅ Assertion 1 PASSED: Campaign status is 'Sent'")
    else:
        print(f"   ❌ Assertion 1 FAILED: Expected 'Sent', got '{verified_campaign.status}'")
        test_passed = False
    
    # Assertion 2: Sent count should match segmentation count
    expected_count = len(ankara_customers)
    actual_count = verified_campaign.stats['sent']
    
    if actual_count == expected_count:
        print(f"   ✅ Assertion 2 PASSED: Sent count ({actual_count}) matches segmentation count ({expected_count})")
    else:
        print(f"   ❌ Assertion 2 FAILED: Expected {expected_count}, got {actual_count}")
        test_passed = False
    
    # Assertion 3: Launch result should indicate success
    if launch_result['success']:
        print("   ✅ Assertion 3 PASSED: Launch result indicates success")
    else:
        print("   ❌ Assertion 3 FAILED: Launch result indicates failure")
        test_passed = False
    
    # Assertion 4: No emails should have failed
    if launch_result['emails_failed'] == 0:
        print("   ✅ Assertion 4 PASSED: No emails failed")
    else:
        print(f"   ❌ Assertion 4 FAILED: {launch_result['emails_failed']} emails failed")
        test_passed = False
    
    # =====================================================================
    # FINAL RESULT
    # =====================================================================
    print("\n" + "=" * 80)
    if test_passed:
        print("🎉 ALL TESTS PASSED ✅")
        print("=" * 80)
        print("\n✨ Summary:")
        print(f"   • Segmentation Service: ✅ Working correctly")
        print(f"   • Campaign Service: ✅ Working correctly")
        print(f"   • Email Strategy Pattern: ✅ Mock provider functioning")
        print(f"   • Repository Pattern: ✅ Data persistence verified")
        print(f"   • End-to-End Flow: ✅ Complete integration successful")
        print("\n🚀 Phase 2 services are ready for Web UI integration!")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        print("\n⚠️  Please review the failed assertions above.")
    
    print("=" * 80)
    
    return test_passed


if __name__ == "__main__":
    success = test_phase2_services()
    sys.exit(0 if success else 1)
