import bs4
import requests
import time
import logging
import traceback
import json

def main():

    with open("iol-urls.json") as data_file:    
        data = json.load(data_file)
    
    history = {}
    
    for page in data["pages"]:
        url = page["url"]    
        print page["month"]
        
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
            if ("TOP 100" in str) or ("TOP 50" in str) or ("50 TOP" in str) or ("TOP SELL" in str):
                company_mode = False
                model_mode = True
                continue
            if ("Kia" in str) or ("EXPORTS" in str) or ("Related" in str) or (len(str) < 3):
                model_mode = False
            if company_mode:
                dash_index = max(str.rfind("-"), str.rfind(u'\u2013'))
                name = str[str.find(".")+1:dash_index].strip()
                quant = int(str[dash_index+1:].strip().replace(' ',''))
                companies.append({"name" : name, "total_sales" : quant})
            if model_mode:
                dash_index = max(str.rfind("-"), str.rfind(u'\u2013'))
                dot_index = str.find(".")
                if dot_index is -1:
                    dot_index = str.find("-")
                make_model = str[dot_index + 1 : dash_index].strip()
                make = make_model.split(" ")[0]
                model = make_model[len(make)+1:]
                quant = int(str[dash_index+1:].strip())
                models.append({"make" : make, "model" : model, "sales" : quant})
              
        print "%s companies, %s models" % (len(companies), len(models))
        #for company in companies:
        #    print "%s %s" % (company["name"], company["total_sales"])
        
        for model in models:
            make_model = "%s %s" % (model["make"], model["model"])
            if make_model not in history:
                history[make_model] = {}
            history[make_model][page["month"]] = model["sales"]
    
    with open("history.json", "w") as output_file:
        output_file.write(json.dumps(history, sort_keys = True, indent = 4))
        
def short_list():
    
    with open("history.json") as data_file:    
        data = json.load(data_file)
    
    for model in data:
        popular = False
        for date in range(1501, 1509):
            if str(date) in data[model]:
                if data[model][str(date)] > 150:
                    popular = True
        if popular:
            print model
    
#main()
short_list()