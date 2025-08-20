"""
TODO: This has to use the 'yta_web_scraper' library and
also must be in another library, not this one.

I comment it to avoid errors.
"""
# from yta_general_utils.web.tiktok.url_parser import parse_tiktok_url
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys

# import time


# def get_video_metadata_by_url(tiktok_video_url):
#     """
#     Receives a tiktok video url and build the metadata information by
#     scrapping with chromedriver.

#     This method returns the video 'id', 'username', 'video_id', 'title'
#     and 'description'
#     """
#     internal_info = parse_tiktok_url(tiktok_video_url)

#     try:
#         options = Options()
#         options.add_argument("--start-maximized")
#         # Remove this line below for debug
#         #options.add_argument("--headless=new") # for Chrome >= 109
#         driver = webdriver.Chrome(options = options)
#         driver.get(internal_info['url'])

#         time.sleep(10)

#         # [ 1 ] Continue as guest
#         actions = ActionChains(driver) 
#         actions.send_keys(Keys.TAB * 8)
#         actions.perform()

#         actions = ActionChains(driver)
#         actions.send_keys(Keys.ENTER * 1)
#         actions.perform()

#         time.sleep(5)

#         title = driver.title.replace('... | TikTok', '')
#         description = ''
#         description_elements = driver.find_elements_by_xpath("//*[@data-e2e='browse-video-desc']")[0].find_elements_by_css_selector("*")
#         for element in description_elements:
#             description += element.get_attribute('innerText') + ' '
#         description = description.strip()

#     finally:
#         driver.close()

#         return {
#             'title': title,
#             'description': description,
#             'url': internal_info['url'],
#             'username': internal_info['username'],
#             'video_id': internal_info['video_id']
#         }

# def get_popular_tiktok_videos():
#     """
#     Work in progress.
#     """
#     # TODO: In progress. To explore most popular videos and build a list of urls

#     # Create a Chrome driver
#     options = Options()
#     options.add_argument("--start-maximized")
#     driver = webdriver.Chrome(options = options)

#     try:
#         # TODO: Improve the way we look for those popular tiktok videos
#         # We can download them, but we need to be sure that those videos
#         # are actually popular and could be viral
#         """
#         driver.get(test_url)
#         time.sleep(2)
#         print(driver.current_url)
#         """

#         """
#         explore_tiktok_url = 'https://www.tiktok.com/explore'
#         driver.get(explore_tiktok_url)

#         time.sleep(5)

#         # [ 1 ] Continue as guest
#         actions = ActionChains(driver) 
#         actions.send_keys(Keys.TAB * 8)
#         actions.perform()

#         actions = ActionChains(driver)
#         actions.send_keys(Keys.ENTER * 1)
#         actions.perform()

#         time.sleep(5)

#         # [ 2 ] Look for popular videos
#         videos = driver.find_elements_by_xpath("//*[@data-e2e='explore-item']")
        
#         for video in videos:
#             # [ 3 ] Download each of those videos
#             video_link_element = video.find_elements_by_css_selector("*")[0].find_elements_by_css_selector("*")[0].find_elements_by_css_selector("*")[0]
#             href = video_link_element.get_attribute('href')
#             split = href.split('/')
#             username = str(split[len(split) - 3]).replace('@', '')
#             video_id = split[len(split) - 1]

#             # TODO: What about video title?
#             output_video_name = username + '_' + video_id + '_tiktok.mp4'
#             print('Downloading video as "' + output_video_name + '"')
#             download_tiktok_video(href, output_video_name)
#         # data-e2e="explore-item" and 3rd son is a href with video link
#         """

#         """
#         If I share a video from mobile Tiktok, the link is like this (https://vm.tiktok.com/ZGeSJ6YRA),
#         but if you search that on Chrome, it will be replaced by the whole url like this 
#         (https://www.tiktok.com/@ahorayasabesque/video/7327001175616703777?_r=1&_t=8jqq93LWqsC).
#         From that long link, if you remove the '?_...' part, you'll get the whole link that we use,
#         including the username and the video_id, so we can work propertly with it.

#         This could be a way of storing interesting tiktok videos in some places and then
#         automate the process of adding some edition to the video (maybe some short video before,
#         overlay video, title, etc.) and then upload it to youtube as a short.
#         """

#     finally:
#         driver.close()
