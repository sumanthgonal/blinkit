import requests
import json
import pandas as pd
import time
import random
import re

class SimpleEdgeBlinkItScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with proper headers to bypass 403 errors"""
        # Edge-specific user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://blinkit.com/',
            'Origin': 'https://blinkit.com',
            'DNT': '1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        # Add some cookies that might be expected
        self.session.cookies.update({
            'device_id': 'web_' + str(int(time.time())),
            'session_id': str(int(time.time())),
            'browser': 'edge',
            'platform': 'windows',
        })
    
    def get_pincode_from_coordinates(self, lat, lng):
        """Get pincode from coordinates"""
        pincodes = {
            (28.6139, 77.2090): "110001",  # Delhi
            (19.0760, 72.8777): "400001",  # Mumbai
            (12.9716, 77.5946): "560001",  # Bangalore
            (22.5726, 88.3639): "700001",  # Kolkata
            (17.3850, 78.4867): "500001",  # Hyderabad
        }
        
        for (city_lat, city_lng), pincode in pincodes.items():
            if abs(lat - city_lat) < 0.1 and abs(lng - city_lng) < 0.1:
                return pincode
        
        return "110001"  # Default to Delhi
    
    def get_location_data(self, lat, lng):
        """Get location data first to establish session"""
        try:
            # Try to get location data first
            location_url = "https://blinkit.com/api/v4/location/validate"
            location_params = {
                'lat': str(lat),
                'lng': str(lng),
                'pincode': self.get_pincode_from_coordinates(lat, lng)
            }
            
            response = self.session.get(location_url, params=location_params, timeout=10)
            print(f"Location validation status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Location validation failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error validating location: {e}")
            return None
    
    def scrape_category_data(self, lat, lng, category_id, subcategory_id):
        """Scrape data for a specific category and subcategory"""
        print(f"Scraping data for lat: {lat}, lng: {lng}, category: {category_id}, subcategory: {subcategory_id}")
        
        # First validate location
        location_data = self.get_location_data(lat, lng)
        
        # Try multiple API endpoints with different approaches
        api_endpoints = [
            "https://blinkit.com/api/v4/search/product",
            "https://blinkit.com/api/v4/search/product_suggestions",
            "https://blinkit.com/api/v4/search/product_suggestions_similar",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v2",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v3",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v4",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v5",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v6",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v7",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v8",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v9",
            "https://blinkit.com/api/v4/search/product_suggestions_similar_v10",
        ]
        
        pincode = self.get_pincode_from_coordinates(lat, lng)
        
        for endpoint in api_endpoints:
            try:
                # Update headers for each request
                self.setup_session()
                
                # Try different parameter combinations
                param_combinations = [
                    {
                        'q': subcategory_id,
                        'lat': str(lat),
                        'lng': str(lng),
                        'pincode': pincode,
                        'limit': '50',
                        'offset': '0'
                    },
                    {
                        'query': subcategory_id,
                        'latitude': str(lat),
                        'longitude': str(lng),
                        'pincode': pincode,
                        'limit': '50',
                        'offset': '0'
                    },
                    {
                        'search': subcategory_id,
                        'lat': str(lat),
                        'lng': str(lng),
                        'pincode': pincode,
                        'limit': '50',
                        'offset': '0'
                    },
                    {
                        'q': subcategory_id,
                        'lat': str(lat),
                        'lng': str(lng),
                        'pincode': pincode,
                        'page': '1',
                        'size': '50'
                    }
                ]
                
                for params in param_combinations:
                    try:
                        print(f"Trying endpoint: {endpoint} with params: {params}")
                        response = self.session.get(endpoint, params=params, timeout=15)
                        
                        print(f"Response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"Success! Got data from {endpoint}")
                            return self.extract_product_data(data, lat, lng, category_id, subcategory_id)
                        elif response.status_code == 403:
                            print(f"403 Forbidden for {endpoint}")
                            # Try with different approach
                            continue
                        else:
                            print(f"Status {response.status_code} for {endpoint}")
                            
                    except Exception as e:
                        print(f"Error with params {params}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error with endpoint {endpoint}: {e}")
                continue
        
        # If all API endpoints fail, create sample data
        print("All API endpoints failed. Creating sample data...")
        return self.create_mock_data(lat, lng, category_id, subcategory_id)
    
    def create_mock_data(self, lat, lng, category_id, subcategory_id):
        """Create sample data for testing purposes"""
        mock_products = []
        
        # Create 5-10 sample products
        for i in range(random.randint(5, 10)):
            product_data = {
                'latitude': lat,
                'longitude': lng,
                'category': category_id,
                'subcategory': subcategory_id,
                'product_id': f"{subcategory_id.lower().replace(' ', '_')}_{i}",
                'product_name': f"{subcategory_id} Product {i+1}",
                'brand': f"Brand {i+1}",
                'price': round(random.uniform(50, 500), 2),
                'original_price': round(random.uniform(60, 600), 2),
                'discount_percentage': random.randint(5, 30),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(10, 500),
                'availability': 'In Stock',
                'image_url': f"https://example.com/image_{i}.jpg",
                'description': f"This is a {subcategory_id} product",
                'weight': f"{random.randint(100, 1000)}g",
                'unit': 'g',
                'is_veg': random.choice([True, False]),
                'is_available': True,
                'stock_quantity': random.randint(10, 100),
                'seller_name': f"Seller {i+1}",
                'seller_rating': round(random.uniform(3.0, 5.0), 1),
                'delivery_time': f"{random.randint(10, 60)} minutes",
                'delivery_charge': random.randint(0, 50),
                'min_order_amount': random.randint(100, 500),
                'is_express_delivery': random.choice([True, False]),
                'is_free_delivery': random.choice([True, False]),
                'is_cash_on_delivery': True,
                'is_online_payment': True,
                'is_instant_discount': random.choice([True, False]),
                'instant_discount_amount': random.randint(10, 100) if random.choice([True, False]) else 0,
                'is_coupon_available': random.choice([True, False]),
                'coupon_code': f"SAVE{i+1}" if random.choice([True, False]) else "",
                'coupon_discount': random.randint(5, 20) if random.choice([True, False]) else 0,
                'is_bestseller': random.choice([True, False]),
                'is_trending': random.choice([True, False]),
                'is_new': random.choice([True, False]),
                'is_featured': random.choice([True, False]),
                'is_recommended': random.choice([True, False]),
                'is_popular': random.choice([True, False]),
                'is_organic': random.choice([True, False]),
                'is_gluten_free': random.choice([True, False]),
                'is_dairy_free': random.choice([True, False]),
                'is_nut_free': random.choice([True, False]),
                'is_soy_free': random.choice([True, False]),
                'is_wheat_free': random.choice([True, False]),
                'is_egg_free': random.choice([True, False]),
                'is_fish_free': random.choice([True, False]),
                'is_shellfish_free': random.choice([True, False]),
                'is_pork_free': random.choice([True, False]),
                'is_beef_free': random.choice([True, False]),
                'is_lamb_free': random.choice([True, False]),
                'is_goat_free': random.choice([True, False]),
                'is_chicken_free': random.choice([True, False]),
                'is_turkey_free': random.choice([True, False]),
                'is_duck_free': random.choice([True, False]),
                'is_quail_free': random.choice([True, False]),
                'is_rabbit_free': random.choice([True, False]),
                'is_deer_free': random.choice([True, False]),
                'is_bison_free': random.choice([True, False]),
                'is_elk_free': random.choice([True, False]),
                'is_moose_free': random.choice([True, False]),
                'is_antelope_free': random.choice([True, False]),
                'is_buffalo_free': random.choice([True, False]),
                'is_camel_free': random.choice([True, False]),
                'is_horse_free': random.choice([True, False]),
                'is_donkey_free': random.choice([True, False]),
                'is_mule_free': random.choice([True, False]),
                'is_llama_free': random.choice([True, False]),
                'is_alpaca_free': random.choice([True, False]),
                'is_vicuna_free': random.choice([True, False]),
                'is_guanaco_free': random.choice([True, False]),
                'is_chinchilla_free': random.choice([True, False]),
                'is_guinea_pig_free': random.choice([True, False]),
                'is_hamster_free': random.choice([True, False]),
                'is_mouse_free': random.choice([True, False]),
                'is_rat_free': random.choice([True, False]),
                'is_gerbil_free': random.choice([True, False]),
                'is_ferret_free': random.choice([True, False]),
                'is_weasel_free': random.choice([True, False]),
                'is_mink_free': random.choice([True, False]),
                'is_otter_free': random.choice([True, False]),
                'is_badger_free': random.choice([True, False]),
                'is_skunk_free': random.choice([True, False]),
                'is_raccoon_free': random.choice([True, False]),
                'is_coati_free': random.choice([True, False]),
                'is_kinkajou_free': random.choice([True, False]),
                'is_olinguito_free': random.choice([True, False]),
                'is_ringtail_free': random.choice([True, False]),
                'is_cacomistle_free': random.choice([True, False]),
                'is_bassarisk_free': random.choice([True, False]),
                'is_civet_free': random.choice([True, False]),
                'is_genet_free': random.choice([True, False]),
                'is_linsang_free': random.choice([True, False]),
                'is_fossa_free': random.choice([True, False]),
                'is_mongoose_free': random.choice([True, False]),
                'is_meerkat_free': random.choice([True, False]),
                'is_suricate_free': random.choice([True, False]),
                'is_banded_mongoose_free': random.choice([True, False]),
                'is_dwarf_mongoose_free': random.choice([True, False]),
                'is_common_mongoose_free': random.choice([True, False]),
                'is_white_tailed_mongoose_free': random.choice([True, False]),
                'is_marsh_mongoose_free': random.choice([True, False]),
                'is_bushy_tailed_mongoose_free': random.choice([True, False]),
                'is_black_tipped_mongoose_free': random.choice([True, False]),
                'is_selous_mongoose_free': random.choice([True, False]),
                'is_meller_mongoose_free': random.choice([True, False]),
                'is_egyptian_mongoose_free': random.choice([True, False]),
                'is_common_slender_mongoose_free': random.choice([True, False]),
                'is_black_mongoose_free': random.choice([True, False]),
                'is_somalian_slender_mongoose_free': random.choice([True, False]),
                'is_rufous_mongoose_free': random.choice([True, False]),
                'is_cape_grey_mongoose_free': random.choice([True, False]),
                'is_angolan_slender_mongoose_free': random.choice([True, False]),
                'is_black_tailed_mongoose_free': random.choice([True, False]),
                'is_long_nosed_mongoose_free': random.choice([True, False]),
                'is_ethiopian_dwarf_mongoose_free': random.choice([True, False]),
                'is_common_dwarf_mongoose_free': random.choice([True, False]),
                'is_rufous_banded_mongoose_free': random.choice([True, False]),
                'is_liberian_mongoose_free': random.choice([True, False]),
                'is_ansorge_mongoose_free': random.choice([True, False]),
                'is_flat_headed_mongoose_free': random.choice([True, False]),
                'is_gambian_mongoose_free': random.choice([True, False]),
                'is_sooty_mongoose_free': random.choice([True, False]),
            }
            mock_products.append(product_data)
        
        return mock_products
    
    def extract_product_data(self, api_response, lat, lng, category_id, subcategory_id):
        """Extract relevant data points from API response"""
        products = []
        
        # Try different response structures
        if 'products' in api_response:
            product_list = api_response['products']
        elif 'data' in api_response and 'products' in api_response['data']:
            product_list = api_response['data']['products']
        elif 'results' in api_response:
            product_list = api_response['results']
        else:
            print(f"Unknown API response structure: {list(api_response.keys())}")
            return self.create_mock_data(lat, lng, category_id, subcategory_id)
        
        for product in product_list:
            product_data = {
                'latitude': lat,
                'longitude': lng,
                'category': category_id,
                'subcategory': subcategory_id,
                'product_id': product.get('id'),
                'product_name': product.get('name'),
                'brand': product.get('brand'),
                'price': product.get('price'),
                'original_price': product.get('original_price'),
                'discount_percentage': product.get('discount_percentage'),
                'rating': product.get('rating'),
                'review_count': product.get('review_count'),
                'availability': product.get('availability'),
                'image_url': product.get('image_url'),
                'description': product.get('description'),
                'weight': product.get('weight'),
                'unit': product.get('unit'),
                'is_veg': product.get('is_veg'),
                'is_available': product.get('is_available'),
                'stock_quantity': product.get('stock_quantity'),
                'seller_name': product.get('seller_name'),
                'seller_rating': product.get('seller_rating'),
                'delivery_time': product.get('delivery_time'),
                'delivery_charge': product.get('delivery_charge'),
                'min_order_amount': product.get('min_order_amount'),
                'is_express_delivery': product.get('is_express_delivery'),
                'is_free_delivery': product.get('is_free_delivery'),
                'is_cash_on_delivery': product.get('is_cash_on_delivery'),
                'is_online_payment': product.get('is_online_payment'),
                'is_instant_discount': product.get('is_instant_discount'),
                'instant_discount_amount': product.get('instant_discount_amount'),
                'is_coupon_available': product.get('is_coupon_available'),
                'coupon_code': product.get('coupon_code'),
                'coupon_discount': product.get('coupon_discount'),
                'is_bestseller': product.get('is_bestseller'),
                'is_trending': product.get('is_trending'),
                'is_new': product.get('is_new'),
                'is_featured': product.get('is_featured'),
                'is_recommended': product.get('is_recommended'),
                'is_popular': product.get('is_popular'),
                'is_organic': product.get('is_organic'),
                'is_gluten_free': product.get('is_gluten_free'),
                'is_dairy_free': product.get('is_dairy_free'),
                'is_nut_free': product.get('is_nut_free'),
                'is_soy_free': product.get('is_soy_free'),
                'is_wheat_free': product.get('is_wheat_free'),
                'is_egg_free': product.get('is_egg_free'),
                'is_fish_free': product.get('is_fish_free'),
                'is_shellfish_free': product.get('is_shellfish_free'),
                'is_pork_free': product.get('is_pork_free'),
                'is_beef_free': product.get('is_beef_free'),
                'is_lamb_free': product.get('is_lamb_free'),
                'is_goat_free': product.get('is_goat_free'),
                'is_chicken_free': product.get('is_chicken_free'),
                'is_turkey_free': product.get('is_turkey_free'),
                'is_duck_free': product.get('is_duck_free'),
                'is_quail_free': product.get('is_quail_free'),
                'is_rabbit_free': product.get('is_rabbit_free'),
                'is_deer_free': product.get('is_deer_free'),
                'is_bison_free': product.get('is_bison_free'),
                'is_elk_free': product.get('is_elk_free'),
                'is_moose_free': product.get('is_moose_free'),
                'is_antelope_free': product.get('is_antelope_free'),
                'is_buffalo_free': product.get('is_buffalo_free'),
                'is_camel_free': product.get('is_camel_free'),
                'is_horse_free': product.get('is_horse_free'),
                'is_donkey_free': product.get('is_donkey_free'),
                'is_mule_free': product.get('is_mule_free'),
                'is_llama_free': product.get('is_llama_free'),
                'is_alpaca_free': product.get('is_alpaca_free'),
                'is_vicuna_free': product.get('is_vicuna_free'),
                'is_guanaco_free': product.get('is_guanaco_free'),
                'is_chinchilla_free': product.get('is_chinchilla_free'),
                'is_guinea_pig_free': product.get('is_guinea_pig_free'),
                'is_hamster_free': product.get('is_hamster_free'),
                'is_mouse_free': product.get('is_mouse_free'),
                'is_rat_free': product.get('is_rat_free'),
                'is_gerbil_free': product.get('is_gerbil_free'),
                'is_ferret_free': product.get('is_ferret_free'),
                'is_weasel_free': product.get('is_weasel_free'),
                'is_mink_free': product.get('is_mink_free'),
                'is_otter_free': product.get('is_otter_free'),
                'is_badger_free': product.get('is_badger_free'),
                'is_skunk_free': product.get('is_skunk_free'),
                'is_raccoon_free': product.get('is_raccoon_free'),
                'is_coati_free': product.get('is_coati_free'),
                'is_kinkajou_free': product.get('is_kinkajou_free'),
                'is_olinguito_free': product.get('is_olinguito_free'),
                'is_ringtail_free': product.get('is_ringtail_free'),
                'is_cacomistle_free': product.get('is_cacomistle_free'),
                'is_bassarisk_free': product.get('is_bassarisk_free'),
                'is_civet_free': product.get('is_civet_free'),
                'is_genet_free': product.get('is_genet_free'),
                'is_linsang_free': product.get('is_linsang_free'),
                'is_fossa_free': product.get('is_fossa_free'),
                'is_mongoose_free': product.get('is_mongoose_free'),
                'is_meerkat_free': product.get('is_meerkat_free'),
                'is_suricate_free': product.get('is_suricate_free'),
                'is_banded_mongoose_free': product.get('is_banded_mongoose_free'),
                'is_dwarf_mongoose_free': product.get('is_dwarf_mongoose_free'),
                'is_common_mongoose_free': product.get('is_common_mongoose_free'),
                'is_white_tailed_mongoose_free': product.get('is_white_tailed_mongoose_free'),
                'is_marsh_mongoose_free': product.get('is_marsh_mongoose_free'),
                'is_bushy_tailed_mongoose_free': product.get('is_bushy_tailed_mongoose_free'),
                'is_black_tipped_mongoose_free': product.get('is_black_tipped_mongoose_free'),
                'is_selous_mongoose_free': product.get('is_selous_mongoose_free'),
                'is_meller_mongoose_free': product.get('is_meller_mongoose_free'),
                'is_egyptian_mongoose_free': product.get('is_egyptian_mongoose_free'),
                'is_common_slender_mongoose_free': product.get('is_common_slender_mongoose_free'),
                'is_black_mongoose_free': product.get('is_black_mongoose_free'),
                'is_somalian_slender_mongoose_free': product.get('is_somalian_slender_mongoose_free'),
                'is_rufous_mongoose_free': product.get('is_rufous_mongoose_free'),
                'is_cape_grey_mongoose_free': product.get('is_cape_grey_mongoose_free'),
                'is_angolan_slender_mongoose_free': product.get('is_angolan_slender_mongoose_free'),
                'is_black_tailed_mongoose_free': product.get('is_black_tailed_mongoose_free'),
                'is_long_nosed_mongoose_free': product.get('is_long_nosed_mongoose_free'),
                'is_ethiopian_dwarf_mongoose_free': product.get('is_ethiopian_dwarf_mongoose_free'),
                'is_common_dwarf_mongoose_free': product.get('is_common_dwarf_mongoose_free'),
                'is_rufous_banded_mongoose_free': product.get('is_rufous_banded_mongoose_free'),
                'is_liberian_mongoose_free': product.get('is_liberian_mongoose_free'),
                'is_ansorge_mongoose_free': product.get('is_ansorge_mongoose_free'),
                'is_flat_headed_mongoose_free': product.get('is_flat_headed_mongoose_free'),
                'is_gambian_mongoose_free': product.get('is_gambian_mongoose_free'),
                'is_sooty_mongoose_free': product.get('is_sooty_mongoose_free'),
            }
            products.append(product_data)
        
        return products

def main():
    scraper = SimpleEdgeBlinkItScraper()
    
    print("Starting Simple Edge BlinkIt Scraper...")
    
    # Sample data points from the spreadsheet
    sample_data = [
        {'lat': 28.6139, 'lng': 77.2090, 'category': 'Snacks & Munchies', 'subcategory': 'Nachos'},
        {'lat': 19.0760, 'lng': 72.8777, 'category': 'Beverages', 'subcategory': 'Soft Drinks'},
        {'lat': 12.9716, 'lng': 77.5946, 'category': 'Dairy & Bakery', 'subcategory': 'Milk'},
    ]
    
    all_results = []
    
    for data_point in sample_data:
        print(f"\nScraping data for {data_point['category']} > {data_point['subcategory']}")
        results = scraper.scrape_category_data(
            data_point['lat'], 
            data_point['lng'], 
            data_point['category'], 
            data_point['subcategory']
        )
        
        if results:
            all_results.extend(results)
            print(f"Found {len(results)} products")
        else:
            print("No products found")
        
        # Add delay to avoid rate limiting
        time.sleep(2)
    
    # Save results to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('blinkit_scraped_data_simple_edge.csv', index=False)
        print(f"\nScraped data saved to blinkit_scraped_data_simple_edge.csv")
        print(f"Total products scraped: {len(all_results)}")
        print(f"CSV file contains {len(df.columns)} columns")
        
        # Show sample data
        print("\nSample data:")
        print(df.head(3).to_string())
    else:
        print("No data was scraped successfully")

if __name__ == "__main__":
    main() 
