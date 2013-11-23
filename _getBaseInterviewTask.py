# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re

class GetBaseTask(unittest.TestCase):
    
    def setUp(self):
        self.username = "donatelo@interia.pl" # TODO: give username and password as parameters
        self.password = "donatelo1"
        self.driver = webdriver.Firefox()
        #self.driver.implicitly_wait(30)
        self.wait = WebDriverWait(self.driver, 10) 
        self.base_url = "https://core.futuresimple.com"
    
    def test_interviewTask(self):
        driver = self.driver
        driver.get(self.base_url + "/users/login")
        driver.find_element_by_id("user_email").clear()
        driver.find_element_by_id("user_email").send_keys(str(self.username))
        driver.find_element_by_id("user_password").clear()
        driver.find_element_by_id("user_password").send_keys(str(self.password))
        driver.find_element_by_xpath("//form[@id='user_new']/fieldset/div[3]/div/button").click()
        ## 1. store custom fields names and types from settings
        self.storeSettings()
        ## 2. navigate to Leads module and check custom fields avaliable on New form
        #self.wait.until(lambda d: d.find_element_by_id("nav-leads").is_displayed())
        driver.find_element_by_id("nav-leads").click()
        time.sleep(2)#self.wait.until(lambda d: d.find_element_by_link_text("Lead").is_displayed())
        driver.find_element_by_link_text("Lead").click()
        allCustomFields = driver.find_elements_by_xpath("//*[contains(@name,'custom_fields')]")
        allCustomFieldsNamesList = list()
        for item in allCustomFields:
            allCustomFieldsNamesList.append(self.getCustomFieldNameFromNameAttribute(item))
        self.validateCustomFields(self.customFieldsLeadsList, allCustomFieldsNamesList)
        ## 3. navigate to Contacts module and check custom fields avaliable on New form
        driver.find_element_by_id("nav-contacts").click()
        self.wait.until(lambda d: d.find_element_by_link_text("Person").is_displayed())
        driver.find_element_by_link_text("Person").click()
        allCustomFields = driver.find_elements_by_xpath("//*[contains(@name,'custom_fields')]")
        allCustomFieldsNamesList = list()
        for item in allCustomFields:
            allCustomFieldsNamesList.append(self.getCustomFieldNameFromNameAttribute(item))
        self.validateCustomFields(self.customFieldsContactsList, allCustomFieldsNamesList)
        ## 4. navigate to Deals module and check custom fields avaliable on New form
        '''driver.find_element_by_id("nav-sales").click()
        time.sleep(2)
        driver.find_element_by_link_text("Deal").click()
        allCustomFields = driver.find_elements_by_xpath("//*[contains(@name,'custom_fields')]")
        allCustomFieldsNamesList = list()
        for item in allCustomFields:
            allCustomFieldsNamesList.append(self.getCustomFieldNameFromNameAttribute(item))
        self.validateCustomFields(self.customFieldsDealsList, allCustomFieldsNamesList)'''

    def storeSettings(self):
        # navigate to settings
        self.wait.until(lambda d: d.find_element_by_css_selector("i.icon-angle-down").is_displayed())
        self.driver.find_element_by_css_selector("i.icon-angle-down").click()
        self.wait.until(lambda d: d.find_element_by_css_selector("a > strong").is_displayed())
        self.driver.find_element_by_css_selector("a > strong").click()
        self.wait.until(lambda d: d.find_element_by_css_selector("ul.nav.nav-list > li.leads > a").is_displayed())
        self.driver.find_element_by_css_selector("ul.nav.nav-list > li.leads > a").click()
        self.customFieldsLeadsList = self.getCustomFielsNamesAndTypesFromSettings()
        self.printCustomFields(self.customFieldsLeadsList, 'Leads')
        self.wait.until(lambda d: d.find_element_by_css_selector("ul.nav.nav-list > li.contacts > a").is_displayed())
        self.driver.find_element_by_css_selector("ul.nav.nav-list > li.contacts > a").click()
        self.customFieldsContactsList = self.getCustomFielsNamesAndTypesFromSettings()
        self.printCustomFields(self.customFieldsContactsList, 'Contacts')
        self.wait.until(lambda d: d.find_element_by_css_selector("ul.nav.nav-list > li.deals > a").is_displayed())
        self.driver.find_element_by_css_selector("ul.nav.nav-list > li.deals > a").click()
        self.wait.until(lambda d: d.find_element_by_link_text("Custom Fields").is_displayed())
        self.driver.find_element_by_link_text("Custom Fields").click()
        self.customFieldsDealsList = self.getCustomFielsNamesAndTypesFromSettings()
        self.printCustomFields(self.customFieldsDealsList, 'Deals')
    
    def validateCustomFields(self, customFieldsListFromSettings, customFieldsListNewForm):
        # 1. check if number of displayed custom fields is equal to number of defined cistom fields
        self.assertEqual(len(customFieldsListFromSettings), len(customFieldsListNewForm))
        # 2. check custom fields names and order (the same as in settings)
        for item in customFieldsListFromSettings:#item contains field name and type
            idx = customFieldsListFromSettings.index(item)
            self.assertEqual(item[0], customFieldsListNewForm[idx])
        
    #
    # TODO: store more attributes co check the Custom Fields types available on the New/Edit forms for Leads, Contacts and Deals are correct
    # for Contacts additionaly check if field is displayed correctly for Person and/or Company
    #
    def storeCustomFieldsProperties(self, customFieldsList):
        self.storedPropertiesList = list() # every field has 3 attributes: name, tag name and text arrtibute value (if present)
        for item in customFieldsList:
            itemPropertiesList = list()
            itemPropertiesList.append(self.getCustomFieldNameFromNameAttribute(item))
            itemPropertiesList.append(item.tag_name)
            itemPropertiesList.append(item.get_attribute("type"))
            self.storedPropertiesList.append(itemPropertiesList)
    
    def getCustomFieldNameFromNameAttribute(self, item):
        attrValue = item.get_attribute("name")
        return re.search(r'^custom_fields\[(.*)\]$', attrValue).group(1).strip()

    def printCustomFields(self, customFieldsList, categoryName):
        print '\n>>>> List of fields and their types in %s category' %categoryName
        for fieldName, fieldType in customFieldsList:
            print fieldName,'\t - \t', fieldType
            
    def getCustomFielsNamesAndTypesFromSettings(self):
        regex = r'^(.*)\((.*)\)$'
        driver = self.driver
        fieldsList = driver.find_elements_by_xpath("//div[@id='custom-fields']/div[@class='named-objects-list ui-sortable']/.//label[@class='control-label']/h4")
        outputList = list()
        for item in fieldsList:
            tempList = list()
            try:
                tempList.append(re.search(regex, item.text).group(1).strip())
                tempList.append(re.search(regex, item.text).group(2).strip())
                #print(tempList)
                outputList.append(tempList)
            except:
                print('Input string in incorrect format')
        return outputList
    
    def tearDown(self):
        self.driver.quit()
        #self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
