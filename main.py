import time
from fastapi import FastAPI
import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tinydb import TinyDB

app = FastAPI()

db = TinyDB('db.json')


@app.on_event("startup")
def startup_event():
    print("NoSQL Database (TinyDB) is ready to use.")


@app.get("/parse")
def parse_website(start_page: int = 1, limit: int = 1):
    print(f"Starting parser. Start page: {start_page}, Limit: {limit}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    inserted_count = 0

    try:
        for current_page in range(start_page, start_page + limit):
            target_url = f"https://quotes.toscrape.com/page/{current_page}/"
            print(f"Parsing: {target_url}")
            driver.get(target_url)
            time.sleep(2)

            quotes = driver.find_elements(By.CLASS_NAME, "quote")
            if not quotes:
                print(f"No quotes found on page {current_page}, stopping pagination.")
                break

            for elem in quotes:
                text = elem.find_element(By.CLASS_NAME, "text").text
                author = elem.find_element(By.CLASS_NAME, "author").text
                author_url = elem.find_element(By.TAG_NAME, "a").get_attribute("href")

                tags_elements = elem.find_elements(By.CLASS_NAME, "tag")
                tags = ", ".join([t.text for t in tags_elements])

                db.insert({
                    "text": text,
                    "author": author,
                    "author_url": author_url,
                    "tags": tags
                })
                inserted_count += 1

        return {"status": "success",
                "message": f"Successfully parsed and inserted {inserted_count} records into TinyDB."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        driver.quit()


@app.get("/data")
def get_data():
    return db.all()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)