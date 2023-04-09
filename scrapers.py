from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
import itertools
import urllib
import json
import pickle
import pandas as pd
import os
import random 
import pyautogui as pt






'''Insert Here Your Research Data'''

LEVEL = ['internship']
CITY = ['Milan']
ROLE = ['','data analyst','data engineer','data scientist', 'intern', 'finance'] 
COMPANY = ['Mediobanca']


'''Insert Here Your Data'''

EMAIL='YOUR_EMAIL'
PASSWORD='YOUR_PASSWORD'
DIRECTORY='YOUR_OUTPUT_FOLDER'
CHROME_PATH='YOUR_CHROME_DRIVER_PATH'









class Scraper():
    def __init__(self,verbose=False) -> None:
        self.verbose = verbose
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_experimental_option('detach', True)
        
        self.driver = webdriver.Chrome(service=Service(CHROME_PATH),options=options)
        
    
    
    def _log_in(self):
        email = EMAIL
        password = PASSWORD
        
        
        self.driver.get('https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1&hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
        self.driver.find_element(By.ID, 'identifierId').send_keys(email)
        self.driver.find_element(By.CSS_SELECTOR, '#identifierNext > div > button > span').click()

        password_selector = "#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input"
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, password_selector)))

        
        self.driver.find_element(By.CSS_SELECTOR, password_selector).send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, '#passwordNext > div > button > span').click()

        time.sleep(1)
        
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open("cookies.pkl", "wb"))

    
    def _save_df(self):
        os.chdir(DIRECTORY)
        if os.path.exists(f'old_{self.__class__.__name__}.xlsx'):
            print('DataFrame loaded.')
            old = pd.read_excel(f'old_{self.__class__.__name__}.xlsx')
            new = self.DF
            old = pd.concat([old, new], axis=0)


            fd=old[old['id']=='-']
            df=old[old['id']!='-']
            df.drop_duplicates(subset=['id'], keep='first',inplace=True) #first, so that it only remains the one you could have already applied for. 
            old = pd.concat([df,fd],axis=0)
            old.reset_index(drop=True, inplace=True)


        else:
            old = self.DF
        
        print('DataFrame saved.')
        old.to_excel(f'old_{self.__class__.__name__}.xlsx',index=False)
        

    
    #def scroll_into_view(self, element):
       #self.driver.execute_script('arguments[0].scrollIntoView(true);', element)




