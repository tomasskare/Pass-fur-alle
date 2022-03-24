from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select    
from datetime import datetime
import time
import sys

sys.setrecursionlimit(100000)

web = webdriver.Chrome()

# Constants
startBookingDate = datetime.today().strftime('%Y-%m-%d') # Start searching today, if you want to start some other day, just change this to a date with the format YYYY-MM-DD
endBookingDate = "2022-08-25" # The last date you want to search for
firstDate = False # If you want to look for the first date using "First available time", change to True
firstNames = ['Test'] # Your first name(s)
lastNames = ['Testsson'] # Your last name(s)
emailAddress = 'test@test.se' # Your email
phoneNumber = '076127567' # Your phone number
numberOfPeople = 1
manualVerify = True # Change this to False if you want the script to automatically book the time in the last step

# Terminal output
print ('Alla län: https://polisen.se/tjanster-tillstand/pass-och-nationellt-id-kort/boka-tid-hitta-passexpedition/')
lan = input("Välj län. Sista delen av url t ex 'halland'. Eller tryck enter för Skåne: ")
if lan:
    expedition = input("Välj expedition. T ex 'Halmstad'. Eller tryck enter för hela länet: ")

if lan and expedition:
    print("Län: ", lan)
    print("Expedition: ", expedition)
elif lan:
    print("Län: ", lan)
    expedition = ''
else:
    lan = 'skane'
    expedition = ''

# Open web page
web.get('https://bokapass.nemoq.se/Booking/Booking/Index/' + lan)

# Start the search
def searchPassTime():
    try:
        time.sleep(1)
        # Click the first button
        startButton = web.find_element(by=By.XPATH, value='//*[@id="Main"]/div[2]/div[1]/div/form/div[2]/input')
        startButton.click()
        time.sleep(.5)
        # Accept
        infoCheck = web.find_element(by=By.XPATH, value='//*[@id="AcceptInformationStorage"]')
        infoNumber = Select(web.find_element(by=By.XPATH, value='//*[@id="NumberOfPeople"]'))
        infoNext = web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[2]/input')
        infoCheck.click()
        infoNumber.select_by_value(str(numberOfPeople))
        infoNext.click()
        time.sleep(.5)
        # Confirm living in Sweden
        for person in range(1, numberOfPeople+1):
            liveInRadio = web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/div[' + str(person) + ']/div/label[1]')
            liveInRadio.click()
        liveInNext = web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[2]/input')
        liveInNext.click()
        time.sleep(.5)
        setBookingDate()
        clickTimeIfExists()
    except NoSuchElementException:
        if firstDate == False:
            time.sleep(10)
        searchPassTime()

# If a time slot is found, click it
def clickTimeIfExists():
    try:
        endBookingDateDateTime = time.strptime(endBookingDate, "%Y-%m-%d")
        formInputDateTime = time.strptime(web.find_element(by=By.XPATH, value='//*[@id="datepicker"]').get_property('value'), "%Y-%m-%d")
        # If form date is larger than your end booking date, start over
        if formInputDateTime > endBookingDateDateTime:
            if firstDate == True:
                time.sleep(15)
            setBookingDate()
            clickTimeIfExists()
        else:
            # Look for a time slot
            if firstDate == False:
                web.find_element(by=By.XPATH, value='//*[@class="timetable-cells"]').click()
            else:
                web.find_element(by=By.XPATH, value='//*[contains(@aria-label,"202")]').click()
            web.find_element(by=By.XPATH, value='//*[@id="booking-next"]').click()
            time.sleep(.5)
            # Fill out your name
            for person in range(numberOfPeople):
                web.find_element(by=By.XPATH, value='//*[@id="Customers_' + str(person) + '__BookingFieldValues_0__Value"]').send_keys(firstNames[person])
                web.find_element(by=By.XPATH, value='//*[@id="Customers_' + str(person) + '__BookingFieldValues_1__Value"]').send_keys(lastNames[person])
                web.find_element(by=By.XPATH, value='//*[@id="Customers_' + str(person) + '__Services_0__IsSelected"]').click()
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[2]/input').click()
            time.sleep(.5)
            # Move on
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div/input').click()
            time.sleep(.5)
            # Fill out your personal information
            web.find_element(by=By.XPATH, value='//*[@id="EmailAddress"]').send_keys(emailAddress)
            web.find_element(by=By.XPATH, value='//*[@id="ConfirmEmailAddress"]').send_keys(emailAddress)
            web.find_element(by=By.XPATH, value='//*[@id="PhoneNumber"]').send_keys(phoneNumber)
            web.find_element(by=By.XPATH, value='//*[@id="ConfirmPhoneNumber"]').send_keys(phoneNumber)
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/div[5]/div/label[1]').click()
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/div[5]/div/label[2]').click()
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/div[6]/div/label[1]').click()
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/div[6]/div/label[2]').click()
            web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[2]/input').click()
            time.sleep(.5)
            if (manualVerify == False):
                # Verify your booking
                web.find_element(by=By.XPATH, value='//*[@id="Main"]/form/div[1]/input').click()
    except NoSuchElementException:
        if firstDate == False:
            # If there are no times available, check next day
            web.find_element(by=By.XPATH, value='//*[@class="btn btn-link pull-right"]').click()
        time.sleep(.5)
        clickTimeIfExists()

# Fill the form with search settings
def setBookingDate():
    if (expedition):
        select = Select(web.find_element(by=By.XPATH, value='//*[@id="SectionId"]'))
        select.select_by_visible_text(expedition)
    if firstDate == False:
        # Search next day
        bookingDate = web.find_element(by=By.XPATH, value='//*[@id="datepicker"]')
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        bookingDate.send_keys(Keys.BACKSPACE)
        myBookingDate = startBookingDate
        bookingDate.send_keys(myBookingDate)
        bookingDate.send_keys(Keys.TAB)
        searchTimeButton = web.find_element(by=By.XPATH, value='//*[@id="Main"]/form[1]/div/div[6]/div/input[1]')
    else:
        # Search first available time
        searchTimeButton = web.find_element(by=By.XPATH, value='//*[@id="Main"]/form[1]/div/div[6]/div/input[2]')
    searchTimeButton.click()

# Kick it!
searchPassTime()
