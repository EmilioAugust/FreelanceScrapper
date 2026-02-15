import re

def clean_about_buyer(text: str):
    lines = text.split("\n")
    result = [line.split(": ") for line in lines if "Нанято" in line]
    if result:
        for r in result:
            data = r[1]
        return int(data[:-1])
    else:
        return "Нету данных по % нанятости"

def clean_budget_sign(text: str):
    return int(text[:-1].replace(" ", ""))

def clean_time_response(text: str):
    datas = []
    lines = text.split("\n")
    result = [line.split(": ") for line in lines]
    data = result[1][0].replace("\xa0", "")
    clean_data = data.split(":")
    datas.append(result[0][1])
    datas.append(int(clean_data[1]))
    return datas

def parse_time_left(time_str):
    days = 0
    hours = 0

    day_match = re.search(r'(\d+)\s*д', time_str)
    hour_match = re.search(r'(\d+)\s*ч', time_str)

    if day_match:
        days = int(day_match.group(1))
    if hour_match:
        hours = int(hour_match.group(1))

    return days * 24 + hours

def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n

# WAVE utils for kwork
def access_time_bonus(hours_left):
    hours = parse_time_left(hours_left)
    if hours >= 120: return 2
    if hours >= 48: return 1
    if hours >= 24: return 0
    if hours >= 6: return -1
    return -2

def effort_time_modifier(hours_left):
    hours = parse_time_left(hours_left)
    if hours >= 120: return 1
    if hours >= 48: return 0
    if hours >= 12: return -1
    return -2

def response_score(responses):
    if responses < 2: return 9
    if responses < 5: return 7
    if responses < 10: return 5
    if responses < 20: return 3
    return 1


# WAVE calcs for kwork
def calc_worth(price):
    if price < 1000: return 2
    if price < 3000: return 4
    if price < 7000: return 6
    if price < 15000: return 8
    return 10

def calc_access(responses, hours_left):
    score = response_score(responses)
    score += access_time_bonus(hours_left)
    return clamp(score, 0, 10)

def calc_validity(hired_percent):
    if isinstance(hired_percent, str): return 5
    if hired_percent < 30: return 2
    if hired_percent < 50: return 5
    if hired_percent < 70: return 7
    if hired_percent < 85: return 9
    return 10

def calc_effort(price, hours_left):
    score = price
    score += effort_time_modifier(hours_left)
    return clamp(score, 0, 10)

def calc_wave(worth, access, validity, effort):
    result = 0.30 * worth + 0.30 * access + 0.25 * validity + 0.15 * effort
    return result



# WAVE utils for fl.ru
def clean_budget(text: str):
    if text == "по договоренности":
        return "по договоренности"
    elif text == "по результатам собеседования":
        return "по результатам собеседования"
    elif text.startswith("от"):
        ot_line = text.replace("от", "").strip()
        result = ot_line.replace("\xa0", "")
        formatted_result = int(result.replace("₽", ""))
        return formatted_result
    elif text.startswith("до"):
        ot_line = text.replace("до", "").strip()
        result = ot_line.replace("\xa0", "")
        formatted_result = int(result.replace("₽", ""))
        return formatted_result
    elif text:
        result = []
        lines = text.split("–")
        for line in lines:
            new_line = line.replace("\xa0", "").strip()
            result.append(int(new_line.replace("₽", "")))
        return result
    else:
        return int(text[:-1].replace(" ", ""))

def clean_views(text: str):
    if text.startswith("больше"):
        new_text = text.split(" ")[-1]
        return int(new_text)
    elif text:
        return int(text)

def clean_responses(text: str):
    if "Нет" in text.strip():
        return "Нет ответов"
    elif "ответ" in text:
        new_text = text.split(" ")[1]
        return int(new_text)
    
def clean_time(text: str):
    minutes = 0

    day_match = re.search(r'(\d+)\s*д', text)
    if day_match:
        minutes += int(day_match.group(1)) * 1440

    hour_match = re.search(r'(\d+)\s*час', text)
    if hour_match:
        minutes += int(hour_match.group(1)) * 60

    min_match = re.search(r'(\d+)\s*мин', text)
    if min_match:
        minutes += int(min_match.group(1))

    return int(minutes)

def time_bonus(minutes_since_post: int):
    minutes = clean_time(minutes_since_post)
    if minutes < 30:
        return 2
    if minutes <= 120:
        return 1
    if minutes <= 360:
        return 0
    if minutes <= 1440:
        return -1
    return -2
        

# WAVE calcs for fl.ru
def calc_worth_fl(budget):
    price = clean_budget(budget)
    if price == "по договоренности" or price == "по результатам собеседования":
        return 6    
    elif isinstance(price, list):
        if price[0] < 3000: return 4
        if price[0] < 3000: return 4
        if price[0] < 7000: return 6
        if price[0] < 15000: return 8
        if price[0] < 30000: return 8
        return 10
    else:
        if price < 3000: return 4
        if price < 3000: return 4
        if price < 7000: return 6
        if price < 15000: return 8
        if price < 30000: return 8
        return 10

def calc_access_fl(responses, hours_post):
    offers = clean_responses(responses)
    if isinstance(offers, str):
        return 10
    score = response_score(offers)
    score += time_bonus(hours_post)
    return clamp(score, 0, 10)

def calc_validity_fl(views, responses, budget):
    score = 0
    offers = clean_responses(responses)
    new_views = clean_views(views)
    price = clean_budget(budget)
    if isinstance(offers, str):
        return 10
    else:
        ratio = new_views / max(offers, 1)

    if ratio < 3:
        score = 9
    elif ratio < 6:
        score = 7
    elif ratio < 10:
        score = 5
    else:
        score = 3

    if price == "по договоренности" or price == "по результатам собеседования":
        return 6

    return clamp(score, 0, 10)

def calc_effort_fl(hours_post, budget):
    price = clean_budget(budget)
    score = time_bonus(hours_post)

    if price == "по договоренности" or price == "по результатам собеседования":
        score += 1    
    elif isinstance(price, list):
        if price[0] < 3000: score -= 1
        if price[0] < 15000: score += 1

    return clamp(score, 0, 10)

def calc_wave_fl(worth, access, validity, effort):
    result = 0.30 * worth + 0.25 * access + 0.30 * validity + 0.15 * effort
    return result