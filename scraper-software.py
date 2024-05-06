from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

arrHashTags = ["vcnojl1", "vcnojl2"]

def hasWebelement(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def handleZero(value):
    if len(value) == 0:
        return "0"
    else:
        return value

def sentiment(con, text):
    response = con.analyze(
        text=text,
        features=Features(sentiment=SentimentOptions())).get_result()
    return [response["sentiment"]["document"]["label"], str(response["sentiment"]["document"]["score"]).replace(".",",")]

def sentiment2():
    return ["teste", "0,0"]

def logar():
    service = Service('YOUR_PATH_TO/DRIVERSELENIUM/chromedriver-linux64/chromedriver')
    options = webdriver.ChromeOptions()
    options.binary_location = "YOUR_PATH_TO/DRIVERSELENIUM/chrome-linux64/chrome"
    options.add_argument("--disable-notifications")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"],
    )
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://twitter.com/i/flow/login")

    element = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))
    )
    element.send_keys("YOUR_X_EMAIL_TO_LOGIN")
    element.send_keys(Keys.ENTER)

    time.sleep(3)  

    element = WebDriverWait(driver, 300).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="password"]'))
    )
    element.send_keys("YOUR_X_PASSWORD_TO_LOGIN")
    element.send_keys(Keys.ENTER)
    time.sleep(3)

    return driver

def main(driver):
    authenticator = IAMAuthenticator('YOUR_KEY_FROM_IBM_WATSON')
    nlpIBM = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    nlpIBM.set_service_url('YOUR_URL_TO_IBM_WATSON)
    
    for i in range(len(arrHashTags)):
        driver.get("https://twitter.com/hashtag/"+arrHashTags[i]+"?f=live")
        time.sleep(5)

        pages = 10
        last_height = 0
        while pages > 0:
            try:
                fullContent = driver.find_element(By.XPATH, "//div[@data-testid='primaryColumn']")
                tweetFull = fullContent.find_elements(By.TAG_NAME, "article")
                j = 0
            except NoSuchElementException as e:
                print(e)
            for j in range(len(tweetFull)):
                try:
                    hasPopupNotification = hasWebelement(driver, "//div[@data-testid='app-bar-close']")
                    if hasPopupNotification:
                        driver.find_element(By.XPATH, "//div[@data-testid='app-bar-close']").click()
                        print("=== POPUP CLOSED! ===")
                        j = j - 1
                    else:
                        userName = tweetFull[j].find_element(By.XPATH, ".//div[@data-testid='User-Name']")
                        tweetTime = userName.find_element(By.TAG_NAME, "time").get_attribute("datetime").replace("T", " ").replace(".000Z","")
                        userName = userName.text.split('\n')
                        user = userName[0]
                        userNick = userName[1]
                        # print(tweetTime)
                        tweetText = tweetFull[j].find_element(By.XPATH, ".//div[@data-testid='tweetText']").text.replace("\n", " ")
                        # print(tweetText.text)
                        reply = tweetFull[j].find_element(By.XPATH, ".//div[@data-testid='reply']").text
                        reply = handleZero(reply)
                        # print("Respostas: "+reply.text)
                        retweet = tweetFull[j].find_element(By.XPATH, ".//div[@data-testid='retweet']").text
                        retweet = handleZero(retweet)
                        # print("Repostagens: "+retweet.text)
                        like = tweetFull[j].find_element(By.XPATH, ".//div[@data-testid='like']").text
                        like = handleZero(like)
                        # print("Curtidas: "+like.text)
                        view = tweetFull[j].find_elements(By.XPATH, ".//span[@data-testid='app-text-transition-container']/span/span")[-1].text
                        view = handleZero(view)
                        # print("Visualizações: "+view.text)

                        twSentiment = sentiment(nlpIBM, tweetText)
                        # twSentiment = sentiment2()
                        
                        with open('data.csv', 'a') as f:
                            print(arrHashTags[i], user, userNick, tweetTime, tweetText, twSentiment[0], twSentiment[1], reply, retweet, like, view, sep="|", file=f)

                except NoSuchElementException as error:
                    print("NoSuchElementException: ")
                except IndexError as error2:
                    print("IndexError: ")
                except ApiException as error3:
                    print("IBMWatsonError: ")

                j = j + 1
                # print("====================================================")
                
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            # Wait to load page
            time.sleep(7)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            # break condition
            if new_height == last_height:
                break
            last_height = new_height

            pages = pages - 1
        
        # driver.close()

driver = logar()
main(driver)