class Indeed(Scraper):
    def __init__(self):
        super().__init__(verbose=False)

        self.DF = pd.DataFrame()

        level = LEVEL
        city = CITY
        role = ROLE
        company = COMPANY


        
        self._log_in()
        self.DF = pd.DataFrame()
        for ci, le, r, co in itertools.product(city, level, role, company):
            self.n = 0
            self.check = True
      
            while self.check:



                link = f'https://it.indeed.com/jobs?q={le}+{r}+{co}&l={ci}&vjk=691c089259c3915c&start={self.n}'.replace(
                    ' ','+') #replace 
                print(link)
                
                self.driver.get(link)
                try:
                    self._scrape_page()
                except ElementClickInterceptedException:
                    print('stupid alert')
                    time.sleep(3)
                    pt.click(1135,241,button='left')
                    time.sleep(1)
                    pt.click(877,422,button='left')
                    time.sleep(2)
                    self._scrape_page()
                    
                self.check_page()



    
        

        #self.DF.drop_duplicates(subset=['role'], keep='last',inplace=True)
        self.DF.reset_index(drop=True, inplace=True)

        self.DF['submitted'] = '-'
        self.DF['answer'] = '-'
        self.DF['outcome'] = '-'


        self._save_df()


        #self.DF.to_excel('inded.xlsx',index=False) già memorizzato


        print("That's all folks.")
        self.driver.quit()
            

    def check_page(self):
        '''Luckly enough, you'll scrape a page more (onlty to search for duplicates later and eventually stop going to the next page), 
        instead of thinking a way to scrape multiple pages. If it has just one page, it will go onto scraping the same one twice, 
        otherwise it will go on until the results of one pages won't be detected as already in the df, as duplicates. Other way, it works just fine
        (or good enoug).'''

        if len(self.DF[self.DF.duplicated(['id'])]) > 0:
            self.DF.drop_duplicates(subset=['id'], keep='last',inplace=True)
            self.check = False
        else:
            self.n += 10
    
    
    def _scrape_page(self):

        self.trafiletti = self.driver.find_elements(By.XPATH,'//div[@class="job_seen_beacon"]')

        LLL = self.driver.find_elements(By.XPATH, '//li//td//a')

        self.IDS = [el.get_attribute('id') for el in LLL if len(el.get_attribute('id'))>1]
        self.LINKS = [el.get_attribute('href') for el in LLL if len(el.get_attribute('id'))>1]


        for i, el in enumerate(self.trafiletti):
            self.driver.execute_script('arguments[0].scrollIntoView(true);', el)
            el.click()
            time.sleep(1)
            job = self._get_job(i,el)

            self.df = pd.DataFrame(job, index=[i])
            self.DF = pd.concat([self.DF, self.df],axis=0)
            #print(self.DF)
            time.sleep(random.randint(1, 5))
        

    def _get_job(self,i,el):

        values = self.driver.find_element(By.ID,"mosaic-provider-jobcards").find_elements(By.XPATH,"//td[@class='resultContent']")[i].text.split('\n')

        if any(x in values[1] for x in ['nuovo','annuncio','new']):
            values.pop(1)
        else:
            if list(values[1])[-2] == ',':
                values[1] = ''.join(list(values[1])[:-3])

        return {
            'role': values[0],
            'company':values[1],
            'location': values[2],
            'days':self._get_days(el),
            'platform':'Indeed',
            'id' : self.IDS[i],#self._get_id(i),
            'description' : self._get_description(),
            'link': self.LINKS[i],#self._get_link(i)
        }
    

    def _get_description(self):
    
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
            
            description = self.driver.find_element(By.ID,'jobDescriptionText').text
            
            self.driver.close()
            self.driver.switch_to.window(window_name=self.driver.window_handles[0])
            
        else:
            description = self.driver.find_element(By.ID,'jobDescriptionText').text

        return description
    

    def _get_id(self,i):
        el =self.driver.find_element(By.ID,"mosaic-provider-jobcards").find_elements(By.XPATH,"//td[@class='resultContent']//a")[i].get_attribute('id')
        if el=='':
            return '-'
        else:
            return el

        
    def _get_link(self,i):
        return self.driver.find_element(By.ID,"mosaic-provider-jobcards").find_elements(By.XPATH,"//td[@class='resultContent']//a")[i].get_attribute('href')


    def _get_days(self, el):
        o = self.driver.execute_script('return arguments[0].textContent;',el)
            
        if 'Posted' in o:
            return o.split('Posted')[1].split(" ")[0]

        elif 'Employer' in o:
            return o.split('EmployerUltimo accesso ')[1].split(" ")[0]
    


