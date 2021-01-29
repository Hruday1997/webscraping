from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask,render_template,request
from pymongo import MongoClient
import json

app=Flask(__name__)

conn = MongoClient("mongodb://localhost:27017/")
db = conn["legodesk"]
collection = db["scraping"]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/insert",methods=["POST"])
def scrapeAndInsert():
    if request.method == "POST":
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        driver.get('https://dsscic.nic.in/cause-list-report-web/registry_cause_list/1')
        #driver.find_element_by_xpath("//input[@value='appCom']").click()
        Select(driver.find_element_by_id("commissionname")).select_by_visible_text(request.form["cic"])
        Select(driver.find_element_by_id("seach_type")).select_by_visible_text(request.form["searchtype"])
        driver.find_element_by_id("fromdate").send_keys(request.form["fromdate"])
        driver.find_element_by_id("todate").send_keys(request.form["todate"])
        driver.find_element_by_id("search_button").click()
        #Select(driver.find_element_by_id("page_length")).select_by_visible_text("All")

        for table in driver.find_elements_by_tag_name('table'):
            data = [[data.text for data in item.find_elements_by_tag_name("td")][1:] for item in table.find_elements_by_tag_name("tr")][2:]
            head = [head.text for head in table.find_elements_by_tag_name("th")][4:]
            final = [dict(zip(head,i)) for i in data]
            docs = collection.insert_many(final)
            return json.dumps(str(final))

if __name__ == "__main__":
    app.run(debug=True)