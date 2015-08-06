__author__ = 'Camilla'

import logging
import os
from time import sleep
import datetime
import unittest

from appium import webdriver
from selenium.common.exceptions import NoSuchElementException


# Refer to following url for screenshot
# https://github.com/appium/appium/issues/968#issuecomment-75641576

# Refer to following url for install google extra service
# http://developer.android.com/sdk/installing/adding-packages.html


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# Set default keyboard as English


class GmailTests(unittest.TestCase):

    MAIL_RECEIPT = ''
    MAIL_TITLE = 'Verify sending email'
    MAIL_BODY = 'Hello, this is a test from the testing script'

    KEY_CODE_ENTER = 66

    # Error message when Gmail server could not find matched mail or get network connection
    ERROR_NOT_FND = ''
    ERROR_NO_CONNECTION = ''

    def setUp(self):

        desired_caps = dict()
        desired_caps['platformName'] = 'Android'

        desired_caps['platformVersion'] = '4.4'
        desired_caps['deviceName'] = 'Android Emulator'

        # If gmail.apk not installed, you have to put the apk and enable the following part
        '''
        desired_caps['app'] = PATH(
            '../TestApp/gmail5.apk'
        )
        '''

        desired_caps['appPackage'] = 'com.google.android.gm'
        desired_caps['appActivity'] = 'com.google.android.gm.ui.MailActivityGmail'

        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        logger.debug('setup down')

        # Add delay for waiting emulator
        sleep(5)

    def tearDown(self):
        # end the session

        self.driver.quit()
        logger.debug('teardown')

    def no_alert_present(self):

        try:
            self.driver.find_element_by_id('android:id/message')
            return False
        except NoSuchElementException:
            return True
    '''
    def get_toast_msg(self):
        toast_msg = self.driver.find_element_by_id('com.google.android.gm:id/toast_bar')
        print (toast_msg.text)
    '''

    def check_mail_list(self, timestamp=None):
        driver = self.driver

        # click search button
        driver.find_element_by_id('com.google.android.gm:id/search').click()

        search_txt = driver.find_element_by_id('com.google.android.gm:id/search_actionbar_query_text')
        # format keyword for verification
        keyword = '123455XXX!@#$%^^^'

        keyword = "subject:{title} to:{receipt} {tstamp:%Y-%m-%d %H:%M:%S} ".format(
            title=self.MAIL_TITLE, receipt=self.MAIL_RECEIPT, tstamp=timestamp
        )

        search_txt.send_keys(keyword)
        driver.press_keycode(self.KEY_CODE_ENTER)

        # time for confirming result
        sleep(10)
        try:
            # successfully search mail with specified keyword
            driver.find_element_by_id('com.google.android.gm:id/search_status_text_view')

        except NoSuchElementException:

            logger.info('No matched mails')

            return
            # search picture of empty result
            empty_text = driver.find_element_by_id('com.google.android.gm:id/empty_text').text

            state1 = self.ERROR_NO_CONNECTION in empty_text
            state2 = self.ERROR_NOT_FND in empty_text

            logger.info("Error Hint: %s state1:%s state2:%s" % (empty_text, state1, state2))
            self.assertTrue((state1 or state2), 'Verify Failed, Could not find error msg')

    # @unittest.skip('send')
    def test_send_mail(self):
        driver = self.driver

        logger.debug('test_open_gmail start!')

        write_btn = driver.find_element_by_id('com.google.android.gm:id/compose_button')
        write_btn.click()

        # fill receipt, title and body
        receipt_text = driver.find_element_by_id('com.google.android.gm:id/to')
        receipt_text.clear()
        receipt_text.send_keys(self.MAIL_RECEIPT)
        driver.press_keycode(self.KEY_CODE_ENTER)

        title_text = driver.find_element_by_id('com.google.android.gm:id/subject')
        title_text.clear()
        title_text.send_keys(self.MAIL_TITLE)
        driver.press_keycode(self.KEY_CODE_ENTER)

        body_text = driver.find_element_by_id('com.google.android.gm:id/body')
        body_text.clear()

        # Get timestamp for mails uniqueness
        timestamp = datetime.datetime.now()
        mail_content = "{}\n{:%Y-%m-%d %H:%M:%S}".format(self.MAIL_BODY, timestamp)

        body_text.send_keys(mail_content)
        driver.press_keycode(self.KEY_CODE_ENTER)

        # sleep for information confirmation
        sleep(3)

        # press send button
        driver.find_element_by_id('com.google.android.gm:id/send').click()

        # if some tips pop up, there is an error in receipt column
        self.assertTrue(self.no_alert_present(), 'Please check your receipt')

        # wait for sending
        sleep(3)
        self.check_mail_list(timestamp)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(GmailTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
