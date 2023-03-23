import requests
import json
from LOG import TOKEN_API, headers
from datetime import datetime, timedelta
import math
import time


def sleep(timeout, retry=6):
    def the_real_decorator(function):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < retry:
                try:
                    value = function(*args, **kwargs)
                    if value is None:
                        return
                except:
                    print(f'Сон на {timeout} секунд')
                    time.sleep(timeout)
                    retries += 1
        return wrapper
    return the_real_decorator


@sleep(30)
def get_matches(selected_date):
    book = ['1XBet', 'BWin', 'BetFair', 'Betway', '10Bet', 'Ladbrokes', 'YSB88', 'WilliamHill', 'Betclic', 'Pinnacle',
            'PlanetWin365', '188Bet', 'UniBet', 'BetFred', '888Sport', 'CloudBet', 'Betsson', 'Betdaq', 'PaddyPower',
            'SBOBET', 'TitanBet', 'BetAtHome', 'DafaBet', 'Marathonbet', 'BetVictor', 'Everygame', 'Interwetten',
            'Nitrogen', 'Winner', 'BetRegal', 'SkyBet', 'MarsBet', 'Macauslot', 'HG', 'GGBet']
    result_data = []
    print("Гэт матчес запущен")
    url = f"https://api.b365api.com/v3/events/upcoming?sport_id=18&skip_esports=1&day={selected_date}&page=1" \
          f"&token={TOKEN_API}"
    s = requests.Session()
    response = s.get(url=url, headers=headers, timeout=200)
    games = response.json()
    pagination_count = math.ceil(games.get("pager").get("total") / games.get("pager").get("per_page"))
    for page_count in range(1, pagination_count + 1):
        s = requests.Session()
        url = f"https://api.b365api.com/v3/events/upcoming?sport_id=18&skip_esports=1&day={selected_date}" \
              f"&page={page_count}&token={TOKEN_API}"
        r = s.get(url=url, headers=headers, timeout=200)
        data = r.json()
        matches = data.get("results")
        print("Я дошел до сюда")
        for match in matches:
            times = datetime.fromtimestamp(int(match.get("time")))
            if times >= datetime.now():
                match_id = match.get("id")
                print(match_id)
                sr_total_book = 'No'
                sr_handi_book = 'No'
                try:
                    s = requests.Session()
                    url_odds = f"https://api.b365api.com/v2/event/odds/summary?token={TOKEN_API}" \
                               f"&event_id={match_id}"
                    r_odds = s.get(url=url_odds, headers=headers, timeout=500)
                    print(r_odds.status_code)
                    data_odds = r_odds.json()
                    data_cache = {match_id: data_odds}
                    if match_id in data_cache:
                        data_odds = data_cache[match_id]
                        try:
                            t = data_odds.get("results").get("Bet365").get("odds").get("end").get("18_3").get(
                                "handicap")
                            h = data_odds.get("results").get("Bet365").get("odds").get("end").get("18_2").get(
                                "handicap")
                            sr_total_book = float(t)
                            sr_handi_book = float(h)
                        except AttributeError or TypeError:
                            for o in book:
                                try:
                                    data_odd = data_odds.get("results").get(o)
                                    if data_odd:
                                        try:
                                            odds = data_odd.get("odds").get("end")
                                            if "18_2" in odds and sr_handi_book == 'No':
                                                sr_handi_book = odds.get("18_2").get("handicap")
                                            if "18_3" in odds and sr_total_book == 'No':
                                                sr_total_book = odds.get("18_3").get("handicap")
                                            if sr_handi_book != 'No' and sr_total_book != 'No':
                                                break
                                        except AttributeError or TypeError:
                                            continue
                                except (AttributeError, ConnectionError, ConnectionResetError):
                                    print(f"Не извлек данные из {o}")
                                    time.sleep(60)
                                    continue
                    else:
                        print("Пошел заново записывать данные в кэш")
                        r_odds = s.get(url=url_odds, headers=headers, timeout=5000)
                        print(r_odds.status_code)
                        data_odds = r_odds.json()
                        data_cache[match_id] = data_odds
                except requests.exceptions.ConnectionError as e:
                    print('Connection error: ', e)
                    time.sleep(60)
                    continue
                print("Я прошел блок с буками")
                print(sr_handi_book)
                print(sr_total_book)
                timem = times.strftime('%d.%m %H:%M')
                res_h2h = []
                games_h = 0
                total_h = 0
                total_handi_h = 0
                games_a = 0
                total_a = 0
                total_handi_a = 0
                link = f"https://bsportsfan.com/r/{match_id}/{match.get('home').get('name')}-vs-" \
                       f"{match.get('away').get('name')}"
                league_id = int(match.get("league").get("id"))
                url = f"https://api.b365api.com/v1/event/history?token={TOKEN_API}&event_id={match_id}&qty=20"
                r = s.get(url=url, headers=headers, timeout=100)
                data = r.json()
                try:
                    last_home_games = data.get("results").get("home")
                except AttributeError:
                    print("Не смог получить домашнюю историю")
                    time.sleep(60)
                    continue
                for last_home_game in last_home_games:
                    lh_time = last_home_game.get("time")
                    lh_times = datetime.fromtimestamp(int(lh_time))
                    leg = int(last_home_game.get("league").get("id"))
                    if lh_times >= datetime.now() - timedelta(days=90) and leg == league_id:
                        total_home = sum(map(int, last_home_game.get("ss").replace("-", " ").split()))
                        total_h += total_home
                        games_h += 1
                        shet_home = list(map(int, last_home_game.get("ss").replace("-", " ").split()))
                        res_hoz = shet_home[0]
                        res_gues = shet_home[1]
                        if res_hoz > res_gues:
                            if last_home_game.get("home").get("id") == match.get("home").get("id"):
                                handi_h = res_gues - res_hoz
                            else:
                                handi_h = res_hoz - res_gues
                        else:
                            if last_home_game.get("home").get("id") == match.get("home").get("id"):
                                handi_h = res_gues - res_hoz
                            else:
                                handi_h = res_hoz - res_gues
                        total_handi_h += handi_h
                sr_home = games_h
                try:
                    sr_total_home = round(total_h // games_h)
                    sr_handi_home = round(total_handi_h // games_h)
                except ZeroDivisionError:
                    sr_total_home = 0
                    sr_handi_home = 0
                print("Я прошел блок дома")
                try:
                    last_away_games = data.get("results").get("away")
                except AttributeError:
                    print("Не смог получить гостевую историю")
                    time.sleep(60)
                    continue
                for last_away_game in last_away_games:
                    lh_time = last_away_game.get("time")
                    lh_times = datetime.fromtimestamp(int(lh_time))
                    leg = int(last_away_game.get("league").get("id"))
                    if lh_times >= datetime.now() - timedelta(days=90) and leg == league_id:
                        total_away = sum(map(int, last_away_game.get("ss").replace("-", " ").split()))
                        total_a += total_away
                        games_a += 1
                        shet_away = list(map(int, last_away_game.get("ss").replace("-", " ").split()))
                        res_hoz = shet_away[0]
                        res_gues = shet_away[1]
                        if res_hoz > res_gues:
                            if last_away_game.get("home").get("id") == match.get("away").get("id"):
                                handi_a = res_gues - res_hoz
                            else:
                                handi_a = res_hoz - res_gues
                        else:
                            if last_away_game.get("home").get("id") == match.get("away").get("id"):
                                handi_a = res_gues - res_hoz
                            else:
                                handi_a = res_hoz - res_gues
                        total_handi_a += handi_a
                sr_away = games_a
                try:
                    sr_total_away = round(total_a // games_a)
                    sr_handi_away = round(total_handi_a // games_a)
                except ZeroDivisionError:
                    sr_total_away = 0
                    sr_handi_away = 0
                print("Я прошел блок гостей")
                try:
                    last_h2h_games = data.get("results").get("h2h")
                except AttributeError:
                    print("Не смог получить очные встречи")
                    time.sleep(60)
                    continue
                for last_h2h_game in last_h2h_games:
                    time_h2h = last_h2h_game.get("time")
                    times_h2h = datetime.fromtimestamp(int(time_h2h))
                    his_time = datetime.fromtimestamp(int("1640995200"))
                    if times_h2h >= his_time:
                        league_h2h = last_h2h_game.get("league").get("name")
                        time_h2h = times_h2h.strftime('%d.%m.%Y')
                        home_h2h_name = last_h2h_game.get("home").get("name")
                        away_h2h_name = last_h2h_game.get("away").get("name")
                        shcet_h2h = last_h2h_game.get("ss")
                        x = league_h2h+' '+time_h2h+' '+home_h2h_name+' '+"vs"+' '+away_h2h_name + \
                            ' '+shcet_h2h
                        res_h2h.append(x)
                print("Я прошел блок очек")
                sr_total = round((sr_total_home + sr_total_away) // 2)
                sr_handi = round(sr_handi_home - sr_handi_away)
                print(sr_total)
                print(sr_handi)
                if sr_total_book == 'No':
                    dif_total = "No"
                else:
                    dif_total = abs(float(sr_total_book) - sr_total)
                if sr_handi_book == 'No':
                    dif_handi = "No"
                else:
                    dif_handi = abs(float(sr_handi_book) - sr_handi)
                print("Я получил разницы")
                result_data.append(
                    {
                        "match_name": f"{match.get('home').get('name')} - {match.get('away').get('name')}",
                        "home_name": match.get("home").get("name"),
                        "away_name": match.get("away").get("name"),
                        "link": link,
                        "time": timem,
                        "match_id": match.get("id"),
                        "sr_home": sr_home,
                        "sr_total_home": sr_total_home,
                        "sr_handi_home": sr_handi_home,
                        "sr_away": sr_away,
                        "sr_total_away": sr_total_away,
                        "sr_handi_away": sr_handi_away,
                        "sr_total": sr_total,
                        "sr_handi": sr_handi,
                        "sr_total_book": sr_total_book,
                        "sr_handi_book": sr_handi_book,
                        "dif_total": dif_total,
                        "dif_handi": dif_handi,
                        "h2h": '\n'.join(res_h2h)
                        }
                    )
                print(timem)
                print(f"{match.get('home').get('name')} - {match.get('away').get('name')}")

    with open("all_matches.json", "w", encoding="utf-8") as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)


def main():
    get_matches()


if __name__ == "__main__":
    main()
