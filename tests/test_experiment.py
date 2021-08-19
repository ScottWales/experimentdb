from experimentdb.experiment import experiment_factory


def test_experiment_factory():
    exp = experiment_factory("generic", "")
    assert exp.type == "generic"

    exp = experiment_factory("access-cm-payu", "")
    assert exp.type == "access-cm-payu"
