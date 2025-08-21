# Getting Started

This guide will walk you through the process of installing and configuring the MkDocs Graph Plugin.

## Installation

Install the plugin using `pip`:

```bash
pip install mkdocs-graph-plugin
```

!!! important
    This plugin is designed to work with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. While it may work with other themes, it is not guaranteed.

## Enabling the Plugin

To enable the plugin, add it to your `mkdocs.yml`:

```yaml
plugins:
  - graph
```

That's it! A graph of your documentation will now be available in your site. By default, it will appear in the table of contents sidebar.

## Next Steps

Now that you have the plugin up and running, you might want to:

- [Configure the plugin](configuration.md) to change its behavior.
- [Customize the graph's appearance](customization.md) to match your theme.
