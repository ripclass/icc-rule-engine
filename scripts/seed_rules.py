#!/usr/bin/env python3
"""
Seed script to populate the database with sample UCP600 rules
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Rule, RuleType
from dotenv import load_dotenv

load_dotenv()

# Sample UCP600 rules for demonstration
SAMPLE_RULES = [
    {
        "rule_id": "UCP600-14a",
        "source": "UCP600",
        "article": "14a",
        "title": "Standard for Examination of Documents",
        "text": "A nominated bank acting on its nomination, a confirming bank, if any, and the issuing bank must examine a presentation to determine, on the basis of the documents alone, whether or not the documents appear on their face to comply with the terms and conditions of the credit.",
        "type": RuleType.AI_ASSISTED,
        "logic": None,
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-14b",
        "source": "UCP600",
        "article": "14b",
        "title": "Examination Period",
        "text": "A nominated bank acting on its nomination, a confirming bank, if any, and the issuing bank shall each have a maximum of five banking days following the day of presentation to determine if a presentation is complying.",
        "type": RuleType.CODABLE,
        "logic": "presentation_date + 5_banking_days >= examination_date",
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-18",
        "source": "UCP600",
        "article": "18",
        "title": "Commercial Invoice",
        "text": "A commercial invoice must appear to be issued by the beneficiary (except as provided in article 38), must be made out in the name of the applicant (except as provided in sub-article 38 (g)), and need not be signed.",
        "type": RuleType.AI_ASSISTED,
        "logic": None,
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-28a",
        "source": "UCP600",
        "article": "28a",
        "title": "Insurance Document Requirements",
        "text": "An insurance document, such as an insurance policy, an insurance certificate or a declaration under an open cover, must appear to be issued and signed by an insurance company, an underwriter or their agents or proxies.",
        "type": RuleType.AI_ASSISTED,
        "logic": None,
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-31",
        "source": "UCP600",
        "article": "31",
        "title": "Date of Shipment",
        "text": "Unless a credit states otherwise, banks will accept a transport document bearing a date of shipment that is not later than the latest date for shipment as specified in the credit.",
        "type": RuleType.CODABLE,
        "logic": "shipment_date <= latest_shipment_date",
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-29",
        "source": "UCP600",
        "article": "29",
        "title": "Expiry Date and Place for Presentation",
        "text": "A credit must state an expiry date for presentation of documents for payment, acceptance or negotiation. An expiry date stated for the credit will be construed to apply to all drafts drawn under and documents required by the credit.",
        "type": RuleType.CODABLE,
        "logic": "presentation_date <= expiry_date",
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-3",
        "source": "UCP600",
        "article": "3",
        "title": "Credits v. Contracts",
        "text": "Credits, by their nature, are separate transactions from the sales or other contract(s) on which they may be based. Banks are in no way concerned with or bound by such contract(s), even if any reference whatsoever to it (them) is included in the credit.",
        "type": RuleType.AI_ASSISTED,
        "logic": None,
        "version": "1.0"
    },
    {
        "rule_id": "UCP600-7a",
        "source": "UCP600",
        "article": "7a",
        "title": "Issuing Bank Undertaking",
        "text": "Provided that the stipulated documents are presented to the nominated bank or to the issuing bank and that they constitute a complying presentation, the issuing bank must honour if the credit is available by sight payment, deferred payment or acceptance with the issuing bank.",
        "type": RuleType.AI_ASSISTED,
        "logic": None,
        "version": "1.0"
    }
]

def seed_database():
    """
    Seed the database with sample UCP600 rules
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("🌱 Starting database seeding...")

        # Check if rules already exist
        existing_count = session.query(Rule).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} rules. Skipping seed.")
            return

        # Insert sample rules
        created_count = 0
        for rule_data in SAMPLE_RULES:
            # Check if rule already exists by rule_id
            existing_rule = session.query(Rule).filter(Rule.rule_id == rule_data["rule_id"]).first()
            if existing_rule:
                print(f"⚠️  Rule {rule_data['rule_id']} already exists, skipping...")
                continue

            rule = Rule(**rule_data)
            session.add(rule)
            created_count += 1
            print(f"✅ Created rule: {rule_data['rule_id']} - {rule_data['title']}")

        session.commit()
        print(f"🎉 Successfully seeded database with {created_count} rules!")

        # Print summary
        total_rules = session.query(Rule).count()
        codable_rules = session.query(Rule).filter(Rule.type == RuleType.CODABLE).count()
        ai_rules = session.query(Rule).filter(Rule.type == RuleType.AI_ASSISTED).count()

        print(f"\n📊 Database Summary:")
        print(f"   Total rules: {total_rules}")
        print(f"   Codable rules: {codable_rules}")
        print(f"   AI-assisted rules: {ai_rules}")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise e
    finally:
        session.close()

def create_sample_lc_document():
    """
    Create a sample Letter of Credit document for testing
    """
    sample_lc = {
        "document_id": "LC-TEST-001",
        "applicant": "ABC Trading Company Ltd",
        "beneficiary": "XYZ Exports Ltd",
        "amount": "100000.00",
        "currency": "USD",
        "expiry_date": "2024-12-31",
        "shipment_date": "2024-12-15",
        "presentation_date": "2024-12-20",
        "latest_shipment_date": "2024-12-30",
        "documents": [
            "Commercial Invoice",
            "Bill of Lading",
            "Insurance Certificate",
            "Certificate of Origin"
        ],
        "terms": [
            "CIF New York",
            "Partial shipments allowed",
            "Transshipment allowed"
        ],
        "description_of_goods": "Cotton T-shirts, 100% cotton, various sizes",
        "port_of_loading": "Mumbai, India",
        "port_of_discharge": "New York, USA"
    }

    # Save to file for testing
    import json
    with open("sample_lc_document.json", "w") as f:
        json.dump(sample_lc, f, indent=2)

    print("📄 Created sample LC document: sample_lc_document.json")
    return sample_lc

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed ICC Rule Engine database")
    parser.add_argument("--create-sample", action="store_true", help="Create sample LC document")
    args = parser.parse_args()

    try:
        seed_database()

        if args.create_sample:
            create_sample_lc_document()

        print("\n🚀 Ready to test the ICC Rule Engine!")
        print("📋 Next steps:")
        print("   1. Start the server: uvicorn app.main:app --reload --port 8000")
        print("   2. Visit Swagger UI: http://localhost:8000/docs")
        print("   3. Test validation: POST /validate with sample_lc_document.json")

    except Exception as e:
        print(f"💥 Seeding failed: {e}")
        sys.exit(1)