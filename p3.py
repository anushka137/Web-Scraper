# project: p3
# submitter: achandrashe4
# partner: none
# hours: 10

import os, zipfile, time
import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.DFSorder.clear()
        self.visited.clear()
        self.dfs_recursive(node)
        
    def dfs_recursive(self, node):
        self.visited.add(node)
        
        for child in self.go(node):
            if not child in self.visited:
                self.dfs_recursive(child)
        
    def bfs_search(self, node):
        self.visited.clear()
        self.BFSorder.clear()
        todo = []
        todo.append(node)
        self.visited.add(node)
        
        while len(todo) > 0:
            n = todo.pop(0)
            for child in self.go(n):
                if not child in self.visited:
                    self.visited.add(child)
                    todo.append(child)

class FileScraper(GraphScraper):
    def __init__(self):
        super().__init__()
        if not os.path.exists("Files"):
            with zipfile.ZipFile("files.zip") as zf:
                zf.extractall()

    def go(self, node):
        path = os.path.join("Files/", node + ".txt")
        with open(path) as f:
            lines = list(f)
            
            children = lines[1].strip().split(" ")
            
            bfs_string = lines[2].strip().split(" ")
            self.BFSorder.append(bfs_string[1])
            
            dfs_string = lines[3].strip().split(" ")
            self.DFSorder.append(dfs_string[1])
        return children
    
class WebScraper(GraphScraper):
    # required
    def	__init__(self, driver=None):
        super().__init__()
        self.driver = driver
        
    def go(self, url):
        self.driver.get(url)
        
        links = self.driver.find_elements_by_tag_name("a")
        bfs_button = self.driver.find_element_by_id("BFS")
        dfs_button = self.driver.find_element_by_id("DFS")
        
        bfs_button.click()
        self.BFSorder.append(bfs_button.text)
        
        dfs_button.click()
        self.DFSorder.append(dfs_button.text)
        return [link.get_attribute("href") for link in links]
        
    def dfs_pass(self, start_url):
        self.dfs_search(start_url)
        return "".join(self.DFSorder)
    
    def bfs_pass(self, start_url):
        self.bfs_search(start_url)
        return "".join(self.BFSorder)
    
    def protected_df(self, url, password):
        self.driver.get(url)
        pwd = self.driver.find_element_by_id("password-input")
        pwd.clear()
        pwd.send_keys(password)

        count = 0
        while(True):
            try:
                btn1 = self.driver.find_element_by_id("attempt-button")
                btn1.click()
                time.sleep(1.5)
                btn2 = self.driver.find_element_by_id("more-locations-button")

                row_count = len(self.driver.find_elements_by_tag_name("tr"))
                while count <= row_count:
                    count += 1
                    btn2.click()
                    time.sleep(1)
            except NoSuchElementException:
                break
        df = pd.read_html(self.driver.page_source)
        return df[0]