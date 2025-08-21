from pathlib import Path

from apilinker.core.plugins import PluginManager, TransformerPlugin


def test_plugin_discovery_from_temp_dir(tmp_path):
    # create a temporary plugin module
    plugin_code = (
        "from apilinker.core.plugins import TransformerPlugin\n"
        "class MyX(TransformerPlugin):\n"
        "    plugin_name='myx'\n"
        "    def transform(self, value, **kwargs):\n"
        "        return value\n"
    )
    mod = tmp_path / "temp_plugin.py"
    mod.write_text(plugin_code, encoding="utf-8")

    pm = PluginManager()
    discovered = pm.discover_plugins(plugin_dir=str(tmp_path))
    # ensure our class is discovered and registered
    names = [p["name"] for p in discovered]
    assert "myx" in names
    cls = pm.get_plugin("transformer", "myx")
    assert cls is not None
    inst = pm.instantiate_plugin("transformer", "myx")
    assert isinstance(inst, TransformerPlugin)
