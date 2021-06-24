from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import time
import sys


class TaoBao(object):
    """
    get personal purchase list from taobao
    """
    url = 'https://www.taobao.com'
    my_taobao_xpath = '//*[@id="J_SiteNavMytaobao"]/div[1]/a/span'
    bought_xpath = '//*[@id="bought"]'
    next_page_xpath = '//*[@id="tp-bought-root"]/div[3]/div[2]/div/button[2]'

    def __init__(self):
        """
        initialization
        """
        options = Options()
        # options.add_argument("--headless")

        # disable loading pictures to speedup
        # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome('chromedriver.exe', options=options)

    def click_button(self, xpath, timeout=20):
        """
        click a button on the page
        :return:
        """
        button = WebDriverWait(self.browser, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath)
            )
        )
        button.click()

    def open_my_taobao(self):
        """
        login using my taobao account
        :return:
        """
        self.browser.get(self.url)
        self.browser.maximize_window()
        # self.browser.implicitly_wait(40)
        self.click_button(xpath=self.my_taobao_xpath, timeout=120)

    def get_text(self):
        """
        parse the item and return text associated with the item
        :return:
        """

    def click_next_page(self):
        """
        click next page button to get items in next page
        :return:
        """
        self.click_button(self.next_page_xpath)

    def get_order_info(self, orders=None):
        """
        crawl order info in current page
        :return:
        """
        orders = [] if orders is None else orders
        action = ActionChains(self.browser)

        # loop orders
        for i in range(4, 19):
            date_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[1]/tr/td[1]/label/span[2]'
            order_number_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[1]/tr/td[1]/span/span[3]'
            price_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[2]/tr/td[5]/div/div[1]/p/strong/span[2]'
            logistics_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[2]/tr[1]/td[6]/div/div/p[2]'

            # try to get basic info about this order, fail to do so means we hit the end of order list and exit looping
            try:
                date = self.browser.find_element_by_xpath(date_xpath).text
                order_number = self.browser.find_element_by_xpath(order_number_xpath).text
                price = self.browser.find_element_by_xpath(price_xpath).text
            except:
                break

            # try to move mouse to "物流信息" and get the info, fail to do so means there is no "物流信息" for this order
            try:
                action.move_to_element(self.browser.find_element_by_xpath(logistics_xpath)).perform()
                time.sleep(2)
                ship_info = self.browser.find_element_by_class_name('logistics-info-mod__header___2_fWN').text
                ship_company, ship_number = ship_info.replace("：", ",").split(",")
            except:
                ship_company, ship_number = '', ''

            # loop items in "this" order
            items = self.browser.find_elements_by_xpath(f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[2]/tr')
            for j in range(len(items)):
                description_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[2]/tr[{j + 1}]/td[1]/div/div[2]/p[1]/a[1]/span[2]'
                unit_price_xpath = f'//*[@id="tp-bought-root"]/div[{i}]/div/table/tbody[2]/tr[{j + 1}]/td[2]/div/p/span[2]'
                try:
                    description = self.browser.find_element_by_xpath(description_xpath).text
                    unit_price = self.browser.find_element_by_xpath(unit_price_xpath).text

                    # insurance items are typically price=0, ignore it
                    if float(unit_price) == 0:
                        continue
                except:
                    continue

                order_info = f'{date},{order_number},{price},{ship_company},{ship_number},{description},{unit_price}'
                orders.append(order_info)

        return orders

    def get_purchase_list(self, num_pages):
        """

        :return:
        """
        self.open_my_taobao()
        self.click_button(xpath=self.bought_xpath, timeout=30)
        print("getting order info in page 1...")
        orders = self.get_order_info(orders=None)
        for i in range(num_pages - 1):
            self.click_next_page()
            time.sleep(3)
            print(f"getting order info in page {i + 2}...")
            orders = self.get_order_info(orders=orders)

        with open('订单信息.csv', 'w', encoding='utf-8') as f:
            header = '日期,订单号,订单总价格,物流公司,运单号码,宝贝,宝贝单价'
            f.write(header + '\n')
            for order in orders:
                f.write(order + '\n')


def main(num_pages=1):
    taobao = TaoBao()
    taobao.get_purchase_list(num_pages)


if __name__ == '__main__':
    try:
        num_pages = sys.argv[1]
    except:
        num_pages = 1
    main(int(num_pages))
    print("Done!")
