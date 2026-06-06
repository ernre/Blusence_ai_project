from vpe.config import config_hash, load_config, seed_everything


def test_load_config_and_hash() -> None:
    config = load_config("configs/base.yaml")

    assert config["engine"]["name"] == "VPE-1.0"
    assert len(config_hash(config)) == 12


def test_seed_everything_is_deterministic() -> None:
    import random

    seed_everything(7)
    first = random.random()
    seed_everything(7)
    second = random.random()

    assert first == second
