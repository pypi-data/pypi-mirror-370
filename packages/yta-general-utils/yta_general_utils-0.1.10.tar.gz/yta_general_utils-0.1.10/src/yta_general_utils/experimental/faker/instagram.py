"""
TODO: This has to use the 'yta_web_scraper' library and
also must be in another library, not this one.

I comment it to avoid errors.
"""
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from yta_general_utils.web.scraper.chrome_scraper import go_to_and_wait_loaded, start_chrome

# import time
# import os
# import pyautogui
# import glob
# import shutil

# MESSAGE_SENDER_ME = 1
# MESSAGE_SENDER_OTHER = 2
# PROJECT_ABSOLUTE_PATH = os.getenv('PROJECT_ABSOLUTE_PATH')
# TOUSE_ABSOLUTE_PATH = os.getenv('TOUSE_ABSOLUTE_PATH')
# # TODO: Move this to .env variable
# DOWNLOADS_ABSOLUTE_PATH = 'C:/Users/dania/Downloads/'

# """
# inputs = driver.find_elements(By.TAG_NAME, 'input')
# profile1_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person1")]')
# profile2_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person2")]')
# # One checkbox below
# is_verified = driver.find_element(By.ID, 'tiktokverfied')
# time_input = driver.find_element(By.ID, 'edit-2-Clock')
# operator_input = driver.find_element(By.ID, 'iphoneoperator')
# battery_input = driver.find_element(By.ID, 'Battery_percent')
# profile1_name_input = driver.find_element(By.ID, 'profile1_name')
# date_input = driver.find_element(By.ID, 'time-profile1')
# # Two checkboxes below
# is_story_active_checkbox = driver.find_element(By.ID, 'visibleStory')
# is_online_checkbox = driver.find_element(By.ID, 'visibleOnline')
# is_online_checkbox.click()
# time.sleep(1)
# # Two radio buttons below plus one text when 'online_time_is_visible'
# online_time_or_nickname_is_hidden = driver.find_element(By.ID, 'Active_hide')
# online_time_or_nickname_is_visible = driver.find_element(By.CSS_SELECTOR, 'input#Active_show')
# online_time_or_nickname_text = driver.find_element(By.ID, 'edit-active')
# """

# def __setup(driver, name, username, profile_picture_absolute_path):
#     # TODO: Set maximum 'name' and 'username' lengths
#     __set_name(driver, name)
#     if username:
#         __set_username(driver, username)
#     __set_profile_picture(driver, profile_picture_absolute_path)

# def __set_profile_picture(driver, absolute_path):
#     element_present = EC.presence_of_element_located((By.ID, 'profileImg'))
#     element = WebDriverWait(driver, 10).until(element_present)
#     time.sleep(1)
#     element = element.find_element(By.XPATH, '..')
#     element.click()
#     time.sleep(2)
#     pyautogui.write((absolute_path).replace('/', '\\')) 
#     time.sleep(1)
#     pyautogui.press('enter')
#     time.sleep(1)

# def __activate_blue_check(driver):
#     is_verified_checkbox = driver.find_element(By.ID, 'tiktokverfied')
#     if not is_verified_checkbox.is_selected():
#         is_verified_checkbox.click()

# def __deactivate_blue_check(driver):
#     is_verified_checkbox = driver.find_element(By.ID, 'tiktokverfied')
#     if is_verified_checkbox.is_selected():
#         is_verified_checkbox.click()

# def __activate_story_active(driver):
#     is_story_active_checkbox = driver.find_element(By.ID, 'visibleStory')
#     if not is_story_active_checkbox.is_selected():
#         is_story_active_checkbox.click()

# def __deactivate_story_active(driver):
#     is_story_active_checkbox = driver.find_element(By.ID, 'visibleStory')
#     if is_story_active_checkbox.is_selected():
#         is_story_active_checkbox.click()

# def __activate_is_online(driver):
#     is_online_checkbox = driver.find_element(By.ID, 'visibleOnline')
#     if not is_online_checkbox.is_selected():
#         is_online_checkbox.click()

