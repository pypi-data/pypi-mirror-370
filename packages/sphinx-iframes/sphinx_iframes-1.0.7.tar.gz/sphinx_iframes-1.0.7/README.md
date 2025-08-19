# Sphinx extension: Iframes

## Introduction

This extension provides an interface to include iframes with relative ease, but does try to provide manners to interact with the various options. This rests purely by setting default CSS values, that the user can overwrite if preferred for individual iframes, but also globally. In general, each `iframe` is embedded within a `div` element, which eases sizing.

> [!NOTE]
> Using CSS is complicated and error prone, so always check and never expect that you get what you want.

## What does it do?

This extension provides several Sphinx directives:

- `iframe`
- `h5p`
- `video`
- `iframe-figure`

 that can be used to quickly insert an iframe with standard sizing and styling.

## Installation
To use this extenstion, follow these steps:

**Step 1: Install the Package**

Install the module `sphinx-iframes` package using `pip`:
```
pip install sphinx-iframes
```
    
**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
sphinx-iframes
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions (**important**: underscore, not dash this time):
```
sphinx: 
    extra_extensions:
        .
        .
        .
        - sphinx_iframes
        .
        .
        .
```

## Configuration

The extension provides several configuration values, which can be added to `_config.yml`:

```yaml
sphinx: 
    config:
        -
        -
        -
        iframe_blend:          true # default value
        iframe_saturation:     1.5 # default value
        iframe_h5p_autoresize: true # default value
        iframe_background:     "#ffffff" # default value
        iframe_width:          calc(100% - 2.8rem) # default value
        iframe_aspectratio:    auto 2 / 1 # default value
        -
        -
        -
```

- `iframe_blend`: `true` (_default_) or `false`:
  - if `true` all iframes are standard blended with the background and in dark-mode also inverted.
  - if `false` all non-blended iframes will have background a colored background and no inversion for dark-mode is applied.
  - there's no need to set the blend or no-blend for individual iframes if it's set in the `_config.yml`, unless you want to deviate from the setting set there.
- `iframe_saturation`: `1.5` (_default_) or **float**:
  - Blended iframes are inverted in darkmode using the CSS filter `invert(1) hue-rotate(180deg) saturation(iframe_saturation)`.
- `iframe_h5p_autoresize`: `true` (_default_) or `false`:
  - if `true` all h5p iframes are automagically resized to fit the element in which the iframe is loaded.
  - if `false` no h5p iframes are automagically resized to fit the element in which the iframe is loaded.
- `iframe_background`: `"#ffffff"` (_default_) or **CSS string**:
  - sets the standard background color of non-blended iframes.
  - Any CSS string defining colors can be used, see [<color> CSS data type](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value).
  - Surround with `" "` for hex strings.
  - Only visible if the content of the iframes has a transparant background. 
- `iframe_width`:  `calc(100% - 2.8rem)` (_default_) or **CSS string**:
  - sets the standard width of the iframe within the parent element;
  - Any CSS string defining a width can be used, see [width CSS property](https://developer.mozilla.org/en-US/docs/Web/CSS/width).
- `iframe_aspectratio`: `auto 2 / 1` (_default_) or **CSS string**:
  - sets the standard aspect ration of the iframe within the parent element;
  - Any CSS string defining an aspect ratio can be used, see [aspect-ratio CSS property](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio).

## Provided code

### Directives

The following new directives are provided:

````md
```{iframe} <link_to_webpage_to_embed>
```
````

````md
```{h5p} <link_to_h5p_webpage_to_embed>
```
````

````md
```{video} <link_to_video_to_embed>
```
````

In case of a YouTube-link, it is inverted to an embed link if the normal web URL is provided. H5p links are converted too if provided without `/embed`.

````md
```{iframe-figure} <link_to_webpage_to_embed>
:name: some:label

The caption for the iframe.
```
````

Note that you don't need the full embed code of an iframe. Only the source url should be used.

All of these have the following options:

- `:class:`
  - If further CSS styling is needed, then use this option to append a CSS class name to the rendered iframe.
  - We recommend to only use the classes `blend` and `no-blend`, see [](sec:iframes:examples).
- `:divclass:`
  - If further CSS styling is needed, then use this option to append a CSS class name to the div surrounding the iframe.
- `:width:`
  - Sets the width of the iframe. Use CSS compatible strings.
- `:height:`
  - Sets the width of the iframe. Use CSS compatible strings.
- `:aspectratio:`
  - Sets the width of the iframe. Use CSS compatible strings.
- `:styleframe:`
  - Sets the style of the iframe. Use CSS compatible strings. Surround with " ".
- `:stylediv:`
  - Sets the style of the surrounding div. Use CSS compatible strings. Surround with " ".

The directive `iframe-figure` also inherits all options from the `figure` directive from Sphinx.

(sec:iframes:examples)=
## Examples and details

To see examples of usage visit [this page in the TeachBooks manual](https://teachbooks.io/manual/external/sphinx-iframes/README.html).

## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/sphinx-iframes). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/sphinx-iframes).

The `README.md` of the branch `Manual` is also part of the [TeachBooks manual](https://teachbooks.io/manual/intro.html) as a submodule.
