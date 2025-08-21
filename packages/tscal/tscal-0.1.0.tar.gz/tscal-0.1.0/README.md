Simple calendar for usage in popups.

Example usage (in Sway):

```sh
kitty --class="kitty-ct" sh -c "uv run ct"
```

Then is Sway config:

```
for_window [app_id="kitty-ct"] floating enable, resize set width 500 px height 250 px, move position cursor
```

Keyboard commands:

- Ctrl+f - next month
- Ctrl+b - previous month
- Ctrl+n - next year
- Ctrl+p - previous year
- Ctrl+t - today