# def __deactivate_is_online(driver):
#     is_online_checkbox = driver.find_element(By.ID, 'visibleOnline')
#     if is_online_checkbox.is_selected():
#         is_online_checkbox.click()

# def __set_conversation_date(driver, str):
#     date_input = driver.find_element(By.ID, 'time-profile1')
#     time.sleep(1)
#     date_input.clear()
#     date_input.send_keys(str)

# def __set_name(driver, name):
#     profile1_name_input = driver.find_element(By.ID, 'profile1_name')
#     time.sleep(1)
#     profile1_name_input.clear()
#     profile1_name_input.send_keys(name)

# def __set_username(driver, username):
#     __deactivate_is_online(driver)
#     time.sleep(1)
#     show_username_radiobutton = driver.find_element(By.CSS_SELECTOR, 'input#Active_show')
#     if not show_username_radiobutton.is_selected():
#         show_username_radiobutton.click()
#     time.sleep(1)
#     # edit-active
#     time_or_nickname_input = driver.find_element(By.ID, 'edit-active')
#     time.sleep(1)
#     time_or_nickname_input.clear()
#     time_or_nickname_input.send_keys(username)

# def __download(driver, output_filename):
#     time.sleep(2)
#     download_button = driver.find_element(By.ID, 'snapshot')
#     download_button.click()
#     time.sleep(10)
#     # Move downloaded file to our destination
#     list_of_files = glob.glob(DOWNLOADS_ABSOLUTE_PATH + '*.png')
#     latest_file = max(list_of_files, key = os.path.getctime)
#     shutil.move(latest_file, os.path.join(PROJECT_ABSOLUTE_PATH + output_filename))

# def __write_my_message(driver, message):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile2_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person2")]')
#     profile2_tab.click()
#     time.sleep(1)
#     profile2_textarea = driver.find_element(By.ID, 'profile2_message')
#     profile2_textarea.clear()
#     profile2_textarea.send_keys(message)
#     time.sleep(1)
#     actions = ActionChains(driver)
#     for i in range(2):
#         actions.send_keys(Keys.TAB)
#     actions.send_keys(Keys.SPACE)
#     actions.perform()
#     time.sleep(1)

# def __write_other_message(driver, message):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile1_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person1")]')
#     profile1_tab.click()
#     time.sleep(1)
#     profile1_textarea = driver.find_element(By.ID, 'profile1_message')
#     profile1_textarea.clear()
#     profile1_textarea.send_keys(message)
#     time.sleep(1)
#     actions = ActionChains(driver)
#     actions.send_keys(Keys.TAB)
#     actions.send_keys(Keys.SPACE)
#     actions.perform()
#     time.sleep(1)

# # TODO: Implement sending foto

# def generate_conversation(name, username, messages, profile_picture_absolute_path, date_str, output_filename):
#     # Messages must come with autor and text
#     URL = 'https://prankshit.com/fake-instagram-chat-generator.php'

#     profile_picture_absolute_path = profile_picture_absolute_path.replace('/', '\\')

#     try:
#         driver = start_chrome(True)
#         go_to_and_wait_loaded(driver, URL)

#         time.sleep(2)
#         __setup(driver, name, username, profile_picture_absolute_path)
#         time.sleep(1)

#         # Add more data ('active')
#         messages = [
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'Holaaaaa!'
#             },
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'estás??'
#             },
#             {
#                 'sender': MESSAGE_SENDER_OTHER,
#                 'message': 'Sí, ¿qué pasa wacho??'
#             },
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'Nada, solo quería saludarte!! Campeón!'
#             },
#             {
#                 'sender': MESSAGE_SENDER_OTHER,
#                 'message': 'Dalee! Grande, gracias!!'
#             },
#         ]

#         for index, message in enumerate(messages):
#             if message['sender'] == MESSAGE_SENDER_ME:
#                 __write_my_message(driver, message['message'])
#             else:
#                 __write_other_message(driver, message['message'])

#             __download(driver, 'wip/test_instagram_' + str(index) + '.png')
#     finally:
#         driver.close()