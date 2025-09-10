from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from claims.models import Claim, ClaimDetail
from decimal import Decimal
from datetime import datetime
import json
import csv
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Load claims data from JSON/CSV files for the ERISA Recovery system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON or CSV file containing claims data',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading new data',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            help='File format (json or csv)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Claim.objects.all().delete()
            User.objects.filter(username='demo_user').delete()

        # Create demo user
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@erisarecovery.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )

        # Determine file path
        file_path = options.get('file')
        if not file_path:
            # Look for default data files
            data_dir = Path(__file__).parent.parent.parent.parent / 'data'
            if data_dir.exists():
                json_file = data_dir / 'claims.json'
                csv_file = data_dir / 'claims.csv'
                if json_file.exists():
                    file_path = str(json_file)
                    file_format = 'json'
                elif csv_file.exists():
                    file_path = str(csv_file)
                    file_format = 'csv'
                else:
                    self.stdout.write(
                        self.style.WARNING('No data files found. Creating sample data...')
                    )
                    self.create_sample_data(user)
                    return
            else:
                self.stdout.write(
                    self.style.WARNING('No data directory found. Creating sample data...')
                )
                self.create_sample_data(user)
                return
        else:
            file_format = options.get('format')
            if not file_format:
                # Auto-detect format from file extension
                if file_path.endswith('.json'):
                    file_format = 'json'
                elif file_path.endswith('.csv'):
                    file_format = 'csv'
                else:
                    self.stdout.write(
                        self.style.ERROR('Cannot determine file format. Please specify --format')
                    )
                    return

        # Load data based on format
        if file_format == 'json':
            self.load_from_json(file_path, user)
        elif file_format == 'csv':
            self.load_from_csv(file_path, user)

    def load_from_json(self, file_path, user):
        """Load claims data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                claims_data = data
            elif isinstance(data, dict) and 'claims' in data:
                claims_data = data['claims']
            else:
                self.stdout.write(
                    self.style.ERROR('Invalid JSON format. Expected array of claims or object with "claims" key.')
                )
                return

            self.process_claims_data(claims_data, user)
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {e}')
            )

    def load_from_csv(self, file_path, user):
        """Load claims data from CSV file"""
        try:
            claims_data = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    claims_data.append(row)
            
            self.process_claims_data(claims_data, user)
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {e}')
            )

    def process_claims_data(self, claims_data, user):
        """Process and save claims data to database"""
        created_count = 0
        updated_count = 0
        
        for claim_data in claims_data:
            try:
                # Parse and validate data
                claim_id = str(claim_data.get('id', claim_data.get('claim_id', '')))
                if not claim_id:
                    self.stdout.write(
                        self.style.WARNING('Skipping claim without ID')
                    )
                    continue

                # Create or update claim
                claim, created = Claim.objects.get_or_create(
                    id=claim_id,
                    defaults={
                        'patient_name': claim_data.get('patient_name', ''),
                        'billed_amount': self.parse_decimal(claim_data.get('billed_amount', 0)),
                        'paid_amount': self.parse_decimal(claim_data.get('paid_amount', 0)),
                        'status': claim_data.get('status', 'Pending'),
                        'insurer_name': claim_data.get('insurer_name', ''),
                        'discharge_date': self.parse_date(claim_data.get('discharge_date', '')),
                    }
                )
                
                if not created:
                    # Update existing claim
                    claim.patient_name = claim_data.get('patient_name', claim.patient_name)
                    claim.billed_amount = self.parse_decimal(claim_data.get('billed_amount', claim.billed_amount))
                    claim.paid_amount = self.parse_decimal(claim_data.get('paid_amount', claim.paid_amount))
                    claim.status = claim_data.get('status', claim.status)
                    claim.insurer_name = claim_data.get('insurer_name', claim.insurer_name)
                    claim.discharge_date = self.parse_date(claim_data.get('discharge_date', claim.discharge_date))
                    claim.save()
                    updated_count += 1
                else:
                    created_count += 1

                # Create or update claim detail
                ClaimDetail.objects.get_or_create(
                    claim=claim,
                    defaults={
                        'cpt_codes': claim_data.get('cpt_codes', ''),
                        'denial_reason': claim_data.get('denial_reason', '') or None,
                    }
                )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing claim {claim_data.get("id", "unknown")}: {e}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(claims_data)} claims: {created_count} created, {updated_count} updated')
        )

    def parse_decimal(self, value):
        """Parse decimal value from string"""
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = value.replace('$', '').replace(',', '').strip()
            try:
                return Decimal(cleaned)
            except:
                return Decimal('0.00')
        return Decimal('0.00')

    def parse_date(self, value):
        """Parse date from string"""
        if isinstance(value, str):
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
            ]
            for fmt in date_formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return datetime.now().date()

    def create_sample_data(self, user):
        """Create sample data if no files are provided"""
        sample_claims = [
            {
                'id': '30001',
                'patient_name': 'Virginia Rhodes',
                'billed_amount': '639787.37',
                'paid_amount': '16001.57',
                'status': 'Denied',
                'insurer_name': 'United Healthcare',
                'discharge_date': '2022-12-19',
                'cpt_codes': '99204, 82947, 99406',
                'denial_reason': 'Policy terminated before service date'
            },
            {
                'id': '30002',
                'patient_name': 'Maria Chen',
                'billed_amount': '3400.00',
                'paid_amount': '0.00',
                'status': 'Denied',
                'insurer_name': 'Aetna',
                'discharge_date': '2023-07-16',
                'cpt_codes': '99213, 80053',
                'denial_reason': 'Coverage not verified at time of service'
            },
            {
                'id': '30003',
                'patient_name': 'Ravi Kumar',
                'billed_amount': '5725.00',
                'paid_amount': '2000.00',
                'status': 'Under Review',
                'insurer_name': 'Cigna',
                'discharge_date': '2023-06-30',
                'cpt_codes': '99215, 93000',
                'denial_reason': ''
            }
        ]
        
        self.process_claims_data(sample_claims, user)
        self.stdout.write(
            self.style.SUCCESS('Created sample data. Use --file to load from JSON/CSV files.')
        )

