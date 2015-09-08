import bs4
import requests
import time
import logging
import traceback

def main():
    url = "http://www.iol.co.za/motoring/industry-news/sa-s-top-100-vehicle-sales-august-1.1909057#.Ve8wXdOqqko"
    #url = "http://www.iol.co.za/motoring/industry-news/top-100-july-vehicle-sales-slide-1.1894970#.Ve8199Oqqko"
    
    companies = []
    models = []
    
    # Scrape!
    session = requests.session()
    response = session.get(url)
    content = response.text
    soup = bs4.BeautifulSoup(content, "html.parser")
    
    article = soup.find("div", "article_column")
    
    company_mode = model_mode = False
    
    for paragraph in article.find_all("p"):
        str = paragraph.text
        if "TOP COMPANIES" in str:
            company_mode = True
            continue
        if "TOP 100 REPORTED SALES" in str:
            company_mode = False
            model_mode = True
            continue
        if "excludes" in str:
            model_mode = False
        if company_mode:
            name = str[str.find(".")+1:str.rfind("-")].strip()
            quant = int(str[str.rfind("-")+1:].strip().replace(' ',''))
            companies.append({"name" : name, "total_sales" : quant})
        if model_mode:
            make_model = str[str.find(".")+1:str.rfind("-")].strip()
            make = make_model.split(" ")[0]
            model = make_model[len(make)+1:]
            quant = int(str[str.rfind("-")+1:].strip())
            models.append({"make" : make, "model" : model, "sales" : quant})
              
        
    for company in companies:
        print "%s %s" % (company["name"], company["total_sales"])
        
    for model in models:
        print "%s %s %s" % (model["make"], model["model"], model["sales"])
    
main()