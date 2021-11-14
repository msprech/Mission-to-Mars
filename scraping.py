

# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt



# In[150]:


def scrape_all():
    #initiate healess driver for deployment 
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)
    hemisphere = hemispheres(browser)
    
    #run scraping functions and store in dict 
    data = {
        "news_title": news_title, 
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser), 
        "facts": mars_facts(),
        "hemispheres": hemisphere,
        "last_modified": dt.datetime.now()
    }
    
    browser.quit()
    return data


# ### Visit the NASA Mars News Site



def mars_news(browser):
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    
    #convert browser html to soup object 
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    try: 
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')
    
        #parent element to find first a tag and save
        news_title = slide_elem.find('div', class_='content_title').get_text()
    
        #parent element to find paragraph text 
        news_paragraph = slide_elem.find('div', class_='article_teaser_body').get_text()
        news_paragraph
        
    except AttributeError:
        return None, None
    
    return news_title, news_paragraph



# ### JPL Space Images Featured Image



def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    #find and click full image 
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()
    
    #parse html w soup 
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    #try/except 
    try: 
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None 
    
    #base url for absolute 
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url 


# ### Mars Facts



def mars_facts(): 
    try: 
        #use read to scrape into df 
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        
    except BaseException:
        return None 
    
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
        
    #convert to html 
    return df.to_html()
        


# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres



# 1. Use browser to visit the URL 
def hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    
    hemisphere_image_urls = []
    results = hemi_soup.find('div', class_='collapsible results')
    items = results.find_all('div', class_='item')
    
    for item in items:
        hemisphere = {}
        title = item.find('h3').text
        links = item.find('a', class_='product-item')['href']
        whole_url = f'https://marshemispheres.com/{links}'
        
        browser.visit(whole_url)
        html = browser.html
        hemi_soup = soup(html, 'html.parser')
        
        img_url = browser.links.find_by_partial_text('Sample')['href']
        
        hemisphere['img_url'] = img_url
        hemisphere['title'] = title
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()
        
    return hemisphere_image_urls




if __name__ == "__main__":
    print(scrape_all())

