from playwright.sync_api import sync_playwright
from utils.utils import clean_about_buyer, clean_budget_sign, clean_time_response, calc_worth, calc_access, calc_validity, calc_effort, calc_wave

def check_kwork(hiring_from: str, label_filter: str, inner_label_filter: str | None = None):
    parsed = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto("https://kwork.ru/projects")
        page.wait_for_timeout(2000)
        page.locator("#hiring-from").fill(hiring_from)
        page.wait_for_timeout(2000)
        page.locator(".multilevel-list__label-title", has_text=label_filter).click()
        page.wait_for_timeout(2000)

        if inner_label_filter:
            page.locator(".multilevel-list__label-title", has_text=inner_label_filter).click()
            page.wait_for_timeout(2000)
        else:
            pass
        
        div_class = page.query_selector_all(".wants-card__header-title.breakwords")
        for i, div in enumerate(div_class):
            title = div.inner_text()
            link_content = div.query_selector("a")
            href_value = link_content.get_attribute("href")
            about_buyer = page.locator(".dib.v-align-t.ml10").nth(i).all_inner_texts()
            about_time_response = page.locator(".want-card__informers-row").nth(i).all_inner_texts()
            page.locator(".wants-card__price").nth(i).wait_for(state="visible", timeout=10000)
            price_locator = page.locator(".wants-card__price .d-inline").nth(i).all_inner_texts()

            parsed.append({
                "about_buyer": about_buyer[0],
                "title": title,
                "project_url": href_value,
                "budget": price_locator[0],
                "about_time_response": about_time_response[0]
            })
            
        browser.close()
        print(f"Нашлось заказов: {len(parsed)}")
        print("=======================")

        ready_url = "https://kwork.ru"

        for i in parsed:
            new_about_buyer = clean_about_buyer(i["about_buyer"])
            new_budget = clean_budget_sign(i["budget"])
            formatted_amount = "{:,}".format(new_budget).replace(",", " ")
            new_time_response = clean_time_response(i["about_time_response"])

            worth = calc_worth(new_budget)
            access = calc_access(responses=new_time_response[1], hours_left=new_time_response[0])
            validity = calc_validity(new_about_buyer)
            effort = calc_effort(price=new_budget, hours_left=new_time_response[0])

            result = calc_wave(worth, access, validity, effort)

            if result > 7:

                print(i["title"])
                print(f"💰 Бюджет: {formatted_amount} ₽")
                print(f"🟢 WAVE: {result} / 10 (чем больше баллов, тем лучше)")
                print(f"W — Деньги: {worth}")
                print(f"A — Конкуренция: {access}")
                print(f"V — Адекватность: {validity}")
                print(f"E — Усилие: {effort}")
                print()
                print(f"Перейти к заказу: {ready_url + i["project_url"]}")
                print()
            