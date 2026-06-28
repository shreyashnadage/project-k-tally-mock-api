from dataclasses import dataclass, field


@dataclass
class ProductTemplate:
    name: str
    hsn_code: str
    unit: str
    rate_min: float
    rate_max: float
    gst_rate: float = 18.0


@dataclass
class SectorTemplate:
    customer_names: list[str]
    vendor_names: list[str]
    products: list[ProductTemplate]
    default_margin_pct: float = 25.0
    typical_gst_rate: float = 18.0


TEMPLATES: dict[str, SectorTemplate] = {
    "retail": SectorTemplate(
        customer_names=[
            "Ramesh Electronics", "Suresh Mobile Hub", "Priya Fashion Store", "Vijay General Stores",
            "Anand Super Market", "Krishna Textiles", "Deepak Home Appliances", "Meera Gift Centre",
            "Rajesh Footwear", "Sunita Cosmetics", "Arun Sports World", "Lakshmi Jewellers",
            "Ganesh Provisions", "Pooja Garments", "Manoj Traders", "Kavita Boutique",
            "Sanjay Electronics City", "Neha Fashion Hub", "Rohit Accessories", "Amit Lifestyle",
            "Shanti General Store", "Vikram Mobiles", "Divya Collections", "Harsh Emporium",
            "Preeti Sarees", "Kiran Electronics", "Nitin Hardware", "Swati Handicrafts",
            "Ashok Furniture Mart", "Renu Beauty Parlour",
        ],
        vendor_names=[
            "Samsung India Distributors", "LG Electronics Wholesale", "Bajaj Distributors",
            "Hindustan Unilever Ltd", "ITC Wholesale Division", "Godrej Consumer Products",
            "Titan Company Distributors", "Bata India Supply", "Asian Paints Depot",
            "Dabur India Wholesale", "Havells India Supply", "Philips India Distributors",
            "Crompton Greaves Dist.", "Whirlpool India Supply", "Voltas Distributors",
        ],
        products=[
            ProductTemplate("Samsung Galaxy A15", "8517", "Nos", 12000, 15000),
            ProductTemplate("Redmi Note 13", "8517", "Nos", 10000, 13000),
            ProductTemplate("Bajaj Mixer Grinder 750W", "8509", "Nos", 3000, 4500),
            ProductTemplate("Prestige Induction Cooktop", "8516", "Nos", 2500, 4000),
            ProductTemplate("Philips LED Bulb 9W", "8539", "Nos", 80, 150, 12.0),
            ProductTemplate("Havells Fan Ceiling 1200mm", "8414", "Nos", 1800, 2800),
            ProductTemplate("Cotton Bedsheet Double", "6302", "Nos", 500, 1200, 5.0),
            ProductTemplate("Men's Formal Shirt", "6205", "Nos", 800, 1500, 5.0),
            ProductTemplate("Sports Shoes Pair", "6404", "Nos", 1200, 3000, 18.0),
            ProductTemplate("Titan Analog Watch", "9101", "Nos", 2000, 8000),
            ProductTemplate("Surf Excel Detergent 1kg", "3402", "Kg", 120, 180),
            ProductTemplate("Tata Salt 1kg", "2501", "Kg", 20, 28, 0.0),
            ProductTemplate("Dove Soap 100g", "3401", "Nos", 45, 65),
            ProductTemplate("Colgate Toothpaste 200g", "3306", "Nos", 100, 140),
            ProductTemplate("Notebook 200 Pages", "4820", "Nos", 40, 80, 12.0),
        ],
        default_margin_pct=25.0,
        typical_gst_rate=18.0,
    ),
    "manufacturing": SectorTemplate(
        customer_names=[
            "Steel Works India Pvt Ltd", "Mahindra Auto Components", "Bharat Heavy Electricals",
            "Tata Motors Parts Div", "Kirloskar Brothers Ltd", "Larsen & Toubro Projects",
            "Ashok Leyland Spares", "Godrej Precision Engg", "Thermax Limited",
            "Siemens India Projects", "Cummins India Ltd", "SKF India Ltd",
            "Bosch Ltd Distribution", "ABB India Ltd", "Schaeffler India",
            "Praj Industries Ltd", "Kennametal India", "Elgi Equipments",
            "Grindwell Norton Ltd", "AIA Engineering Ltd",
        ],
        vendor_names=[
            "Tata Steel Distributor", "JSW Steel Supply", "Hindalco Raw Materials",
            "Vedanta Resources Supply", "NALCO Aluminium Depot", "SAIL Steel Centre",
            "Jindal Stainless Supply", "Supreme Industries Raw", "Finolex Cables Wholesale",
            "Polycab Wires Depot", "APL Apollo Tubes Supply",
        ],
        products=[
            ProductTemplate("MS Round Bar 12mm", "7214", "Kg", 55, 72),
            ProductTemplate("MS Flat Bar 50x6mm", "7216", "Kg", 58, 75),
            ProductTemplate("SS Sheet 304 2mm", "7219", "Kg", 220, 280),
            ProductTemplate("Aluminium Sheet 1mm", "7606", "Kg", 240, 320),
            ProductTemplate("Copper Wire 2.5mm", "7408", "Kg", 750, 900),
            ProductTemplate("Bearing SKF 6205", "8482", "Nos", 250, 400),
            ProductTemplate("V-Belt A68", "4010", "Nos", 180, 300),
            ProductTemplate("Hydraulic Oil 20L", "2710", "Ltr", 120, 180),
            ProductTemplate("Welding Rod 3.15mm 5kg", "8311", "Pkt", 400, 600),
            ProductTemplate("Grinding Wheel 150mm", "6805", "Nos", 120, 250),
        ],
        default_margin_pct=18.0,
        typical_gst_rate=18.0,
    ),
    "trading": SectorTemplate(
        customer_names=[
            "Patel Trading Co.", "Shah Enterprises", "Gupta & Sons", "Agarwal Distributors",
            "Mehta Brothers", "Joshi Trading Co.", "Deshmukh Wholesale", "Kulkarni Agencies",
            "Iyer & Associates", "Reddy Commercials", "Nair Trading House", "Pillai Enterprises",
            "Choudhury & Co.", "Banerjee Trading Corp", "Mukherjee Distributors",
            "Kapoor Wholesale", "Malhotra Trading Co.", "Bhatia Enterprises",
            "Sharma Commercial Corp", "Verma Agencies",
        ],
        vendor_names=[
            "National Wholesale Depot", "Central Trading Corp", "Eastern Distributors",
            "Western Supply House", "Southern Trading Agency", "Mumbai Wholesale Market",
            "Delhi Supply Network", "Kolkata Trading House", "Chennai Distributors",
            "Hyderabad Wholesale Corp", "Pune Trading Agency",
        ],
        products=[
            ProductTemplate("Basmati Rice Premium 25kg", "1006", "Bag", 1800, 2500, 5.0),
            ProductTemplate("Toor Dal 50kg", "0713", "Bag", 4500, 6000, 5.0),
            ProductTemplate("Refined Sunflower Oil 15L", "1512", "Tin", 1800, 2200, 5.0),
            ProductTemplate("Sugar Crystal 50kg", "1701", "Bag", 1800, 2200, 5.0),
            ProductTemplate("Wheat Flour Atta 50kg", "1101", "Bag", 1400, 1800, 5.0),
            ProductTemplate("Cement OPC 43 Grade", "2523", "Bag", 350, 420, 28.0),
            ProductTemplate("TMT Steel Bar 12mm", "7214", "Kg", 55, 70),
            ProductTemplate("PVC Pipe 4inch 6m", "3917", "Nos", 450, 650),
            ProductTemplate("Electrical Wire 1.5mm 90m", "8544", "Coil", 1200, 1800),
            ProductTemplate("Plywood 18mm 8x4", "4412", "Sheet", 1800, 2800),
            ProductTemplate("Paint Emulsion 20L", "3209", "Bucket", 2500, 4000),
            ProductTemplate("Tiles Ceramic 2x2 Box", "6908", "Box", 400, 800),
            ProductTemplate("Sanitary Fittings Set", "6910", "Set", 3000, 8000),
            ProductTemplate("GI Pipe 1inch 6m", "7306", "Nos", 600, 900),
            ProductTemplate("MCB Switch 32A", "8536", "Nos", 200, 400),
        ],
        default_margin_pct=15.0,
        typical_gst_rate=18.0,
    ),
    "services": SectorTemplate(
        customer_names=[
            "TechSoft Solutions Pvt Ltd", "Infosys BPO Division", "Wipro Digital Services",
            "HCL Technologies", "Mindtree Consulting", "Mphasis Services",
            "Persistent Systems", "Zensar Technologies", "KPIT Technologies",
            "Quick Heal Technologies", "Cyient Ltd", "Hexaware Technologies",
            "Coforge Ltd", "Birlasoft Ltd", "LTTS Engineering",
            "Tata Elxsi Ltd", "Happiest Minds Tech", "Sonata Software",
            "Mastek Ltd", "Sasken Technologies",
        ],
        vendor_names=[
            "AWS India Billing", "Microsoft Azure India", "Google Cloud India",
            "Adobe Software India", "Atlassian Tools India", "Slack Technologies",
            "Zoom Video India", "Freshworks India", "Zoho Corporation",
            "DigitalOcean India",
        ],
        products=[
            ProductTemplate("IT Consulting - Senior", "998314", "Hrs", 2500, 5000),
            ProductTemplate("IT Consulting - Junior", "998314", "Hrs", 1200, 2500),
            ProductTemplate("Web Development Service", "998314", "Hrs", 1500, 3000),
            ProductTemplate("Mobile App Development", "998314", "Hrs", 2000, 4000),
            ProductTemplate("Cloud Infrastructure Mgmt", "998315", "Hrs", 1800, 3500),
            ProductTemplate("Data Analytics Service", "998316", "Hrs", 2500, 5000),
            ProductTemplate("UI/UX Design Service", "998314", "Hrs", 1500, 3000),
            ProductTemplate("QA Testing Service", "998314", "Hrs", 1000, 2000),
            ProductTemplate("DevOps Consulting", "998315", "Hrs", 2000, 4000),
            ProductTemplate("Cybersecurity Audit", "998316", "Nos", 50000, 200000),
        ],
        default_margin_pct=40.0,
        typical_gst_rate=18.0,
    ),
    "pharma": SectorTemplate(
        customer_names=[
            "MedPlus Pharmacy Chain", "Apollo Pharmacy Distribution", "Wellness Forever Chain",
            "Netmeds Wholesale", "PharmEasy Distributors", "1mg Distribution Centre",
            "Practo Medical Supply", "Noble Plus Pharmacy", "Shree Medical Stores",
            "Sai Life Sciences Dist", "City Pharma Wholesale", "HealthKart Distribution",
            "Medlife Pharmacy", "Generic Aadhaar Dist", "Jan Aushadhi Depot",
            "Star Health Pharma", "Guardian Pharmacy", "Aster Pharmacy Chain",
            "Fortis Medical Supply", "Max Healthcare Pharmacy",
        ],
        vendor_names=[
            "Sun Pharma Wholesale", "Cipla Ltd Depot", "Dr Reddys Labs Supply",
            "Lupin Pharmaceuticals Dist", "Aurobindo Pharma Depot", "Torrent Pharma Supply",
            "Glenmark Pharma Depot", "Zydus Cadila Wholesale", "Alkem Labs Supply",
            "Mankind Pharma Depot", "Ipca Labs Wholesale",
        ],
        products=[
            ProductTemplate("Paracetamol 500mg Strip", "3004", "Strip", 15, 30, 12.0),
            ProductTemplate("Amoxicillin 500mg Strip", "3004", "Strip", 80, 120, 12.0),
            ProductTemplate("Omeprazole 20mg Strip", "3004", "Strip", 40, 70, 12.0),
            ProductTemplate("Metformin 500mg Strip", "3004", "Strip", 25, 50, 12.0),
            ProductTemplate("Atorvastatin 10mg Strip", "3004", "Strip", 60, 100, 12.0),
            ProductTemplate("Cetirizine 10mg Strip", "3004", "Strip", 20, 40, 12.0),
            ProductTemplate("Azithromycin 500mg Strip", "3004", "Strip", 90, 150, 12.0),
            ProductTemplate("ORS Powder Sachet", "3004", "Nos", 8, 15, 5.0),
            ProductTemplate("Dettol Antiseptic 500ml", "3808", "Nos", 180, 250),
            ProductTemplate("Surgical Mask Box 50", "6307", "Box", 150, 300, 5.0),
        ],
        default_margin_pct=20.0,
        typical_gst_rate=12.0,
    ),
    "fmcg": SectorTemplate(
        customer_names=[
            "D-Mart Wholesale", "Big Bazaar Supply", "Reliance Fresh Depot",
            "More Supermarket Dist", "Spencer's Retail Supply", "Star Bazaar Wholesale",
            "Spar Hypermarket Dist", "Nature's Basket Supply", "Easy Day Distribution",
            "Heritage Fresh Depot", "Nilgiris Dairy Dist", "Ratnadeep Supermarket",
            "Metro Cash & Carry", "Walmart India Supply", "Lulu Hypermarket Dist",
            "V-Mart Retail Supply", "Vishal Mega Mart Dist", "Aditya Birla Retail",
            "Future Retail Supply", "Trent Retail Depot",
        ],
        vendor_names=[
            "Hindustan Unilever Depot", "ITC Ltd Wholesale", "Nestle India Supply",
            "Dabur India Wholesale", "Marico Ltd Depot", "Godrej Consumer Depot",
            "Britannia Industries Dist", "Parle Products Wholesale", "Amul Dairy Depot",
            "Mother Dairy Supply", "Haldiram's Wholesale",
        ],
        products=[
            ProductTemplate("Surf Excel Detergent 1kg", "3402", "Kg", 120, 180),
            ProductTemplate("Maggi Noodles Carton", "1902", "Carton", 800, 1100, 12.0),
            ProductTemplate("Amul Butter 500g", "0405", "Nos", 250, 290, 12.0),
            ProductTemplate("Tata Tea Premium 1kg", "0902", "Kg", 350, 450, 5.0),
            ProductTemplate("Nescafe Classic 200g", "2101", "Nos", 450, 550),
            ProductTemplate("Parle-G Biscuit Carton", "1905", "Carton", 300, 450),
            ProductTemplate("Colgate Toothpaste 200g", "3306", "Nos", 100, 140),
            ProductTemplate("Clinic Plus Shampoo 1L", "3305", "Nos", 350, 450),
            ProductTemplate("Dettol Soap Pack 4", "3401", "Pack", 160, 220),
            ProductTemplate("Vim Dishwash Bar 500g", "3402", "Nos", 30, 50),
            ProductTemplate("Good Knight Liquid Refill", "3808", "Nos", 60, 90),
            ProductTemplate("Haldiram's Namkeen 1kg", "1905", "Kg", 300, 500, 12.0),
        ],
        default_margin_pct=12.0,
        typical_gst_rate=18.0,
    ),
}


def get_template(sector: str) -> SectorTemplate:
    return TEMPLATES.get(sector, TEMPLATES["trading"])
