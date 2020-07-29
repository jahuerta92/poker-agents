import os
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

'''
CHUNK PARA EXTRAER JUGADORES Ad-hoc
from selenium import webdriver
import pickle

browser = webdriver.Firefox()

URL_0 = 'https://www.winamax.es/challenges-winamax_expresso_clasificacion-expresso-de-050-eur-a-3-eur'
URL_1 = 'https://www.winamax.es/challenges-winamax_expresso_clasificacion-expresso-de-4-eur-a-10-eur'
URL_2 = 'https://www.winamax.es/challenges-winamax_expresso_clasificacion-expresso-de-16-eur-a-50-eur'
URL_3 = 'https://www.winamax.es/challenges-winamax_expresso_clasificacion-expresso-de-100-eur-a-250-eur'

def get_players(b, url):
    TABLE_WINAMAX_XPATH = '/html/body/div[3]/div/div[2]/section/div/div/section/div/div/div[2]/form/table'

    b.get(url)
    table = b.find_element_by_xpath(TABLE_WINAMAX_XPATH)
    player_list = []
    for i in table.find_elements_by_xpath('.//tr'):
        prop = [j.get_attribute('innerText') for j in i.find_elements_by_xpath('.//td')]
        if len(prop) == 3:
            player_list.append(prop[1])
    return player_list[:-2]

players = set(get_players(browser, URL_0) + get_players(browser, URL_1) + get_players(browser, URL_2) +  get_players(browser, URL_3))
control = {'etilEnipS', 'frimija26', 'LACHATATATA', 'Cocochamelle', 'Ryujin', 'D0ntCryBB', 'BTCto1M', 'Cesar Polska', 'rorro29', 'Hari86'}
bots = {'kelly59242'}

players.update(control)
players.update(bots)

with open('player_master_list.pkl', 'wb') as f:
    pickle.dump(players, f)

'''

DATASET_DIR = './dataset'

with open('player_master_list.pkl', 'rb') as f:
    PLAYERS = pickle.load(f)

#PLAYERS = {'etilEnipS', 'frimija26', 'LACHATATATA', 'Cocochamelle', 'Ryujin', 'D0ntCryBB', 'BTCto1M', 'Cesar Polska', 'rorro29', 'Hari86', 'kelly59242'}
URL_FORMAT = 'https://es.sharkscope.com/#Player-Statistics//networks/Winamax.fr/players/{}'
URL_LOGIN = 'https://es.sharkscope.com/#'
JS_GAIN_OT = '''var dt = window.Highcharts.charts[1].series[1].data;
                var result_x = [], result_y = [], result_date = [];
                for(key in dt) { result_x.push(dt[key].options.x);
                                 result_y.push(dt[key].options.y);
                                 result_date.push(dt[key].options.z);}
                var result = [result_x, result_y, result_date];
                return result
             '''

JS_RAKE_GAMES = 'return window.Highcharts.charts[3].series[0].processedYData' # Games
JS_RAKE_ROI = 'return window.Highcharts.charts[3].series[1].processedYData' # ROI
JS_RAKE_RAKE = 'return window.Highcharts.charts[3].series[2].processedYData' # Rake
JS_RAKE_X = '''var dt = window.Highcharts.charts[3].series[0].data;
               var result = [];
               for(key in dt) { result.push(dt[key].category);;}
               return result
            '''

CREDENTIALS = {'user': 'octa.mad@gmail.com', 'pass': '34pepe34'}
LOGIN_JS = 'return window.Login("{}","{}")'
LOGOUT_JS = 'return window.Logout()'

CHART_SELECTOR = '.DetailedGraphsSelect'
ROW_SELECTOR = '# mainplayergrid-row-1 > td:nth-child(2) > span:nth-child(1) > span:nth-child(1) > a:nth-child(1)'
CHECKBOX_XPATH = '//*[@id="cb_mainplayergrid"]'
TRASH_XPATH = '/html/body/div[2]/div[2]/div[1]/div[5]/div[3]/div/div[5]/div/table/tbody/tr/td[1]/div/div[1]/div/span'
CONTINUE_XPATH = '/html/body/div[18]/div[3]/div/button[1]/span'
ZERO_ROW_XPATH = '/html/body/div[2]/div[2]/div[1]/div[5]/div[3]/div/div[3]/div[4]/div/table/tbody/tr[2]/td[2]/span/span[1]/a[1]'

