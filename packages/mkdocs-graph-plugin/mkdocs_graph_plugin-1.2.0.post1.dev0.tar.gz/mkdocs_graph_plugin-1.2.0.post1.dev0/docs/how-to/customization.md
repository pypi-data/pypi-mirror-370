# Customization

You can customize the appearance of the graph by overriding the default CSS variables in your `extra.css` file.

!!! warning
    Be careful when overriding CSS variables, as it can affect the entire look and feel of your site. It's recommended to test your changes thoroughly.

## CSS Variables

| Variable | Description |
|---|---|
| `--md-graph-text-color` | The color of the node text. |
| `--md-graph-link-color` | The color of the links between nodes. |
| `--md-graph-node-color` | The color of the nodes. |
| `--md-graph-node-color--hover`| The color of a node when hovered. |
| `--md-graph-node-color--current`| The color of the current node. |

## Example

To change the color of the nodes and links, you could add the following to your `extra.css` file:

```css
:root {
  --md-graph-node-color: #ff0000;
  --md-graph-link-color: #00ff00;
}
```

This would make the nodes red and the links green.

## Next Steps

After customizing the appearance of the graph, you might also want to [configure the plugin's behavior](../reference/configuration.md).
