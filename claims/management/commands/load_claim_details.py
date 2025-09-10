from django.core.management.base import BaseCommand
import json
import csv
from claims.models import Claim, ClaimDetail


class Command(BaseCommand):
    help = 'Load claim details data from JSON or CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the details file')
        parser.add_argument('--format', type=str, choices=['json', 'csv'], help='File format')
        parser.add_argument('--clear', action='store_true', help='Clear existing details before loading')

    def handle(self, *args, **options):
        file_path = options['file']
        file_format = options['format']
        clear_existing = options['clear']

        if not file_path:
            self.stdout.write(self.style.ERROR('Please provide a file path with --file'))
            return

        if clear_existing:
            ClaimDetail.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing claim details'))

        if file_format == 'json':
            self.load_from_json(file_path)
        elif file_format == 'csv':
            self.load_from_csv(file_path)
        else:
            self.stdout.write(self.style.ERROR('Please specify format with --format (json or csv)'))

    def load_from_json(self, file_path):
        """Load claim details from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.stdout.write(self.style.ERROR('JSON file must contain an array of claim details'))
                return

            self.process_details_data(data)
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {e}'))

    def load_from_csv(self, file_path):
        """Load claim details from CSV file"""
        try:
            details_data = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    details_data.append(row)
            
            self.process_details_data(details_data)
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {e}'))

    def process_details_data(self, details_data):
        """Process and save claim details data to database"""
        created_count = 0
        updated_count = 0
        
        for detail_data in details_data:
            try:
                # Get claim_id (could be 'claim_id' or 'id')
                claim_id = detail_data.get('claim_id') or detail_data.get('id')
                if not claim_id:
                    self.stdout.write(self.style.WARNING('Skipping detail without claim_id'))
                    continue

                # Find the corresponding claim
                try:
                    claim = Claim.objects.get(id=claim_id)
                except Claim.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Claim {claim_id} not found, skipping detail'))
                    continue

                # Create or update claim detail
                detail, created = ClaimDetail.objects.get_or_create(
                    claim=claim,
                    defaults={
                        'cpt_codes': detail_data.get('cpt_codes', ''),
                        'denial_reason': detail_data.get('denial_reason', '') or None,
                    }
                )
                
                if not created:
                    # Update existing detail
                    detail.cpt_codes = detail_data.get('cpt_codes', detail.cpt_codes)
                    detail.denial_reason = detail_data.get('denial_reason', '') or None
                    detail.save()
                    updated_count += 1
                else:
                    created_count += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error processing detail for claim {claim_id}: {e}'))
                continue

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(details_data)} claim details: {created_count} created, {updated_count} updated')
        )
