import requests
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
from tkinter import *
import urllib
import math
from PIL import ImageTk, Image
from selenium.common.exceptions import TimeoutException

# Array for storing eBay product after retrieving it from eBay website
ebayProductArr = []

# Array for storing Amazon product after retrieving it from Amazon website
amazonProductArr = []

root = Tk()
root.title("Product Price Comparison")
root.geometry("600x600")
search = StringVar()
state = StringVar()
state.set("Ready")

def USDtoINR(amount):
    url = f"https://api.apilayer.com/exchangerates_data/convert?to=PKR&from=USD&amount={amount}"
    payload = {}
    headers = {
        "apikey": "3s0PboHwgdGYDTykizxdJrH2f0osJut0"
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    status_code = response.status_code
    result = response.text

    # converting string to dictionary
    r = json.loads(result)
    return f"Rs. {math.trunc(r['result'])}"

# Function to get products from Amazon
def getDetailsAmazon():
    amazonURL = f"https://www.amazon.com/s?k={search.get()}"
    options = Options()
    options.headless = True
    print("Search Started")
    state.set(f"Searching {search.get()} on Amazon")

    service = Service('geckodriver.exe')  # Replace with path to geckodriver
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(amazonURL)
    print("Search End")
    state.set(f"Searched Finished")

    print("Finding Elements")
    state.set(f"Finding Products....")

    try:
        title = driver.find_element(By.CSS_SELECTOR, ".s-title-instructions-style h2 a span")
        price = driver.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
        link = driver.find_element(By.CSS_SELECTOR, f".aok-relative span a").get_attribute("href")
        photo = driver.find_element(By.CSS_SELECTOR, f".aok-relative span a div img")
        
        print("Elements Found")
        state.set(f"Products Found")
        
        # Clearing all previous items from array
        amazonProductArr.clear()

        # Adding product to array
        amazonProductArr.append(link)
        amazonProductArr.append(title.text)
        pkrPrice = USDtoINR(float(price.get_attribute("textContent")[1:]))
        amazonProductArr.append(pkrPrice)
        amazonProductArr.append(photo.get_attribute("src"))
        
        print("Amazon Products Done")
        state.set(f"Amazon Products Done")
    except Exception as e:
        print(f"Error fetching Amazon data: {e}")
        state.set(f"Error: Amazon search failed")

    driver.quit()
    showAmazonProducts()

# Function to get products from eBay
def getDetailsEbay():
    ebayURL = f"https://www.ebay.com/sch/i.html?_nkw={search.get()}"
    options = Options()
    options.headless = True
    print("Search Started on eBay")
    state.set(f"Searching {search.get()} on eBay")

    service = Service('geckodriver.exe')  # Replace with path to geckodriver
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(ebayURL)
    print("Search End")
    state.set(f"Searched Finished")

    print("Finding Elements")
    state.set(f"Finding Products....")

    try:
        # Finding product title
        title = driver.find_element(By.CSS_SELECTOR, ".s-item__title")

        # Finding product price
        price = driver.find_element(By.CSS_SELECTOR, ".s-item__price")

        # Finding product link
        link = driver.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        # Finding product image
        photo = driver.find_element(By.CSS_SELECTOR, ".s-item__image-img").get_attribute("src")

        print("Elements Found")
        state.set(f"Products Found")

        # Clearing all previous items from array
        ebayProductArr.clear()

        # Adding product to array
        ebayProductArr.append(link)
        ebayProductArr.append(title.text)
        pkrPrice = USDtoINR(float(price.text[1:]))  # Remove '$' symbol from price text
        ebayProductArr.append(pkrPrice)
        ebayProductArr.append(photo)

        print("eBay Products Done")
        state.set(f"eBay Products Done")
    except Exception as e:
        print(f"Error fetching eBay data: {e}")
        state.set(f"Error: eBay search failed")

    driver.quit()
    showEbayProducts()  # Show eBay products in the UI

# Function to show products from Amazon
def showAmazonProducts():
    if not amazonProductArr:
        print("No Amazon products to display.")
        state.set("No Amazon products to display.")
        return

    deleteFrame(amazonProductFrame)
    Label(amazonProductFrame, text="AMAZON", font=("Calibri", 20, "bold")).pack()
    Label(amazonProductFrame, text=addSpacing(amazonProductArr[1])).pack()
    Label(amazonProductFrame, text=amazonProductArr[2]).pack()
    Button(amazonProductFrame, text="Open in AMAZON", command=lambda: webbrowser.open(amazonProductArr[0])).pack()

    raw_data = urllib.request.urlopen(amazonProductArr[3])
    u = raw_data.read()
    raw_data.close()
    photo = ImageTk.PhotoImage(data=u)
    Label(amazonProductFrame, image=photo, width=300, height=300).pack(side=RIGHT)
    amazonProductFrame.image = photo
    print("Amazon DONE")

# Function to show products from eBay
def showEbayProducts():
    if not ebayProductArr:
        print("No eBay products to display.")
        state.set("No eBay products to display.")
        return

    deleteFrame(ebayProductFrame)
    Label(ebayProductFrame, text="EBAY", font=("Calibri", 20, "bold")).pack()
    Label(ebayProductFrame, text=addSpacing(ebayProductArr[1])).pack()
    Label(ebayProductFrame, text=ebayProductArr[2]).pack()
    Button(ebayProductFrame, text="Open in eBay", command=lambda: webbrowser.open(ebayProductArr[0])).pack()

    raw_data = urllib.request.urlopen(ebayProductArr[3])
    u = raw_data.read()
    raw_data.close()
    photo = ImageTk.PhotoImage(data=u)
    Label(ebayProductFrame, image=photo, width=300, height=300).pack(side=RIGHT, pady=100)
    ebayProductFrame.image = photo
    print("eBay DONE")

# Function to add spacing to text (for better display)
def addSpacing(text):
    newText = ""
    i = 0
    text = text.split(" ")
    for val in text:
        if i == 10:
            newText += "\n "
            i = 0
        newText += f"{val} "
        i += 1

    return newText

# Function to delete frames (to refresh the GUI display)
def deleteFrame(frame):
    for item in frame.winfo_children():
        item.destroy()

    print("Items Deleted")

# Main function that will run when user enters product name and clicks SEARCH PRODUCT
def getResult():
    getDetailsEbay()  # Fetch from eBay
    getDetailsAmazon()  # Fetch from Amazon
    state.set(f"Ready")

# Search Entry for entering product name on UI
label = Label(root, text="Enter Search Result: ")
label.pack()
entry = Entry(root, textvariable=search)
entry.pack()

button = Button(root, text="Search Product", command=getResult)
button.pack()

# Product Frame for showing eBay and Amazon products
productFrame = Frame(root, relief=SUNKEN)

# eBay Frame where eBay product will be shown
ebayProductFrame = Frame(root)
ebayProductFrame.pack(side=LEFT)

# Amazon Frame where Amazon product will be shown
amazonProductFrame = Frame(root)
amazonProductFrame.pack(side=LEFT)

productFrame.pack(side=TOP, anchor=CENTER)

statusBar = Label(root, textvariable=state, relief=SUNKEN)
statusBar.pack(fill=X, side=BOTTOM)

root.mainloop()
