from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PLAYERS = {'etilEnipS', 'frimija26', 'LACHATATATA', 'Cocochamelle', 'Ryujin', 'D0ntCryBB', 'BTCto1M', 'Cesar Polska', 'rorro29', 'Hari86'}
URL_FORMAT = 'https://es.sharkscope.com/#Player-Statistics//networks/Winamax.fr/players/{}'
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
browser = webdriver.Firefox()
result_dict = dict()
for player in PLAYERS:
    browser.get(URL_FORMAT.format(player))
    WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "highcharts-root")))

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
    result_dict[player] = player_dict

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