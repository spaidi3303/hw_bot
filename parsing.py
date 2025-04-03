from datetime import datetime
from playwright.async_api import async_playwright
import re

async def log_ps(login: str, password: str) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://dnevnik.pravgym.ru/')
            login_field = page.locator('input[name=login]')
            password_field = page.locator('input[name=password]')
            await login_field.fill(login)
            await password_field.fill(password)
            await page.click('button[type=submit]')
            await page.locator('tr').first.wait_for()
            return True
    except:
        return False



async def parse(login: str, password: str) -> list[str, str, int]:
    async with async_playwright() as p:
        date = get_trimestr()
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://dnevnik.pravgym.ru/')
        login_field = page.locator('input[name=login]')
        password_field = page.locator('input[name=password]')
        date_field = page.locator('input[name=date]')
        await login_field.fill(login)
        await password_field.fill(password)
        await date_field.fill(date)
        await page.click('button[type=submit]')
        await page.locator('tr').first.wait_for()
        table_rows = (await page.locator('tr').all())[1:]
        grades = []
        for row in table_rows:
            try:
                date, subject, grade = (await row.all_inner_texts())[0].split('\t')
            except ValueError:  # таблица закончилась
                continue
            grades.append((date, subject, int(grade)))
        await browser.close()
        return grades


async def parse_all(login: str, password: str) -> list[str, str, int]:
    async with async_playwright() as p:
        date = get_trimestr()
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://dnevnik.pravgym.ru/')
        login_field = page.locator('input[name=login]')
        password_field = page.locator('input[name=password]')
        date_field = page.locator('input[name=date]')
        await login_field.fill(login)
        await password_field.fill(password)
        await date_field.fill(date)
        await page.click('button[type=submit]')
        await page.locator('tr').first.wait_for()
        table_rows = (await page.locator('tr').all())[1:]
        grades = []
        array = []
        for row in table_rows:
            array.append(await row.all_inner_texts())
        index_start = array.index(['ПредметСр. баллОценки'])
        index_finish = array.index(['ПредметПериодОценка'])
        grades = array[index_start+1:index_finish]
        res_array = []
        for i in grades:
            text = i[0]
            lesson = re.match(r"\D*", text).group()
            bal = re.search(r"\d\.\d\d", text).group()
            bal_match = re.search(r"\d\.\d\d", text)
            marks = re.findall(r"\d+", text[bal_match.end():])
            res_array.append((lesson, bal, marks))
        await browser.close()
        return res_array


def get_trimestr() -> datetime:
    today = datetime.now()
    current_year = today.year
    first_tr_date = datetime.strptime(f"{current_year}-09-01", "%Y-%m-%d")
    second_tr_date = datetime.strptime(f"{current_year}-11-18", "%Y-%m-%d")
    third_tr_date = datetime.strptime(f"{current_year}-02-23", "%Y-%m-%d")
    if today >= third_tr_date:
        return third_tr_date.strftime("%Y-%m-%d")
    elif today >= second_tr_date:
        return second_tr_date.strftime("%Y-%m-%d")
    elif today >= first_tr_date:
        return first_tr_date.strftime("%Y-%m-%d")
