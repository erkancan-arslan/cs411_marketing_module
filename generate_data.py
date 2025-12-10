"""
Mock Data Generator for Customer Segmentation Module
Generates realistic Turkish customer data for testing and demonstration purposes.
"""
import json
import random
import uuid
from pathlib import Path


# Turkish names for realistic data
FIRST_NAMES = [
    "Mehmet", "Ahmet", "Mustafa", "Ali", "Hüseyin", "Hasan", "İbrahim", "Yusuf", "Osman", "Fatma",
    "Ayşe", "Emine", "Hatice", "Zeynep", "Elif", "Meryem", "Sultan", "Özge", "Deniz", "Can",
    "Cem", "Berk", "Ege", "Doruk", "Arda", "Burak", "Emre", "Selin", "Merve", "Gizem",
    "Nur", "Yağmur", "Pınar", "Ceren", "Burcu", "Ece", "İrem", "Beste", "Begüm", "Tuğba"
]

LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Aydın", "Öztürk", "Arslan", "Doğan", "Kılıç",
    "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özdemir", "Şimşek", "Erdoğan", "Aksoy", "Yıldız",
    "Yıldırım", "Özer", "Acar", "Güneş", "Polat", "Uzun", "Aydin", "Bulut", "Tekin", "Ünal"
]

# Turkish cities as specified
CITIES = ["Ankara", "Istanbul", "Izmir", "Bursa", "Antalya", "Adana", "Gaziantep", "Konya"]

# Email domains
EMAIL_DOMAINS = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "mynet.com"]


def generate_customer():
    """Generate a single realistic customer record."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate email based on name
    email_prefix = f"{first_name.lower()}.{last_name.lower()}"
    # Remove Turkish characters for email
    email_prefix = email_prefix.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u')
    email_prefix = email_prefix.replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    email = f"{email_prefix}{random.randint(1, 999)}@{random.choice(EMAIL_DOMAINS)}"
    
    # Generate customer data
    customer = {
        "id": str(uuid.uuid4()),
        "name": f"{first_name} {last_name}",
        "email": email,
        "city": random.choice(CITIES),
        "age": random.randint(18, 65),
        "spending_score": random.randint(1, 100),
        "total_spent": round(random.uniform(100.0, 50000.0), 2),
        "is_active": random.choice([True, True, True, False])  # 75% active
    }
    
    return customer


def generate_customers(count=50):
    """
    Generate multiple customer records.
    
    Args:
        count: Number of customers to generate (default: 50)
    
    Returns:
        List of customer dictionaries
    """
    customers = []
    
    # Ensure good distribution across cities
    customers_per_city = count // len(CITIES)
    
    for city in CITIES:
        for _ in range(customers_per_city):
            customer = generate_customer()
            customer["city"] = city  # Ensure even distribution
            customers.append(customer)
    
    # Generate remaining customers randomly
    remaining = count - len(customers)
    for _ in range(remaining):
        customers.append(generate_customer())
    
    # Shuffle to mix cities
    random.shuffle(customers)
    
    return customers


def save_customers_to_json(customers, file_path="data/customers.json"):
    """
    Save generated customers to a JSON file.
    
    Args:
        customers: List of customer dictionaries
        file_path: Path where to save the JSON file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {len(customers)} customers and saved to {file_path}")


def main():
    """Main execution function."""
    print("🚀 Starting customer data generation...")
    
    # Generate 50 customers
    customers = generate_customers(50)
    
    # Save to JSON file
    save_customers_to_json(customers)
    
    # Display statistics
    print(f"\n📊 Statistics:")
    print(f"   Total customers: {len(customers)}")
    print(f"   Active customers: {sum(1 for c in customers if c['is_active'])}")
    print(f"   Inactive customers: {sum(1 for c in customers if not c['is_active'])}")
    
    # Show distribution by city
    print(f"\n🌆 Distribution by city:")
    for city in CITIES:
        count = sum(1 for c in customers if c['city'] == city)
        print(f"   {city}: {count} customers")
    
    print(f"\n✨ First 2 customer records:")
    for i, customer in enumerate(customers[:2], 1):
        print(f"\n   Customer {i}:")
        print(f"      ID: {customer['id']}")
        print(f"      Name: {customer['name']}")
        print(f"      Email: {customer['email']}")
        print(f"      City: {customer['city']}")
        print(f"      Age: {customer['age']}")
        print(f"      Spending Score: {customer['spending_score']}")
        print(f"      Total Spent: ${customer['total_spent']:.2f}")
        print(f"      Active: {customer['is_active']}")


if __name__ == "__main__":
    main()