class Gjobs(Scraper):
    def __init__(self):
        super().__init__(verbose=False)
        
        self.DF = pd.DataFrame()
        
        city = CITY
        level = LEVEL
        role = ROLE
        company = COMPANY
        
    
        self._log_in()

        
        for ci, le, r, co in itertools.product(city, level, role, company):
            link = f'https://www.google.com/search?q={ci} {le} {r} {co}&oq=google+jobs&aqs=chrome..69i57j69i64.3549j0j7&sourceid=chrome&ie=UTF-8&ibp=htl;jobs&sa=X&ved=2ahUKEwiWwpCOvvT9AhXZRPEDHaMzApwQutcGKAF6BAgQEAU&sxsrf=AJOqlzXS7Qu0EqlQQHKyQMD5hIb9YzQdzw:1679658123034#htivrt=jobs&fpstate=tldetail&htilrad={50}.0&htidocid=NWVIsfNjDkwAAAAAAAAAAA%3D%3D'.replace(
                    ' ', '+') #replace
            #print(link)
            self.driver.get(link)
            
            self._scrape_page()
        
        self.DF.drop_duplicates(subset=['id'], keep='last',inplace=True)
        self.DF.reset_index(drop=True, inplace=True)

        self.DF['submitted'] = '-'
        self.DF['answer'] = '-'
        self.DF['outcome'] = '-'


        self._save_df()

        print("That's all folks.")
        self.driver.quit()
            
        
        

            
    def _scrape_page(self):

        
        self._formatta_liste() 
         
        for i, el in enumerate(self.trafiletti):
            self.driver.execute_script('arguments[0].scrollIntoView(true);', el) 
            time.sleep(1)
            el.click()
                
            self.job_container = self.driver.find_element(
                                                By.XPATH, '//div[@class="whazf bD1FPe"]')
            

            parsed_url = urllib.parse.urlparse(self.driver.current_url)
            self._id = urllib.parse.parse_qs(parsed_url.fragment)['htidocid'][0]
            try:
                job = self._scrape_job(el.text, i)
                self.df = pd.DataFrame(job, index=[i])
                self.DF = pd.concat([self.DF, self.df],axis=0)

            except:
                print('something went wrong')
                continue
            #try except qui dovrebbe garantire che json funzioni

        
    def _formatta_liste(self):
   
        for _ in range(3):
            time.sleep(1)
            self.trafiletti = self.driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
            try:
                self.driver.execute_script('arguments[0].scrollIntoView(true);', self.trafiletti[-1])
            except IndexError:
                print('la chiamata è avvenuta prima che la lista "trafiletti" caricasse, dunque "self.trafilett[-1]" su [] dava errore IndexError;'+
                    'oppure non ci sono risultati. Continua'+
                    'oppure Google si mette di mezzo')
                pass
    

        self.trafiletti.reverse()         
        
        self.l = [self.driver.execute_script('return arguments[0].textContent;', i) for i in self.driver.find_elements(By.XPATH, '//div[@class="KKh3md"]')]
        self.l.reverse()

        for i, number in enumerate(self.l):
            try:
                if 'day' in number:
                    number = float(number.split(' ')[0])
                elif 'hour' in number:
                    number = float(number.split(' ')[0])/24
                elif 'month' in number:
                    number = float(number.split(' ')[0])*31
                else:
                    #number = 'NA'
                    number = '-'
            except:
                number = number.split(' ')[0]
                print('potrebbe esserci scritto 30+')

            self.l[i] = number
        
            
            
            
    def _scrape_job(self, role, i):
        return {
            'role': role,
            'company': self._scrape_company(),
            'location': self._scrape_location(),
            'days': self._scrape_days(i),
            'platform': self._scrape_platform(),
            'id': self._scrape_id(),
            'description': self._scrape_description(),
            'link': self._scrape_link()
            
        }
            
        
    def _scrape_days(self,i):
        return self.l[i]
        
        
    
    def _scrape_id(self):
        return self._id

    
    def _scrape_company(self):
        self.company = self.job_container.find_element(
                    By.XPATH, './/div[@class="nJlQNd sMzDkb"]').text
        return self.company

    def _scrape_location(self):
        self.location = self.job_container.find_element(
                By.XPATH, './/div[@class="sMzDkb"]').text
        return self.location
    
    
    def _scrape_description(self):
        try:
            button = self.driver.find_element(
                        By.XPATH, '//div[@class="whazf bD1FPe"]//div[@jsname="mKTrKf"]')

            self.driver.execute_script('arguments[0].scrollIntoView(true);', button)


            ActionChains(self.driver).move_to_element(button).click(button).perform()   



        except NoSuchElementException:
            pass

        except ElementNotInteractableException:
            print('hai premuto il pulsante per la descrizione. Però poi hai ri-runnato il programma'+
                    'con la descrizione già aperta, dunque viene fuori questo errore')




        self.description = self.job_container.find_element(
                            By.XPATH, './/span[@class="HBvzbc"]').text
    
        
        return self.description
    
    
    def _scrape_platform(self):
        self.platform = self.job_container.find_element(By.XPATH,f".//a[@data-encoded-docid='{self._id}']//span").text
        return self.platform
            
            
    def _scrape_link(self):
        '''lo chiamo linko per distinguerlo dal link di google jobs;
        linko è il link della piattaforma su cui applicare'''
        self.linko = self.job_container.find_element(By.XPATH,f".//a[@data-encoded-docid='{self._id}']").get_attribute('href')
        return self.linko
    
    
                            




if __name__ == '__main__':
    Indeed()
    Gjobs()


