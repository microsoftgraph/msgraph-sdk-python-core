from msgraphcore.middleware.redirect_middleware import RedirectMiddleware


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    redirect_middleware = RedirectMiddleware()

    assert redirect_middleware.allow_redirects == redirect_middleware.DEFAULT_ALLOW_REDIRECTS
    assert redirect_middleware.total_redirects == redirect_middleware.DEFAULT_TOTAL_REDIRECTS
    assert redirect_middleware._redirect_status_codes == redirect_middleware.DEFAULT_REDIRECT_CODES


def test_custom_config():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    redirect_middleware = RedirectMiddleware(
        redirect_configs={
            "allow_redirects": False,
            "total_redirects": 3,
            "redirect_on_status_codes": [300, 301, 302, 303, 307]
        }
    )

    assert not redirect_middleware.allow_redirects
    assert redirect_middleware.total_redirects == 3
    assert redirect_middleware._redirect_status_codes == {300, 301, 302, 303, 307, 308}


def test_disable_redirects():
    """
    Test that when disable_redirects class method is called, allow redirects is set to false
    """
    redirect_middleware = RedirectMiddleware.disallow_redirects()
    assert not redirect_middleware.allow_redirects
