from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from query import query
from time import sleep
import pathes
import pandas as pd
from transformers import pipeline

links = []  
labels = []
scores = []
w_plus = 0
w_minus = 0
w_total = 0
REVIEWS = []
DATASET = dict()


def get_element_text(driver: WebDriver, path: str) -> str:
    try:
        return driver.find_element(By.XPATH, path).text
    except NoSuchElementException:
        return ''
    
def move_to_element(driver: WebDriver, element: WebElement | WebDriver) -> None:
    try:
        webdriver.ActionChains(driver).move_to_element(element).perform()
    except StaleElementReferenceException:
        pass

def element_click(driver: WebDriver | WebElement, path: str) -> bool:
    try:
        driver.find_element(By.XPATH, path).click()
        return True
    except:
        return False

def get_sentiment_analysis(classifier: pipeline, txt: str) -> str and float:
    result = classifier(txt)
    return result[0]['label'], result[0]['score']

def main():
    url = f'https://2gis.kz/almaty/search/{query}'
    driver = webdriver.Edge()
    driver.maximize_window()
    driver.get(url)
    element_click(driver, pathes.main_banner)
    element_click(driver, pathes.cookie_banner)
    element_click(driver, pathes.first_page)
    element_click(driver, pathes.reviews_button)
    sleep(1)

    total_mark = float(get_element_text(driver, pathes.reviews_total_mark))
    r_cnt = driver.find_element(By.XPATH, pathes.reviews_count).text

    for i in range(int(pathes.reviews_a_pattern[-18]), int(r_cnt) + int(pathes.reviews_a_pattern[-18]) + 1):
        link = pathes.reviews_a_pattern[:129] + str(i) + pathes.reviews_a_pattern[130:]
        links.append(link)
    
    classifier = pipeline('sentiment-analysis', model='blanchefort/rubert-base-cased-sentiment')
    for link in links:
        review = get_element_text(driver, link)
        if review != '':
            label, score = get_sentiment_analysis(classifier, review)
            REVIEWS.append(review)
            labels.append(label)
            scores.append(score)
    
    
    #print(f'Total mark: {total_mark}')
    #print(f'Reviews count: {r_cnt}')
    #print(len(REVIEWS))
    #for review in REVIEWS:
    #    print(review)

    r_cnt = len(REVIEWS)
    driver.quit()

    DATASET['total_mark'] = total_mark
    DATASET['reviews_count'] = r_cnt
    DATASET['reviews'] = REVIEWS
    DATASET['labels'] = labels
    DATASET['scores'] = scores

    for i in range(len(labels)):
        if labels[i] == 'POSITIVE' or labels[i] == 'NEUTRAL':
            w_plus += scores[i]
        elif labels[i] == 'NEGATIVE':
            w_minus -= scores[i]
        
        w_total += scores[i]

    print(w_total, w_plus, w_minus, total_mark/5)
    print(round(30000 * (w_plus/w_total) * (1 - (w_minus/w_total)) * (total_mark/5)))

if __name__ == '__main__':
    main()