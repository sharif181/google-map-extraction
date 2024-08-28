import random
import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains, ScrollOrigin
from selenium.webdriver.common.by import By

from helper.scaper import Scraper


def random_sleep_seconds(seconds):
    time.sleep(random.randint(1, seconds))


def get_link(soup) -> set[str]:
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'google.com/maps/place/' in href:
            # href = href.split("?")[0]
            # href = href.split("/")[:-1]
            # href = "/".join(href)
            links.append(href)

    return list(set(links))

def scroll_to_bottom(bot, element):
    last_height = bot.driver.execute_script("return arguments[0].scrollHeight", element)
    while True:
        bot.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        random_sleep_seconds(5)  # Pause to allow the scroll to happen
        new_height = bot.driver.execute_script("return arguments[0].scrollHeight", element)
        if new_height == last_height:
            break
        last_height = new_height



def get_places_name(bot) -> set[str]:
    results = bot.find_element_by_xpath('//*[contains(translate(@aria-label, "RESULTS", "results"), "results")]')
    final_links = set()
    last_length = 0
    max_count = 3
    last_count = 0
    if results:
        button = bot.driver.find_element(By.XPATH, "//button[@role='checkbox']")
        button.click()
  
        while True:
            page_source = bot.get_page_source()
            soup = BeautifulSoup(page_source, "html.parser")
            links = get_link(soup)
            final_links.update(links)
            random_sleep_seconds(10)
            scroll_to_bottom(bot, results)
            
            if len(final_links) != last_length:
                last_length = len(final_links)

            if last_count <= max_count:
                last_count += 1
            else:
                break
        bot.driver.close()
        return final_links



def extract_name(place: str) -> str:
    try:
        # Extract the text between 'place/' and '/@'
        start_marker = "place/"
        end_marker = "/data"

        # Find the start and end positions
        start_pos = place.find(start_marker) + len(start_marker)
        end_pos = place.find(end_marker)

        # Extract the text between the markers
        extracted_text = place[start_pos:end_pos].replace("+", " ")
        return extracted_text
    except Exception as e:
        print(e)



def clean_text(address):
    if not address:
        return ""
    # Replace unwanted characters
    text = address.text.replace('\ue0c8', '')  # Remove '\ue0c8'
    text = text.replace('\ue558', '')  # Remove '\ue558'
    text = text.replace('\ue0b0\n', '')  # Remove '\ue558'
    
    # Remove extra newlines and spaces
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline
    text = text.strip()  # Remove leading and trailing whitespace
    
    return text

def extract_phone_number(phone):
    if not phone:
        return ""

    # Regular expression to extract phone number after "Phone:"
    pattern = r'Phone:\s*([\d-]+)'

    # Search for the pattern
    match_ = re.search(pattern, phone.text)

    if match_:
        phone_number = match_.group(1)
        return phone_number
    else:
        return ""

def extract_places(places):
    names = []
    phones = []
    emails = []
    addresses = []
    links = []
    # place_orders = []
    websites = []
    for place in places:
        random_sleep_seconds(20)
        place_bot = Scraper(place)
        name=extract_name(place)
        main_div = place_bot.find_element_by_xpath('//*[@jsaction="focus:scrollable.focus; blur:scrollable.blur"]')
        if main_div.is_enabled():
            ActionChains(place_bot.driver)\
                .move_to_element(main_div)\
                    .move_by_offset(0,200)\
                        .click()\
                            .perform()
        address = place_bot.find_element_by_xpath("//button[contains(@aria-label, 'Address:')]", False, 4)
        phone = place_bot.find_element_by_xpath("//button[starts-with(@data-item-id,'phone')]", False, 20)
        
        phone = clean_text(phone)
        phones.append(phone)
        addresses.append(clean_text(address))
        names.append(name)
        links.append(place)
        # place_order = place_bot.find_element_by_xpath("//a[@data-tooltip='Place an order']", False, 4)
        # if place_order:
        #     place_orders.append(clean_text(place_order.text).replace("Place an order\n", ""))
        # else:
        #     place_orders.append("")
        place_bot.driver.close()
    
    return {
        "name": names,
        "phone": phones,
        "address": addresses,
        "email": emails,
        # "place_order": place_orders,
        "website": websites,
        "links": links
    }

def call_crawler(url: str, places: str = None) -> None:
    bot = Scraper(url)
    places = get_places_name(bot)
    results = extract_places(places)
    

    

if __name__ == "__main__":
    # https://www.google.com/maps/place/The+Garden+Kitchen+at+Sheraton+Dhaka
    call_crawler("https://www.google.com/maps/search/restaurants near gulshan dhaka?hl=en")

    # data = {
    #     'https://www.google.com/maps/place/Spaghetti+Jazz,+Dhaka/data=!4m7!3m6!1s0x3755c7a6f8cab4eb:0x13f527876dcd7594!8m2!3d23.7952438!4d90.4143379!16s%2Fg%2F1ts3czt9!19sChIJ67TK-KbHVTcRlHXNbYcn9RM?authuser=0&hl=en&rclk=1', 
    #     # 'https://www.google.com/maps/place/Seasonal+Tastes/data=!4m7!3m6!1s0x3755c7b5c7fd929d:0x6ba7f3ac5654648e!8m2!3d23.7933656!4d90.4146485!16s%2Fg%2F11fkn0mzrx!19sChIJnZL9x7XHVTcRjmRUVqzzp2s?authuser=0&hl=en&rclk=1', 
    #     # 'https://www.google.com/maps/place/Sushi+Tei+Bangladesh/data=!4m7!3m6!1s0x3755c79c8f920e4f:0x308eb2981df495e2!8m2!3d23.7907102!4d90.4188492!16s%2Fg%2F11gdknh17z!19sChIJTw6Sj5zHVTcR4pX0HZiyjjA?authuser=0&hl=en&rclk=1'
    # }