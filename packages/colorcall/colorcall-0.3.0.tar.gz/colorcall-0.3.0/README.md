![Logo](https://mykaleidoscope.ru/x/uploads/posts/2022-09/1663623253_4-mykaleidoscope-ru-p-zloi-karakal-pinterest-4.jpg)

# Colorcall

Color call your caracal!


## Authors

- [@MikleSedrakyan](https://github.com/Sw1mmeR)
- [@AndreyAfanasiev](https://github.com/AfanasevAndrey)

## Usage/Examples

```python
from colorcall import green

green("My caracal is green!")
```
```python
from colorcall import Color, rgb, basic

print(
    rgb("Font is pink, background is purple,", (250, 132, 239), bgcolor=(50, 30, 100)),
    basic("background is yellow.", bgcolor=Color.yellow),
)
```
```python
from colorcall import FontStyle, rgb, basic

print(basic("This is bold", style=FontStyle.bold))
print(rgb("This is italic", style=FontStyle.italic))
```