class CatchInvalidSeleniumException:

    def __init__(self, test_case):
        self.enabled = test_case.suppress_invalid_exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled:
            print(f'{exc_type} {exc_val} was suppressed')
            return True
