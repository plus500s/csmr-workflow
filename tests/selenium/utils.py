from selenium.webdriver.common.keys import Keys


def send_predict_keys(predict_a, predict_b, predict_c, key_a, key_b, key_c):
    for i in range(int(key_a/5)):
        predict_a.send_keys(Keys.RIGHT)
    for i in range(int(key_b/5)):
        predict_b.send_keys(Keys.RIGHT)
    for i in range(int(key_c/5)):
        predict_c.send_keys(Keys.RIGHT)


def set_predict_keys_to_zero(predict_a, predict_b, predict_c, key_a, key_b, key_c):
    for i in range(int(key_a/5)):
        predict_a.send_keys(Keys.LEFT)
    for i in range(int(key_b/5)):
        predict_b.send_keys(Keys.LEFT)
    for i in range(int(key_c/5)):
        predict_c.send_keys(Keys.LEFT)
