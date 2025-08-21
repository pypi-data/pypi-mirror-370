# Configuration

You can configure the plugin in your `mkdocs.yml` file.

## Options

| Option       | Type     | Default     | Description                                               |
|--------------|----------|-------------|-----------------------------------------------------------|
| `name`       | `string` | `"title"`   | The name of the nodes in the graph (`title` or `file_name`). |
| `debug`      | `boolean`| `false`     | Enable debug logging in the terminal and browser console. |

### `name`

This option controls how the nodes in the graph are named.

- **Type:** `string`
- **Default:** `title`
- **Options:**
    - `title`: Use the title from the Markdown file's metadata. This is the recommended setting.
    - `file_name`: Use the name of the Markdown file. This can be useful if you have a lot of files with the same title.

### `debug`

This option enables detailed logging for debugging purposes.

- **Type:** `boolean`
- **Default:** `false`

When set to `true`, the plugin will output verbose logs to the terminal and the browser console, which can be useful for troubleshooting issues with graph generation or rendering.

## Example Configuration

Here is an example of a complete configuration:

```yaml
plugins:
  - graph:
      name: "file_name"
      debug: true
```

## Next Steps

Once you have configured the plugin, you might want to [customize the appearance of the graph](../how-to/customization.md).
