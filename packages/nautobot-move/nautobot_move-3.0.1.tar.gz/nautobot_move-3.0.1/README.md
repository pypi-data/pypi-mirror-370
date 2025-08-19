# Nautobot Move

Nautobot Move enables you to move a device by replacing a planned device. It works best in
connection with [nautobot\_deepcopy](https://gitlab.intern.gwdg.de/ag-n/nautobot-deepcopy)
to enable you to plan a move and then switch it on once you’re ready to go.
Cables and connections will be preserved from the planned device.

Please note that this plugin uses internal Nautobot components, which is
explicitly discouraged by the documentation. We promise to keep the plugin up
to date, but the latest version might break on unsupported Nautobot version.
Your mileage may vary.

## Integration

To integrate the plugin, you will have to provide add it to your `PLUGINS`
configuration to your `configuration.py`:

```
PLUGINS = [
  "nautobot_move",
  # my other plugins
]
```

The [Nautobot plugins guide](https://nautobot.readthedocs.io/en/stable/plugins/development/#initial-setup)
should help you get started!

## Usage

Once the plugin is installed, a button labelled `Move` will appear on the
detail page of devices.

<img alt="Move button" src="./docs/button.png" width="150">

Once you click that button, you will be directed to a form that allows you to
choose any planned device to move this device to, preserving any connections.
When submitting, the backend will make sure the connections actually match up,
and emit a form error otherwise.

![Move form](./docs/form.png)

The planned device that is superseded will be deleted.

<hr/>

Have fun!
