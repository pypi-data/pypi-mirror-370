import os
from unittest import TestCase

from readables.deferrable import deferrable, defer
from readables.env import required_env, RequiredEnvironmentVariable, EnvironmentVariableManager


class TestUnit(TestCase):
    def _revert_env_var_to_original(self, env, value):
        if value is None:
            if env in os.environ:
                del os.environ[env]
        else:
            os.environ[env] = value

    @deferrable
    def test_required_flag(self):
        original_value = os.getenv('T_ALPHA')

        evm = EnvironmentVariableManager()

        with self.assertRaises(RequiredEnvironmentVariable):
            evm.required_env('T_ALPHA')

        expected_value = 'foo'
        os.environ['T_ALPHA'] = expected_value
        defer(lambda: self._revert_env_var_to_original('T_ALPHA', original_value))

        self.assertEqual(evm.required_env('T_ALPHA'), expected_value)

        expected_value = 123
        os.environ['T_ALPHA'] = str(expected_value)
        defer(lambda: self._revert_env_var_to_original('T_ALPHA', original_value))

        self.assertEqual(evm.required_env('T_ALPHA', kind=int), expected_value)