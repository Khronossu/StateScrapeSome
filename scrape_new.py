from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


# Initialize the Chrome WebDriver
def initialize_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


# Scrape hotel price from Agoda
def agoda_scrape(driver, url):
    driver.get(url)
    try:
        price_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="StickyNavPrice"]'))
        )
        price = price_element.get_attribute("data-element-cheapest-room-price")
    except:
        price = 'N/A'
    return price


# Scrape hotel price from Booking.com
def booking_scrape(driver, booking_url):
    driver.get(booking_url)
    try:
        price_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '//td[@class="totalPrice"]'))
        )
        price = price_element.text
    except:
        try:
            price_element = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.XPATH, '//span[@class="prco-valign-middle-helper"]'))
            )
            price = price_element.text
        except:
            price = 'N/A'

    # Extract the largest numeric value from the price text
    numbers = re.findall(r'\d+', price.replace(",", ""))
    if numbers:
        price = max(map(int, numbers))
    else:
        price = 'N/A'

    return str(price)


# Main function to coordinate scraping over multiple dates
def main():
    check_in_date = input("Enter check-in date (YYYY-MM-DD): ")
    check_in_date_obj = datetime.strptime(check_in_date, '%Y-%m-%d')
    searched_date = datetime.today().strftime('%Y-%m-%d')
    # search_duration = int(input("Enter the number of days to search: "))
    search_duration = 1  # Set to 1 for testing purposes

    driver = initialize_driver()
    all_hotel_data = []

    # Iterate over the days for the search duration
    for day in range(search_duration):
        current_check_in = check_in_date_obj + timedelta(days=day)  # Update the check-in date here
        check_in_date_str = current_check_in.strftime('%Y-%m-%d')  # Format the updated check-in date
        check_out_date = (current_check_in + timedelta(days=1)).strftime('%Y-%m-%d')  # Calculate check-out date

        # Define URLs inside the loop to avoid unbound local errors
        urls = {
            "Agoda": {
                'Villa Samayra': f'https://www.agoda.com/en-gb/super-luxury-villa-on-ocean-4bhk/hotel/koh-samui-th.html?finalPriceView=1&isShowMobileAppPrice=false&cid=1919571&numberOfBedrooms=&familyMode=false&adults=6&children=0&rooms=1&maxRooms=0&checkIn={check_in_date}&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=3&showReviewSubmissionEntry=false&currencyCode=THB&isFreeOccSearch=false&tag=0002d4f2-d0b3-4684-9a42-27ea2c122dab&tspTypes=-1&los=1&searchrequestid=2ca088ea-3780-4ed9-882c-6c99f9901d1e&ds=CRif%2BLFtF1KeK97T',
                'V Villas Hua Hin': f'https://www.agoda.com/th-th/v-villa-hua-hin-mgallery_2/hotel/hua-hin-cha-am-th.html?finalPriceView=1&isShowMobileAppPrice=false&cid=1844104&numberOfBedrooms=&familyMode=false&adults=6&children=0&rooms=1&maxRooms=0&checkIn={check_in_date}&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=3&showReviewSubmissionEntry=false&currencyCode=THB&isFreeOccSearch=false&los=1&searchrequestid=0bab3f37-067a-4858-9aad-896de02c2c93&ds=v8WZcR7LXXUqJOX3',
                'SALA Samui Choengmon Beach': f'https://www.agoda.com/th-th/sala-samui-choengmon-beach/hotel/koh-samui-th.html?finalPriceView=1&isShowMobileAppPrice=false&cid=1844104&numberOfBedrooms=&familyMode=false&adults=6&children=0&rooms=1&maxRooms=0&checkIn={check_in_date}&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=3&showReviewSubmissionEntry=false&currencyCode=THB&isFreeOccSearch=false&los=1&searchrequestid=43e6cff5-3e1d-474c-835b-51111d7bce6a&ds=CIXyU97MqeYE/E5Q'
            },
            "Booking": {
                'Villa Samayra': f'https://www.booking.com/hotel/th/super-luxury-villa-on-ocean-5-bhk.th.html?aid=356980&label=gen173nr-1FCAEoggI46AdIM1gEaN0BiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAKqra65BsACAdICJGNiNzdmMjIwLTQ1YjYtNDQ4ZS1hNDhjLTM3M2VlMjQ4NGU2ZNgCBeACAQ&sid=fb556ccd1a5c759be1c2edaa5fb89c8b&all_sr_blocks=616629504_398408689_6_0_0;checkin={check_in_date};checkout={check_out_date};dest_id=900040609;dest_type=city;dist=0;group_adults=6;group_children=0;hapos=1;highlighted_blocks=616629504_398408689_6_0_0;hpos=1;matching_block_id=616629504_398408689_6_0_0;no_rooms=1;req_adults=6;req_children=0;room1=A%2CA%2CA%2CA%2CA%2CA;sb_price_type=total;sr_order=popularity;sr_pri_blocks=616629504_398408689_6_0_0__3599925;srepoch=1731329658;srpvid=1c075abb26d2047e;type=total;ucfs=1&',
                'V Villas Hua Hin': f'https://www.booking.com/hotel/th/v-villas-hua-hin.th.html?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaN0BiAEBmAEmuAEHyAEM2AEB6AEB-AEMiAIBqAIDuAKwr665BsACAdICJDQ0MDUzYTY4LTQxMmItNDBlZS1iYzFlLWRlMzFhNDViY2MzNdgCBuACAQ&sid=35dca382aab620ced18797f2996a3872&all_sr_blocks=4252811_335362730_6_2_0;checkin={check_in_date};checkout={check_out_date};dest_id=42528;dest_type=hotel;dist=0;group_adults=6;group_children=0;hapos=1;highlighted_blocks=4252811_335362730_6_2_0;hpos=1;matching_block_id=4252811_335362730_6_2_0;no_rooms=1;req_adults=6;req_children=0;room1=A%2CA%2CA%2CA%2CA%2CA;sb_price_type=total;sr_order=popularity;sr_pri_blocks=4252811_335362730_6_2_0__11849000;srepoch=1730910656;srpvid=c47b741e5a7e019d;type=total;ucfs=1&',
                'SALA Samui Choengmon Beach': f'https://www.booking.com/hotel/th/sala-samui-resort-and-spa.th.html?aid=356980&label=gog235jc-1FCAso3QFCGXNhbGEtc2FtdWktcmVzb3J0LWFuZC1zcGFIM1gDaN0BiAEBmAEmuAEHyAEM2AEB6AEB-AEMiAIBqAIDuAKJlsi5BsACAdICJDE3MzQwYzBhLWQzNzQtNGVlYS04NTEzLWRjMDNiZDQ1NTdjM9gCBuACAQ&sid=fb556ccd1a5c759be1c2edaa5fb89c8b&all_sr_blocks=4916807_88871549_6_1_0_303269;checkin={check_in_date};checkout={check_out_date};dest_id=-3406758;dest_type=city;dist=0;group_adults=6;group_children=0;hapos=1;highlighted_blocks=4916807_88871549_6_1_0_303269;hpos=1;matching_block_id=4916807_88871549_6_1_0_303269;no_rooms=1;req_adults=6;req_children=0;room1=A%2CA%2CA%2CA%2CA%2CA;sb_price_type=total;sr_order=popularity;sr_pri_blocks=4916807_88871549_6_1_0_303269_2691733;srepoch=1731332897;srpvid=893e610e1ee502b8;type=total;ucfs=1&'
            }
        }

        # Loop through Agoda URLs
        for villa_name, url in urls["Agoda"].items():
            try:
                price = agoda_scrape(driver, url)
                hotel_data = {
                    "Search Date": searched_date,
                    "Check-in Date": check_in_date_str,  # Use updated check-in date
                    "Pool Villa Name": villa_name,
                    "Agoda Price": price,
                    "Booking.com Price": 'N/A'
                }
                all_hotel_data.append(hotel_data)
            except Exception as e:
                print(f"Error scraping {villa_name} from Agoda: {e}")

        # Loop through Booking.com URLs
        for villa_name, url in urls["Booking"].items():
            try:
                divided_price = booking_scrape(driver, url)
                for data in all_hotel_data:
                    if data["Pool Villa Name"] == villa_name and data["Check-in Date"] == check_in_date_str:
                        data["Booking.com Price"] = divided_price
                        break
                else:
                    hotel_data = {
                        "Search Date": searched_date,
                        "Check-in Date": check_in_date_str,  # Use updated check-in date
                        "Pool Villa Name": villa_name,
                        "Agoda Price": 'N/A',
                        "Booking.com Price": divided_price
                    }
                    all_hotel_data.append(hotel_data)
            except Exception as e:
                print(f"Error scraping {villa_name} from Booking: {e}")

    driver.quit()

    # Save data to an Excel file after all dates have been processed
    df = pd.DataFrame(all_hotel_data)
    # xlsx_filename = f"saved_data/hotel_data_{searched_date}_{datetime.now().strftime('%H%M%S')}.xlsx"
    xlsx_filename = f"new_data/hotel_data_{searched_date}_{check_in_date}.xlsx"

    df.to_excel(xlsx_filename, index=False)
    print(f"Data saved to {xlsx_filename}")


if __name__ == "__main__":
    main()