"""Test the Retryer model."""

from tenacity import Retrying

from dkist_service_configuration.retryer import RetryerFactory


def test_retryer_defaults():
    """
    :given: A retryer factory
    :when: The factory is called
    :then: A Retryer object is returned
    """
    # given
    factory = RetryerFactory()
    # when
    retryer = factory()
    # then
    assert isinstance(retryer, Retrying)


def test_retryer_with_attempts():
    """
    :given: A retryer factory with attempts > 1
    :when: The factory is called
    :then: A Retryer object is returned with a stop_after_attempt object
    """
    # given
    factory = RetryerFactory(attempts=5)
    # when
    retryer = factory()
    # then
    assert isinstance(retryer, Retrying)
    assert retryer.stop is not None
