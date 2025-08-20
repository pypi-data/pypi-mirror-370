# dpy-container-pagination

#### The library originated from [discord.py-pagination](https://github.com/soosBot-com/Pagination).

#### dpy-container-pagination is a Python library to easily create embed paginators.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the library.

```bash
pip install dpy-container-pagination
```

## Usage

### Quickstart

```python
import Paginator

# Create a list of containers to paginate.
containers = [discord.ui.Container().add_item(discord.ui.TextDisplay("First container")),
          discord.ui.Container().add_item(discord.ui.TextDisplay("Second container")),
          discord.ui.Container().add_item(discord.ui.TextDisplay("Third container"))]

... # Inside a command.
await Paginator.Simple().start(ctx, pages=containers)
```

### Advanced

##### To use custom buttons, pass in the corresponding argument when you initiate the paginator. **THESE ARE OPTIONAL**

```python
# These arguments override the default ones.

PreviousButton = discord.ui.Button(...)
NextButton = discord.ui.Button(...)
PageCounterStyle = discord.ButtonStyle(...) # Only accepts ButtonStyle instead of Button
InitialPage = 0 # Page to start the paginator on.
ephemeral = true # Defaults to false if not passed in.

await Paginator.Simple(
    PreviousButton=PreviousButton,
    NextButton=NextButton,
    PageCounterStyle=PageCounterStyle,
    InitialPage=InitialPage,
    ephemeral=ephemeral).start(ctx, pages=embeds)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
