import random
import re
import time

import pyautogui
import pyperclip
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



def get_places_name(bot, keyword = None, location = None) -> set[str]:
    click_continue_button(bot)

    if keyword and location:
        pyperclip.copy(f"{keyword} near {location}")
        random_sleep_seconds(2)
        pyautogui.hotkey('ctrl', 'v')
        random_sleep_seconds(2)
        pyautogui.press("enter")
    
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
        return list(final_links)



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


def click_continue_button(bot):
    # for safty
    keep_cont_btn = bot.find_element_by_xpath("//button[.//span[text()='Keep using web']]", False, 3)
    if keep_cont_btn and keep_cont_btn.is_enabled():
        print("continue button clicked")
        keep_cont_btn.click()
        random_sleep_seconds(2)


def clean_text(address):
    if not address:
        return ""
    try:
        # Replace unwanted characters
        text = address.text.replace('\ue0c8', '')  # Remove '\ue0c8'
        text = text.replace('\ue558', '')  # Remove '\ue558'
        text = text.replace('\ue0b0', '')  # Remove '\ue0b0'
        text = text.replace('\ue80b\n', '')  # Remove '\ue80b\n'
        
        # Remove extra newlines and spaces
        text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline
        text = text.strip()  # Remove leading and trailing whitespace
        
        return text
    except Exception as e:
        return ""

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
    # place_orders = []
    for place in places:
        random_sleep_seconds(10)
        place_bot = Scraper(place)

        click_continue_button(place_bot)

        name=extract_name(place)
        main_div = place_bot.find_element_by_xpath('//*[@jsaction="focus:scrollable.focus; blur:scrollable.blur"]', False, 10)
        if main_div and main_div.is_enabled():
            ActionChains(place_bot.driver)\
                .move_to_element(main_div)\
                    .move_by_offset(0,200)\
                        .click()\
                            .perform()
            address = place_bot.find_element_by_xpath("//button[contains(@aria-label, 'Address:')]", False, 4)
            phone = place_bot.find_element_by_xpath("//button[starts-with(@data-item-id,'phone')]", False, 10)
            website = place_bot.find_element_by_xpath("//a[starts-with(@data-item-id,'authority')]", False, 10)
            phone = clean_text(phone)
            address = clean_text(address)
            website = clean_text(website)
            link = place_bot.driver.current_url
            data = {
                "name": name,
                "phone": phone,
                "address": address,
                # "place_order": place_orders,
                "website": website,
                "google_map_links": link
            }
            # place_order = place_bot.find_element_by_xpath("//a[@data-tooltip='Place an order']", False, 4)
            # if place_order:
            #     place_orders.append(clean_text(place_order.text).replace("Place an order\n", ""))
            # else:
            #     place_orders.append("")
            yield data
        place_bot.driver.close()


def url_maker(keyword:str, location: str) -> str:
    return f"https://www.google.com/maps/search/{keyword} near {location}?hl=en"


def get_places(keyword: str, location: str):
    url = url_maker(keyword=keyword, location=location)
    # url = "https://www.google.com/maps/?hl=en"
    bot = Scraper(url)
    places = get_places_name(bot)
    return places


def call_crawler(places):
    results = extract_places(places)
    yield from results

    

if __name__ == "__main__":
    pass
    # call_crawler("restaurants", "Dhaka")
    # call_crawler(keyword="", location="", places=["https://www.google.com/maps/place/Spaghetti+Jazz,+Dhaka/data=!4m7!3m6!1s0x3755c7a6f8cab4eb:0x13f527876dcd7594!8m2!3d23.7952438!4d90.4143379!16s%2Fg%2F1ts3czt9!19sChIJ67TK-KbHVTcRlHXNbYcn9RM?authuser=0&hl=en&rclk=1"])
    # call_crawler("https://www.google.com/maps/search/software company near gulshan?hl=en")
    # call_crawler("https://www.google.com/maps/search/restaurants near gulshan dhaka?hl=en")

    # data = {
    #     'https://www.google.com/maps/place/Spaghetti+Jazz,+Dhaka/data=!4m7!3m6!1s0x3755c7a6f8cab4eb:0x13f527876dcd7594!8m2!3d23.7952438!4d90.4143379!16s%2Fg%2F1ts3czt9!19sChIJ67TK-KbHVTcRlHXNbYcn9RM?authuser=0&hl=en&rclk=1', 
    #     # 'https://www.google.com/maps/place/Seasonal+Tastes/data=!4m7!3m6!1s0x3755c7b5c7fd929d:0x6ba7f3ac5654648e!8m2!3d23.7933656!4d90.4146485!16s%2Fg%2F11fkn0mzrx!19sChIJnZL9x7XHVTcRjmRUVqzzp2s?authuser=0&hl=en&rclk=1', 
    #     # 'https://www.google.com/maps/place/Sushi+Tei+Bangladesh/data=!4m7!3m6!1s0x3755c79c8f920e4f:0x308eb2981df495e2!8m2!3d23.7907102!4d90.4188492!16s%2Fg%2F11gdknh17z!19sChIJTw6Sj5zHVTcR4pX0HZiyjjA?authuser=0&hl=en&rclk=1'
    # }