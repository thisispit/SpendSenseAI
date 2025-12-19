class Categorizer:
    def __init__(self):
        # Keyword to Category mapping (Rule-based AI)
        self.rules = {
            "Food & Dining": ["starbucks", "mcdonalds", "kfc", "burger king", "subway", "pizza", "restaurant", "cafe", "coffee", "baker", "supermarket", "grocer", "whole foods", "trader joes", "zomato", "swiggy", "ubereats", "doordash", "dining", "lunch", "dinner"],
            "Travel & Transport": ["uber", "lyft", "ola", "grab", "taxi", "cab", "airline", "flight", "delta", "united", "hotel", "airbnb", "expedia", "booking", "train", "metro", "bus", "transport", "fuel", "gas", "petrol", "shell", "bp"],
            "Entertainment": ["netflix", "spotify", "hulu", "prime video", "disney", "cinema", "movie", "theatre", "steam", "playstation", "xbox", "nintendo", "game", "entertainment"],
            "Shopping": ["amazon", "walmart", "target", "best buy", "apple", "nike", "zara", "h&m", "clothing", "shoe", "retail", "store", "shop", "mall"],
            "Utilities": ["electric", "water", "gas", "internet", "wifi", "phone", "mobile", "att", "verizon", "t-mobile", "bill", "insurance", "power", "utility"],
            "Income": ["salary", "payroll", "deposit", "transfer from", "refund", "cashback", "paycheck"],
            "Housing": ["rent", "mortgage", "lease", "apartment", "house"],
            "Education": ["tuition", "course", "udemy", "coursera", "school", "college", "university", "education", "book"],
            "Health & Fitness": ["gym", "fitness", "doctor", "pharmacy", "medicine", "hospital", "clinic", "health", "medicare"]
        }

    def predict(self, description: str) -> str:
        """
        Predicts the category based on the transaction description.
        """
        if not description:
            return "Uncategorized"
        
        desc_clean = description.lower()
        
        # Check rule matches
        for category, keywords in self.rules.items():
            for keyword in keywords:
                # Simple substring match
                if keyword in desc_clean:
                    return category
        
        return "Uncategorized"

# Singleton instance
categorizer = Categorizer()
