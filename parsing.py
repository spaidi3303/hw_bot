from playwright.async_api import async_playwright
import re

async def parse(login: str, password: str) -> list[str, str, int]:
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
        table_rows = (await page.locator('tr').all())[1:]
        grades = []
        for row in table_rows:
            try:
                date, subject, grade = (await row.all_inner_texts())[0].split('\t')
            except ValueError:  # table ended
                continue
            grades.append((date, subject, int(grade)))
        await browser.close()
        return grades

async def parse_all(login: str, password: str) -> list[str, str, int]:
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
    