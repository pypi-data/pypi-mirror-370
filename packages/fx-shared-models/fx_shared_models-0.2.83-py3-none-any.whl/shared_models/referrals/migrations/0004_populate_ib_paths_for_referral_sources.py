# Generated migration to populate ib_path and agreement_path for existing IB referral sources

from django.db import migrations

def populate_ib_paths_for_referral_sources(apps, schema_editor):
    """
    Populate ib_path and agreement_path for existing IB referral sources.
    
    These fields track the IB hierarchy and agreement structure at the time 
    the referral code was created, ensuring proper commission distribution.
    """
    ReferralSource = apps.get_model('referrals', 'ReferralSource')
    IBHierarchy = apps.get_model('ib_commission', 'IBHierarchy')
    
    sources_to_update = []
    
    # Process all IB-type referral sources that don't have paths set
    for source in ReferralSource.objects.filter(
        source_type='IB',
        ib_path__isnull=True
    ).select_related('customer', 'agreement'):
        
        if not source.customer_id:
            continue
            
        # Get the IB hierarchy for this IB
        hierarchy = IBHierarchy.objects.filter(
            customer_id=source.customer_id
        ).first()
        
        if hierarchy:
            # Build the IB path
            ib_path_parts = []
            agreement_path_parts = []
            
            # Check if this is a single-level IB (no parent)
            if not hierarchy.parent_customer_id:
                # Single-level IB
                ib_path_parts = [str(source.customer_id)]
                
                # For agreement path, use the source's agreement or the hierarchy's default
                if source.agreement_id:
                    agreement_path_parts = [str(source.agreement_id)]
                elif hierarchy.default_agreement_id:
                    agreement_path_parts = [str(hierarchy.default_agreement_id)]
                else:
                    agreement_path_parts = ['']
            else:
                # Multi-level IB - build the full path
                # Start with the current IB
                current_ib = hierarchy
                ib_ids = []
                
                # Walk up the hierarchy to build the path
                while current_ib:
                    ib_ids.insert(0, str(current_ib.customer_id))
                    
                    if current_ib.parent_customer_id:
                        current_ib = IBHierarchy.objects.filter(
                            customer_id=current_ib.parent_customer_id
                        ).first()
                    else:
                        current_ib = None
                
                ib_path_parts = ib_ids
                
                # For agreement path, use empty strings for parents, actual agreement for the IB
                agreement_path_parts = [''] * (len(ib_ids) - 1)
                if source.agreement_id:
                    agreement_path_parts.append(str(source.agreement_id))
                elif hierarchy.default_agreement_id:
                    agreement_path_parts.append(str(hierarchy.default_agreement_id))
                else:
                    agreement_path_parts.append('')
            
            # Set the paths
            source.ib_path = '.'.join(ib_path_parts)
            source.agreement_path = '.'.join(agreement_path_parts)
            sources_to_update.append(source)
        else:
            # No hierarchy found - treat as single-level IB
            source.ib_path = str(source.customer_id)
            
            if source.agreement_id:
                source.agreement_path = str(source.agreement_id)
            else:
                source.agreement_path = ''
            
            sources_to_update.append(source)
    
    # Bulk update all referral sources
    if sources_to_update:
        ReferralSource.objects.bulk_update(
            sources_to_update, 
            ['ib_path', 'agreement_path']
        )
        print(f"Updated paths for {len(sources_to_update)} IB ReferralSource records")
    else:
        print("No IB ReferralSource records needed updating")

def reverse_populate_ib_paths(apps, schema_editor):
    """
    Reverse the population by clearing the paths.
    """
    ReferralSource = apps.get_model('referrals', 'ReferralSource')
    
    # Clear paths for IB-type referral sources
    ReferralSource.objects.filter(source_type='IB').update(
        ib_path=None,
        agreement_path=None
    )


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0003_referralsource_agreement_path_referralsource_ib_path'),
        ('ib_commission', '0012_clientibmapping_agreement_path_and_more'),  # Ensure IB fields exist
    ]

    operations = [
        migrations.RunPython(
            populate_ib_paths_for_referral_sources,
            reverse_populate_ib_paths
        ),
    ]