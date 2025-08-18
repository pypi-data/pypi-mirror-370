# Generated migration to populate agreement_path for existing single-level IBs

from django.db import migrations

def populate_agreement_path_for_single_level_ibs(apps, schema_editor):
    """
    Populate agreement_path for existing IBs.
    
    For single-level IBs: agreement_path = their agreement ID
    For multi-level IBs: agreement_path = empty strings with dots (e.g., "..")
    """
    ClientIBMapping = apps.get_model('ib_commission', 'ClientIBMapping')
    
    # Process all ClientIBMapping records with no agreement_path
    mappings_to_update = []
    
    for mapping in ClientIBMapping.objects.filter(agreement_path__isnull=True):
        # Check if this is a single-level IB (direct_ib == master_ib)
        if mapping.direct_ib_customer_id == mapping.master_ib_customer_id:
            # Single-level IB - set agreement_path to just the agreement ID
            if mapping.agreement_id:
                mapping.agreement_path = str(mapping.agreement_id)
                mappings_to_update.append(mapping)
        else:
            # Multi-level IB - count the levels and create empty agreement path
            # Parse the ib_path to count levels
            ib_levels = len([id for id in mapping.ib_path.split('.') if id])
            
            # Create agreement_path with empty strings (one less than levels, as last level gets the agreement)
            if ib_levels > 1:
                # Create dots for parent levels, last level gets the agreement
                empty_levels = [''] * (ib_levels - 1)
                if mapping.agreement_id:
                    empty_levels.append(str(mapping.agreement_id))
                else:
                    empty_levels.append('')
                mapping.agreement_path = '.'.join(empty_levels)
            else:
                # Just one level, use the agreement ID
                mapping.agreement_path = str(mapping.agreement_id) if mapping.agreement_id else ''
            
            mappings_to_update.append(mapping)
    
    # Bulk update all mappings
    if mappings_to_update:
        ClientIBMapping.objects.bulk_update(mappings_to_update, ['agreement_path'])
        print(f"Updated agreement_path for {len(mappings_to_update)} ClientIBMapping records")

def reverse_populate_agreement_path(apps, schema_editor):
    """
    Reverse the population by setting agreement_path back to null.
    """
    ClientIBMapping = apps.get_model('ib_commission', 'ClientIBMapping')
    IBHierarchy = apps.get_model('ib_commission', 'IBHierarchy')
    
    # Clear agreement_path
    ClientIBMapping.objects.update(agreement_path=None)
    
    # Clear default_agreement
    IBHierarchy.objects.update(default_agreement=None)


class Migration(migrations.Migration):

    dependencies = [
        ('ib_commission', '0012_clientibmapping_agreement_path_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_agreement_path_for_single_level_ibs,
            reverse_populate_agreement_path
        ),
    ]