import time
from com_tools.loggers import logger
from com_tools.profiles import ComProfile, ProfileRepo
import pytest

logger.info(f"Starting Test...")
PROFILE_NAME="my_test_client_profile"

_test_dict = {
    "name": PROFILE_NAME,
    "protocol": "demo",
    "config": {
        "delay": 1.5,
        "count": 3,
        "message": {
            "header": "DEMO",
            "content": "A Simple Demo"
        }
    }
}

@pytest.fixture
def repo() -> ProfileRepo:
    return ProfileRepo()


def test_create_profile() -> None:
    profile = ComProfile(**_test_dict)
    assert isinstance(profile, ComProfile)
    assert profile.name == _test_dict["name"]
    assert profile.config == _test_dict["config"]


def test_save_and_load_profile(repo: ProfileRepo) -> None:
    profile = ComProfile(**_test_dict)
    repo.add_profile(profile)
    new_profile = repo.get_profile(profile.name)
    assert (profile == new_profile)



def test_list_client_and_load(repo: ProfileRepo) -> None:
    profile = ComProfile(**_test_dict)

    for name, _profile in repo.list_profiles():
        if name == profile.name:
            assert (profile == _profile)

def test_remove_profile(repo: ProfileRepo) -> None:
    profile = ComProfile(**_test_dict)
    logger.info(f"NAME => {profile.name}")
    time.sleep(2)
    repo.delete_profile(profile.name)
    for name, _ in repo.list_profiles():
        if name == profile.name:
            assert False, "Profile wasn't deleted."
