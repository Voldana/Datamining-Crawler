from math import fabs
from types import NoneType
from typing_extensions import Required
from BaseCrawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('__main__')

class UIO(BaseCrawler) :
    Course_Page_Url = "https://www.uio.no/english/studies/courses/"
    University = "University of Oslo"
    Abbreviation = "UIO"
    University_Homepage = "https://www.uio.no"
    Professor_Homepage = None
    def get_department_info(self, department):
        a_element = department.find('a')
        Department_Name = a_element.text
        department_Url = self.Course_Page_Url + a_element.get('href')
        
        return Department_Name,department_Url
    def get_courses_of_department(self, department):
        department = requests.get(department).content
        soup = BeautifulSoup(department,'html.parser')
        courses = soup.find('table',{'id':'vrtx-course-description-listing-results'}).find('tbody').find_all('tr')
        courses_urls =[]
        for course in courses :
            course_url = self.University_Homepage + course.find('a').get('href')
            courses_urls.append(course_url)
            print(course_url)
        #check for next pages
        next_element = soup.find('span',{'class':'vrtx-paging-wrapper'})
        if(type(next_element) != NoneType):
            nex = next_element.find('a',{'class':'vrtx-next'})
            if(type(nex) != NoneType):
                courses_urls = courses_urls + self.get_courses_of_department(nex.get('href'))
        return courses_urls
    def get_course_data(self, course):
        course = requests.get(course).content
        soup = BeautifulSoup(course,'html.parser')
        Prerequisites = None
        Outcomes = None
        Objective =None
        RequiredSkill = None
        content = None
        course_header = soup.find('div',{'id':'vrtx-course-title-toc'}).find('h1')
        course_title =' '.join(course_header.text.split()[2:])
        course_credit = h_credit = soup.find('div',{'id':'vrtx-additional-content'}).find('p').text
        #prerequisites_content = soup.find(id='prerequisites')    
        learning_outcomes_content =soup.find(id='learning-outcomes')
        content_div = soup.find(id='course-content')
        if(type(content_div) != NoneType):
            content = self.get_Course_Content(content_div)
        #if(type(prerequisites_content) != NoneType):
        Prerequisites = self.get_Course_Prerequisites(soup)
        if(type(learning_outcomes_content) != NoneType):
            Outcomes = self.get_Course_Outcome(learning_outcomes_content)
        return Prerequisites,Outcomes,Objective,RequiredSkill,course_title,course_credit,content
    def get_Course_Prerequisites(self,course_cont):
        res = course_cont.find(id='prerequisites')
        if(type(res) == NoneType):
            res =[]
            con = course_cont.find(id='vrtx-course-content')
            child =next(con.children)
            while type(child) != NoneType:
                if(type(child.find_next_sibling()) != NoneType and child.find_next_sibling().name == 'h3'):
                    child = child.find_next_sibling()
                    co = []
                    while type(child.find_next_sibling()) != NoneType and child.find_next_sibling().name != 'h3':
                        child = child.find_next_sibling()
                        co.append(child.text)
                    res.append(co)
                else:
                    child = child.find_next_sibling()
        else :
            res = res.text
        return res
    def get_Course_Outcome(self,outcome_div):
        #outcome_sectors = outcome_div.find_all('ul')
        outcome_results = outcome_div.text
        return outcome_results
    def get_Course_Content(self,Content_div):
        return Content_div.text
    def is_valid_department(self,department):
        a_element = department.find('a')
        if(type(a_element) == NoneType) :
            return False
        return True
    def handler(self):
        professor =None
        references =None
        scores = None
        projects = None
        html_content = requests.get(self.Course_Page_Url).content
        soup = BeautifulSoup(html_content, 'html.parser')
        departments = soup.find('div',{'class':'left'}).find_all('h3')
        departments = departments + soup.find('div',{'class':'right'}).find_all('h3')
        for department in departments :
            if(self.is_valid_department(department)):
                try:
                    Department_Name,Department_Url = self.get_department_info(department)
                    courses_urls = self.get_courses_of_department(Department_Url)
                    for course_url in courses_urls :
                      #  print("extracting course data")
                        Prerequisites,outcomes,objectives,skills,c_title,c_credit,c_content = self.get_course_data(course_url)
                        self.save_course_data(
                            self.University, self.Abbreviation,
                        Department_Name,c_title,c_credit,professor,
                        objectives,Prerequisites,skills,
                        outcomes,references,scores,c_content,projects,
                        self.University_Homepage,course_url,self.Professor_Homepage)
                except:
                    print('error in dept :' + str(department))