'''
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False)
'''
browser = webdriver.Firefox()
browser.get(URL_LOGIN)
browser.implicitly_wait(10)
browser.execute_script(LOGIN_JS.format(CREDENTIALS['user'], CREDENTIALS['pass']))

init = True

wait = WebDriverWait(browser, 10)


def select_player_graph(w, b, p, init=False):
    b.get(URL_FORMAT.format(p))
    b.implicitly_wait(5)
    check = b.find_elements_by_xpath(ZERO_ROW_XPATH)
    if len(check) > 0:
        play = check[0]
        if not init:
            play.click()
        return True
    print(p)
    return False


def clear_player_graph(w, b):
    w.until(EC.element_to_be_clickable((By.XPATH, CHECKBOX_XPATH))).click()
    w.until(EC.element_to_be_clickable((By.XPATH, TRASH_XPATH))).click()
    b.execute_script('window.Highcharts.charts.length = 0')
    try:
        b.find_element_by_xpath(CONTINUE_XPATH).click()
        return None
    except:
        return None
    #w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.delete'))).click()


from banned import banned


for player in PLAYERS:
    if '{}.pkl'.format(player) not in [f for f in os.walk(DATASET_DIR)][0][2] and player not in banned:
        #print(browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[1]/b').text)
        check = select_player_graph(wait, browser, player, init)
        if not check:
            init = False
            continue
        selector = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, CHART_SELECTOR)))
        Select(selector).select_by_value('Stakes')

        n_games, gain, date = browser.execute_script(JS_GAIN_OT)
        y_games = browser.execute_script(JS_RAKE_GAMES)
        roi = browser.execute_script(JS_RAKE_ROI)
        rake = browser.execute_script(JS_RAKE_RAKE)
        game_value = browser.execute_script(JS_RAKE_X)
        player_dict = {'gain_series': {'n_games': n_games,
                                        'gain': gain,
                                        'date': date},
                        'rake_series': {'n_games': y_games,
                                        'roi': roi,
                                        'rake': rake,
                                        'game_value': game_value}}

        Select(selector).select_by_value('ProfitHistory')
        with open(os.path.join(DATASET_DIR, '{}.pkl'.format(player)), 'wb') as f:
            pickle.dump(player_dict, f)
        init = False

        clear_player_graph(wait, browser)
        browser.delete_all_cookies()

'''
YEARS = range(2007, 2019)
SITES = ['Poker Stars', 'partypoker', 'Full Tilt Poker', 'Carbon Poker', 'Ongame']
ITEMS_PER_PAGE = 250

SITES_XPATH = "/html/body/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr[2]/td[1]/select/option[text()='{}']"
PERIOD_XPATH = "/html/body/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr[2]/td[3]/select[@name='s3']/option[text()='Year {}']"
TABLE_XPATH = "/html/body/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table"
STATS_XPATH = "/html/body/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[5]/td/table/tbody/tr[18]"
NEXT_XPATH = "/html/body/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/img[3]"

ROOT_SITE = "http://www.officialpokerrankings.com/"
LEADERBOARD_SITE = "http://www.officialpokerrankings.com/pokerleaderboards.html"

browser = webdriver.Firefox()

browser.get(LEADERBOARD_SITE)


from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(browser)


def click_on_row(row):
    actions.move_to_element(row).click().perform()
    return None


print('Beggining search of player names')
with open("player.csv", 'w', buffering=20*(1024**2)) as output:
    for year in YEARS:
        for site in SITES:
            print('Searching on site "{}" for year {}'.format(site, year))

            browser.find_element_by_xpath(SITES_XPATH.format(site)).click()
            browser.find_element_by_xpath(PERIOD_XPATH.format(year)).click()

            continue_search = True

            while continue_search:
                player_table = browser.find_element_by_xpath(TABLE_XPATH)
                player_rows = player_table.find_elements(By.TAG_NAME, "tr")
                continue_search = len(player_rows) == 251

                for row in player_rows[1:]:
                    rank, _, player, *_ = [it.text for it in row.find_elements(By.TAG_NAME, "td")]
                    if player != 'Hidden':
                        print('Added player {} from site {} on year {}'.format(player, site, year))
                        output.write('{};{};{};{}\n'.format(rank, player, site, year))

                browser.find_element_by_xpath(NEXT_XPATH).click()
                
'''
