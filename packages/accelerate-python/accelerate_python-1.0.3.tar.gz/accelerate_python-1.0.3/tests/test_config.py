## external imports
from pathlib import Path

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import Config, WrapperTest

## global variables
CONFIG_PATH = Path(__file__).parent.joinpath("input/config")


## test cases
class TestConfig(WrapperTest):
    @pytest.fixture
    def config(self):
        return Config(CONFIG_PATH)

    def test_init(self, config: Config):
        assert_that(config, "default_init").is_instance_of(Config).contains("root")

        key_prefix = "root.config-1"
        assert_that(
            config.get_value(key_prefix, "key-1-4"), "merge - override value"
        ).is_equal_to("value-1-4-0")
        assert_that(
            config.get_value(key_prefix, "key-1-5.key-1-5-1"),
            "merge - override inner value",
        ).is_equal_to("value-1-5-1-0")
        assert_that(
            config.get_value(key_prefix, "key-1-5.key-1-5-3"), "merge - new inner key"
        ).is_equal_to("value-1-5-3")
        assert_that(
            config.get_value(key_prefix, "key-1-6"), "merge - override list"
        ).is_equal_to(["value-1-6-3"])
        assert_that(
            config.get_value(key_prefix, "key-1-7"), "merge - new child key"
        ).is_equal_to("value-1-7")
        assert_that(config["root"], "merge - new key").contains("config-2", "config-3")

    def test_init_custom(self):
        config = Config(
            CONFIG_PATH.parent.joinpath("data"), config_type="json", normalize=True
        )
        assert_that(config, "custom_init").is_instance_of(Config).contains("a")
        assert_that(config.get_value("g"), "normalize").is_equal_to(1)

    def test_get_value(self, config: Config):
        assert_that(config.get_value("root.config-1.key-1-1"), "get_value").is_equal_to(
            "value-1-1"
        )

    def test_set_value(self, config: Config):
        config.set_value("root.config-7.key-7-1.key-7-1-1", "value-7-1-1")
        config.set_value("root.config-7.key-7-1.key-7-1-2", "value-7-1-2")
        assert_that(config.get_value("root.config-7.key-7-1"), "object").is_equal_to(
            {
                "key-7-1-1": "value-7-1-1",
                "key-7-1-2": "value-7-1-2",
            }
        )

        config.set_value("root.config-7.key-7-2", ["value-7-2-1", "value-7-2-2"])
        config.set_value("root.config-7.key-7-2.2", "value-7-2-3")
        assert_that(config.get_value("root.config-7.key-7-2"), "list").is_equal_to(
            ["value-7-2-1", "value-7-2-2", "value-7-2-3"]
        )

    def test_normalize(self, config: Config):
        config.normalize()

        ## standard references
        key_prefix = "root.config-2"
        assert_that(
            config.get_value(key_prefix, "key-2-4"), "value reference"
        ).is_equal_to("value-2-1")
        assert_that(
            config.get_value(key_prefix, "key-2-5"), "object reference"
        ).is_equal_to(
            {
                "key-2-2-1": "value-2-2-1",
                "key-2-2-2": "value-2-2-2",
            }
        )
        assert_that(
            config.get_value(key_prefix, "key-2-6"), "list reference"
        ).is_equal_to(
            [
                "value-2-3-1",
                "value-2-3-2",
            ]
        )
        assert_that(
            config.get_value(key_prefix, "key-2-7"), "invalid reference"
        ).is_equal_to("${root.config-2.key-2-0}")

        ## nested references
        key_prefix = "root.config-4"
        assert_that(
            config.get_value(key_prefix, "key-4-1"), "nested value reference"
        ).is_equal_to("value-3-4")
        assert_that(
            config.get_value(key_prefix, "key-4-2"), "nested object reference"
        ).is_equal_to(
            {
                "key-3-5-1": "value-3-5-1",
                "key-3-5-2": "value-3-5-2",
            }
        )
        assert_that(
            config.get_value(key_prefix, "key-4-3"), "nested list reference"
        ).is_equal_to(
            [
                "value-3-6-1",
                "value-3-6-2",
            ]
        )

        ## parent references
        key_prefix = "root.config-6"
        assert_that(
            config.get_value(key_prefix, "key-5-1"), "inherited key"
        ).is_equal_to("value-5-1")
        assert_that(
            config.get_value(key_prefix, "key-5-3"), "overridden parent key"
        ).is_equal_to("value-5-3-0")
        assert_that(
            config.get_value(key_prefix, "key-5-4"), "new child key"
        ).is_equal_to("value-5-4")


if __name__ == "__main__":
    pytest.main([__file__])
