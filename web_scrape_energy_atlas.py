import json

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from datetime import date, datetime, timedelta
import time
import warnings
warnings.filterwarnings("ignore")

#%% Parameters
year = date.today().year
month = date.today().month
query_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

#%% Functions 
def get_profile_table_data(profile_table, type_):
    number_of_powerplants = None
    installed_capacity = None
    ratio_to_installed_capacity = None
    annual_production = None
    production_to_consumption_ratio = None
    number_of_licenced = None
    number_of_unlicenced = None

    for row in profile_table:
        th = row.find_elements(By.TAG_NAME, "th")
        td = row.find_elements(By.TAG_NAME, "td")

        param = th[0].text if isinstance(th, list) else th.text
        param = param.replace(" :", "")

        val = td[0].text if isinstance(td, list) else td.text

        if "Kayıtlı Santral Sayısı" in param:
            try:
                number_of_powerplants = int(val)
            except Exception as e:
                print(e)

        elif "Kurulu Güç" in param:
            try:
                installed_capacity = float(val.split(" ")[0])
            except Exception as e:
                print(e)
        elif "Kurulu Güce Oranı" in param:
            try:
                ratio_to_installed_capacity = float(val.replace("% ", "").replace(",", "."))
            except Exception as e:
                print(e)
        elif "Yıllık Elektrik Üretimi" in param:
            try:
                annual_production = float(val.replace("~", "").strip().split(" ")[0]) * 1000
            except Exception as e:
                print(e)
        elif "Üretimin Tüketime Oranı" in param:
            try:
                production_to_consumption_ratio = float(val.replace("% ", "").replace(",", "."))
            except Exception as e:
                print(e)
        elif "Lisans Durumu" in param:
            try:
                number_of_licenced = int(val.split(",")[0].replace(" lisanslı", ""))
                number_of_unlicenced = int(val.split(",")[1].replace(" lisanssız", ""))
            except Exception as e:
                print(e)

    data_ = [year, month, type_, number_of_powerplants, installed_capacity, ratio_to_installed_capacity, annual_production, production_to_consumption_ratio, number_of_licenced, number_of_unlicenced, query_date]
    return data_

def get_project_table(project_table, type_):
    data_ = []
    for row in project_table:  
        td = row.find_elements(By.TAG_NAME, "td")

        state = td[0].text.strip()
        power = td[1].text.strip()
        percentage = td[2].text.replace("%","").replace(",",".")

        if "\n" in power:
            power = power.replace("\n", " ").split(" ")[0]

        if "\n" in percentage:
            percentage = percentage.replace("\n", " ").split(" ")[0]

        try:
            power = float(power)
        except Exception as e:
            print(e)
        try:
            percentage = float(percentage)
        except Exception as e:
            print(e)

        data_.append([year, month, type_, state, power, percentage, query_date])
    return data_

def get_table(table, type_):
    data_ = []
    for row in table:  
        td = row.find_elements(By.TAG_NAME, "td")
        
        place = td[0].text.replace(")", "")
        powerplant = td[1].text
        city = td[2].text
        company = td[3].text
        installed_capacity = td[4].text.split(" ")[0].replace(",", ".")
        
        try:
            place = int(place)
        except Exception as e:
            print(e)
        try:
            installed_capacity = float(installed_capacity)
        except Exception as e:
            print(e)
        
        data_.append([year, month, type_, place, powerplant, city, company, installed_capacity, query_date])
    return data_

def save_to_json(data, file_name):
    with open(f"{file_name}.json", "w") as f:
        f.write(json.dumps(dictionary, indent=4))

if __name__ == "__main__":
    options = ChromeOptions()
    # options.add_argument("--start-maximized")
    # options.add_experimental_option("detach", True) # to stay browser open
    options.add_argument("--headless=new") # to make browser invisible

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    #%% WPP
    driver.get("https://www.enerjiatlasi.com/ruzgar/")
    time.sleep(5)

    wpp_profile_table = driver.find_elements(By.XPATH, """//*/div[@class='s_sbsag']/table/tbody/tr""")
    wpp_project_table = driver.find_elements(By.XPATH, """//*/table[@id='tozel2']/tbody/tr""")
    wpp_table = driver.find_elements(By.XPATH, """//*/div[@class='liste p5r']/table/tbody/tr""")

    type_ = "WPP"

    #%% Ruzgar Enerji Santralleri Profili
    data_ = get_profile_table_data(wpp_profile_table, type_)
    save_to_json(data_, "Ruzgar Enerji Santralleri Profili")

    #%% Ruzgar Enerji Santralleri Kurulu Guc ve Proje Kapasiteleri
    data_ = get_project_table(wpp_project_table, type_)
    save_to_json(data_, "Ruzgar Enerji Santralleri Kurulu Guc ve Proje Kapasiteleri")

    #%% Isletmedeki Ruzgar Enerji Santralleri
    data_ = get_table(wpp_table, type_)
    save_to_json(data_, "Isletmedeki Ruzgar Enerji Santralleri")

    #%% SPP
    driver.get("https://www.enerjiatlasi.com/gunes/")
    time.sleep(5)

    spp_profile_table = driver.find_elements(By.XPATH, """//*/div[@class='s_sbsag']/table/tbody/tr""")
    spp_project_table = driver.find_elements(By.XPATH, """//*/table[@id='tozel2']/tbody/tr""")
    spp_table = driver.find_elements(By.XPATH, """//*/div[@class='liste p5r']/table/tbody/tr""")

    type_ = "SPP"

    #%% Gunes Enerji Santralleri Profili
    data_ = get_profile_table_data(spp_profile_table, type_)
    save_to_json(data_, "Gunes Enerji Santralleri Profili")

    #%% Gunes Enerji Santralleri Kurulu Guc ve Proje Kapasiteleri
    data_ = get_project_table(spp_project_table, type_)
    save_to_json(data_, "Gunes Enerji Santralleri Kurulu Guc ve Proje Kapasiteleri")

    #%% Isletmedeki Gunes Enerji Santralleri
    data_ = get_table(spp_table, type_)
        
    driver.close()