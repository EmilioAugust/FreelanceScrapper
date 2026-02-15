from playwright.sync_api import sync_playwright
from utils.utils import calc_worth_fl, calc_access_fl, calc_validity_fl, calc_effort_fl, calc_wave_fl

def check_fl(label_filter: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.fl.ru/projects")

        page.wait_for_timeout(2000)

        page.locator(".fl-home-page__spec-link", has_text=label_filter).click()

        page.wait_for_timeout(2000)

        div_class = page.query_selector_all(".pt-24.pb-32.b-page__lenta_item")
        ready_url = "https://www.fl.ru"
        print(f"Нашлось заказов: {len(div_class)}")
        print("================")
        for card in div_class:
            user_found = card.query_selector(".text-7.text-decoration-none")
            if user_found.inner_text() == "Исполнитель определён":
                continue

            title_el = card.query_selector(".text-h5.b-post__title.b-post__grid_title")
            title = title_el.inner_text()

            link_content = title_el.query_selector("a")
            href_value = link_content.get_attribute("href")

            time = card.query_selector(".text-gray-opacity-4")
            time_text = time.inner_text() if time else 0

            watched = card.query_selector(".d-flex.align-items-center.b-post__txt.b-post__txt_float_right")
            watched_text = watched.inner_text()

            responses = card.query_selector(".b-post__txt_float_right.b-page__desktop.text-7")
            responses_text = responses.inner_text() if responses else "Нет"

            budget = card.query_selector(".text-4.text-dark")
            budget_text = budget.inner_text()

            worth = calc_worth_fl(budget_text)
            access = calc_access_fl(responses_text, time_text)
            validity = calc_validity_fl(watched_text, responses_text, budget_text)
            effort = calc_effort_fl(time_text, budget_text)

            result = calc_wave_fl(worth, access, validity, effort)

            print(title)
            print(f"🟢 WAVE: {result:{.2}f} / 10 (чем больше баллов, тем лучше)")
            print(f"W — Деньги: {worth}")
            print(f"A — Конкуренция: {access}")
            print(f"V — Адекватность: {validity}")
            print(f"E — Усилие: {effort}")                                          
            print(f"Перейти к заказу: {ready_url + href_value}")
            print()

        browser.close()
