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

# def __setup(driver, name, conversation_date, profile_picture_absolute_path):
#     # TODO: Set maximum 'name' and 'username' lengths
#     # TODO: Implement 'status' (?)
#     __set_name(driver, name)
#     __set_status(driver, 'En línea')
#     __set_conversation_date(driver, conversation_date)
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

# def __set_conversation_date(driver, str):
#     date_input = driver.find_element(By.ID, 'edit-chatday')
#     time.sleep(1)
#     date_input.clear()
#     date_input.send_keys(str)

# def __send_my_photo(driver, photo_absolute_path, hour):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile2_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person2")]')
#     profile2_tab.click()
#     element_present = EC.presence_of_element_located((By.ID, 'SecondImage'))
#     element = WebDriverWait(driver, 10).until(element_present)
#     time.sleep(1)
#     element = element.find_element(By.XPATH, '..')
#     element.click()
#     time.sleep(2)
#     pyautogui.write((photo_absolute_path).replace('/', '\\')) 
#     time.sleep(1)
#     pyautogui.press('enter')
#     time.sleep(1)
#     profile2_time_input = driver.find_element(By.ID, 'time-profile2')
#     profile2_time_input.clear()
#     profile2_time_input.send_keys(hour)
#     time.sleep(1)
#     # Set message as read
#     profile2_message_is_read_radiobutton = driver.find_element(By.ID, 'read')
#     if not profile2_message_is_read_radiobutton.is_selected():
#         profile2_message_is_read_radiobutton.click()
#     time.sleep(1)
#     profile2_textarea = driver.find_element(By.ID, 'profile2_message')
#     profile2_textarea.clear()
#     profile2_textarea.send_keys('')
#     time.sleep(1)
#     actions = ActionChains(driver)
#     for i in range(2):
#         actions.send_keys(Keys.TAB)
#     actions.send_keys(Keys.SPACE)
#     actions.perform()
#     time.sleep(1)

# def __send_other_photo(driver, photo_absolute_path, hour):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile2_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person1")]')
#     profile2_tab.click()
#     element_present = EC.presence_of_element_located((By.ID, 'InputFirstImage'))
#     element = WebDriverWait(driver, 10).until(element_present)
#     time.sleep(1)
#     element = element.find_element(By.XPATH, '..')
#     element.click()
#     time.sleep(2)
#     pyautogui.write((photo_absolute_path).replace('/', '\\')) 
#     time.sleep(1)
#     pyautogui.press('enter')
#     time.sleep(1)
#     profile1_time_input = driver.find_element(By.ID, 'time-profile1')
#     profile1_time_input.clear()
#     profile1_time_input.send_keys(hour)
#     time.sleep(1)
#     profile1_textarea = driver.find_element(By.ID, 'profile1_message')
#     profile1_textarea.clear()
#     profile1_textarea.send_keys('')
#     time.sleep(1)
#     actions = ActionChains(driver)
#     actions.send_keys(Keys.TAB)
#     actions.send_keys(Keys.SPACE)
#     actions.perform()
#     time.sleep(1)

# def __set_name(driver, name):
#     profile1_name_input = driver.find_element(By.ID, 'profile1_name')
#     time.sleep(1)
#     profile1_name_input.clear()
#     profile1_name_input.send_keys(name)

# def __set_status(driver, status):
#     status_input = driver.find_element(By.ID, 'edit-Status')
#     time.sleep(1)
#     status_input.clear()
#     status_input.send_keys(status)

# def __download(driver, output_filename):
#     time.sleep(2)
#     download_button = driver.find_element(By.ID, 'snapshot')
#     download_button.click()
#     time.sleep(10)
#     # Move downloaded file to our destination
#     list_of_files = glob.glob(DOWNLOADS_ABSOLUTE_PATH + '*.png')
#     latest_file = max(list_of_files, key = os.path.getctime)
#     shutil.move(latest_file, os.path.join(PROJECT_ABSOLUTE_PATH + output_filename))

# def __write_my_message(driver, message, hour):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile2_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person2")]')
#     profile2_tab.click()
#     time.sleep(1)
#     profile2_time_input = driver.find_element(By.ID, 'time-profile2')
#     profile2_time_input.clear()
#     profile2_time_input.send_keys(hour)
#     time.sleep(1)
#     # Set message as read
#     profile2_message_is_read_radiobutton = driver.find_element(By.ID, 'read')
#     if not profile2_message_is_read_radiobutton.is_selected():
#         profile2_message_is_read_radiobutton.click()
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

# def __write_other_message(driver, message, hour):
#     driver.execute_script('window.scrollTo(0, 0)')
#     profile1_tab = driver.find_element(By.XPATH, '//a[contains(@href, "#tab-person1")]')
#     profile1_tab.click()
#     time.sleep(1)
#     profile1_time_input = driver.find_element(By.ID, 'time-profile1')
#     profile1_time_input.clear()
#     profile1_time_input.send_keys(hour)
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
    
# def generate_conversation(name, messages, conversation_date, profile_picture_absolute_path, output_filename):
#     # Messages must come with autor and text
#     URL = 'https://prankshit.com/fake-whatsapp-chat-generator.php'

#     profile_picture_absolute_path = profile_picture_absolute_path.replace('/', '\\')

#     try:
#         driver = start_chrome(True)
#         go_to_and_wait_loaded(driver, URL)

#         # I force 'conversation_date' by now
#         conversation_date = 'Hoy'

#         time.sleep(2)
#         __setup(driver, name, conversation_date, profile_picture_absolute_path)
#         time.sleep(1)

#         # Add more data ('active')
#         messages = [
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'Holaaaaa!',
#                 'hour': '22:07',
#             },
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': '',
#                 'photo': 'C:/Users/dania/Desktop/PROYECTOS/Youtube/stockpediayt/software/ai.png',
#                 'hour': '22:07',
#             },
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'estás??',
#                 'hour': '22:07',
#             },
#             {
#                 'sender': MESSAGE_SENDER_OTHER,
#                 'message': 'Sí, ¿qué pasa wacho??',
#                 'hour': '22:09',
#             },
#             {
#                 'sender': MESSAGE_SENDER_OTHER,
#                 'message': '',
#                 'photo': 'C:/Users/dania/Desktop/PROYECTOS/Youtube/stockpediayt/software/ai_image.png',
#                 'hour': '22:10',
#             },
#             {
#                 'sender': MESSAGE_SENDER_ME,
#                 'message': 'Nada, solo quería saludarte!! Campeón!',
#                 'hour': '22:10',
#             },
#             {
#                 'sender': MESSAGE_SENDER_OTHER,
#                 'message': 'Dalee! Grande, gracias!!',
#                 'hour': '22:11'
#             },
#         ]

#         for index, message in enumerate(messages):
#             if message['sender'] == MESSAGE_SENDER_ME:
#                 if 'photo' in message and message['photo']:
#                     __send_my_photo(driver, message['photo'], message['hour'])
#                 else:
#                     __write_my_message(driver, message['message'], message['hour'])
#             else:
#                 if 'photo' in message and message['photo']:
#                     __send_other_photo(driver, message['photo'], message['hour'])
#                 else:
#                     __write_other_message(driver, message['message'], message['hour'])

#             __download(driver, 'wip/test_whatsapp_' + str(index) + '.png')
#     finally:
#         driver.close()