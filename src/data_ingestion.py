import os
import logging
import pandas as pd
import numpy as np
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.products_path = os.path.join(data_dir, "products.csv")
        self.interactions_path = os.path.join(data_dir, "user_interactions.csv")
        
    def generate_sample_data(self) -> None:
        """Generates mock datasets if they do not exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 1. Generate Products
        if not os.path.exists(self.products_path):
            logger.info("Generating sample products.csv...")
            categories = ["Electronics", "Fashion", "Home & Kitchen", "Books", "Sports & Outdoors"]
            product_templates = {
                "Electronics": [
                    ("Wireless Headphones", "High-fidelity Bluetooth wireless headphones with active noise cancellation."),
                    ("Smart Watch", "Waterproof fitness tracker smart watch with heart rate monitor."),
                    ("Mechanical Keyboard", "RGB backlit mechanical keyboard with tactile blue switches."),
                    ("Bluetooth Speaker", "Portable waterproof Bluetooth speaker with 360-degree bass."),
                    ("Smartphone Gimbal", "3-axis smartphone gimbal stabilizer for stable video recording."),
                    ("4K Action Camera", "Ultra HD waterproof action camera with touch screen and stabilization."),
                    ("Wireless Charger Pad", "Fast charging Qi-compatible wireless charger pad for multiple devices."),
                    ("Noise Cancelling Earbuds", "Compact true wireless earbuds with immersive audio experience."),
                    ("Smart LED Bulb Pack", "Wi-Fi enabled color-changing smart LED bulbs compatible with assistants."),
                    ("External SSD 1TB", "High-speed portable solid state drive with USB-C connection.")
                ],
                "Fashion": [
                    ("Running Shoes", "Lightweight breathable running shoes with high arch support."),
                    ("Leather Jacket", "Classic genuine leather jacket with zip closure and pockets."),
                    ("Designer Sunglasses", "Polarized UV protection retro style designer sunglasses."),
                    ("Canvas Backpack", "Durable water-resistant canvas backpack for travel and laptop."),
                    ("Minimalist Wallet", "RFID blocking slim leather minimalist wallet for cards."),
                    ("Fleece Hoodie", "Cozy soft fleece pullover hoodie with front kangaroo pocket."),
                    ("Casual Chino Pants", "Slim-fit stretch cotton chino trousers for comfortable daily wear."),
                    ("Sports Windbreaker", "Water-resistant lightweight windbreaker jacket with hood."),
                    ("Smart Casual Blazer", "Modern tailored fit lightweight blazer for formal or casual events."),
                    ("Wool Knit Scarf", "Warm premium wool knit scarf perfect for winter styling.")
                ],
                "Home & Kitchen": [
                    ("Coffee Maker", "Programmable drip coffee maker with thermal carafe."),
                    ("Air Fryer", "Digital touch-screen air fryer oven with presets."),
                    ("Chef Knife", "Professional high-carbon stainless steel chef knife."),
                    ("Vacuum Cleaner", "Cordless stick vacuum cleaner with powerful suction."),
                    ("Scented Candle Set", "Natural soy wax scented candles gift set for home."),
                    ("Electric Kettle", "Rapid-boil stainless steel electric tea kettle with auto shut-off."),
                    ("Non-Stick Cookware Set", "Durable non-stick pots and pans set for easy cleaning."),
                    ("Memory Foam Pillow", "Ergonomic contour memory foam pillow for neck pain relief."),
                    ("Robot Vacuum Cleaner", "Self-charging robotic vacuum cleaner with smart sensor navigation."),
                    ("Air Purifier", "HEPA air purifier for home allergies, pets, and smoke control.")
                ],
                "Books": [
                    ("Sci-Fi Novel", "An epic space opera exploring artificial intelligence and humanity."),
                    ("Mystery Thriller", "A gripping psychological thriller filled with twists and turns."),
                    ("Self-Help Book", "Practical guide to building good habits and breaking bad ones."),
                    ("Recipe Book", "Easy healthy recipes for quick weekday meals."),
                    ("History Biography", "An inspiring biography of an influential historic leader."),
                    ("Fantasy Epic", "A legendary journey of magic, swords, and empires in a mystical land."),
                    ("Personal Finance Guide", "Smart strategy guide to investing, saving, and wealth creation."),
                    ("Science Explainer Book", "Accessible breakdown of quantum physics and cosmology concepts."),
                    ("Productivity Playbook", "Actionable systems to manage time and stop procrastination."),
                    ("Creative Writing Guide", "Masterclass book detailing character building and plot structures.")
                ],
                "Sports & Outdoors": [
                    ("Yoga Mat", "Eco-friendly non-slip yoga mat with carrying strap."),
                    ("Water Bottle", "Double-walled vacuum insulated stainless steel water bottle."),
                    ("Camping Tent", "Waterproof 4-person camping dome tent with rainfly."),
                    ("Adjustable Dumbbells", "Space-saving adjustable dumbbell set for home gym."),
                    ("Resistance Bands", "Set of heavy-duty latex resistance exercise bands."),
                    ("Hydration Backpack", "Lightweight running and cycling backpack with 2L water bladder."),
                    ("Sleeping Sleeping Bag", "Cold weather compact sleeping bag for camping and hiking."),
                    ("Pickleball Paddle Set", "Premium graphite pickleball paddles with replacement grips and balls."),
                    ("Trekking Poles", "Collapsible carbon fiber trekking poles with cork grips."),
                    ("Folding Camping Chair", "Heavy duty portable folding lawn chair with cup holder.")
                ]
            }
            
            product_list = []
            pid = 1001
            for cat, items in product_templates.items():
                for name, desc in items:
                    product_list.append({
                        "product_id": f"P{pid}",
                        "product_name": name,
                        "category": cat,
                        "description": desc
                    })
                    pid += 1
                    
            df_products = pd.DataFrame(product_list)
            df_products.to_csv(self.products_path, index=False)
            logger.info(f"Saved {len(df_products)} products to {self.products_path}")
            
        # 2. Generate User Interactions
        if not os.path.exists(self.interactions_path):
            logger.info("Generating sample user_interactions.csv...")
            np.random.seed(42)
            
            # Read product IDs
            df_p = pd.read_csv(self.products_path)
            pids = df_p["product_id"].tolist()
            
            num_users = 100
            num_interactions = 3000
            
            interactions = []
            for _ in range(num_interactions):
                user_id = f"U{np.random.randint(1, num_users + 1):03d}"
                product_id = np.random.choice(pids)
                
                # Simulate behavioral features
                views = int(np.random.poisson(2)) + 1
                clicks = views + int(np.random.poisson(1))
                
                # Purchase history - higher rating makes purchase more likely
                rating = float(np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0], p=[0.05, 0.1, 0.25, 0.35, 0.25]))
                purchased = 1 if (rating >= 3.0 and np.random.rand() > 0.3) else 0
                
                interactions.append({
                    "user_id": user_id,
                    "product_id": product_id,
                    "rating": rating,
                    "purchased": purchased,
                    "views": views,
                    "clicks": clicks
                })
                
            df_interactions = pd.DataFrame(interactions)
            # Remove direct duplicates to keep ratings unique per user-product
            df_interactions = df_interactions.drop_duplicates(subset=["user_id", "product_id"])
            df_interactions.to_csv(self.interactions_path, index=False)
            logger.info(f"Saved {len(df_interactions)} interactions to {self.interactions_path}")

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Loads and returns both datasets."""
        self.generate_sample_data()
        
        logger.info(f"Loading data from {self.products_path} and {self.interactions_path}...")
        df_products = pd.read_csv(self.products_path)
        df_interactions = pd.read_csv(self.interactions_path)
        
        return df_products, df_interactions

    def merge_datasets(self, df_products: pd.DataFrame, df_interactions: pd.DataFrame) -> pd.DataFrame:
        """Merges the interactions and products on product_id."""
        logger.info("Merging datasets...")
        merged_df = pd.merge(df_interactions, df_products, on="product_id", how="left")
        return merged_df

if __name__ == "__main__":
    ingestor = DataIngestion()
    products, interactions = ingestor.load_data()
    merged = ingestor.merge_datasets(products, interactions)
    print("Merged data preview:\n", merged.head())
