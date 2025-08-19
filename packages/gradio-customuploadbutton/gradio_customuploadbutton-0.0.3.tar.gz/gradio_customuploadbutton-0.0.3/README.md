---
tags: [gradio-custom-component, UploadButton]
title: gradio_customuploadbutton
short_description: support Distributed upload
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_customuploadbutton`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.3%20-%20orange">  

support Distributed upload

## Installation

```bash
pip install gradio_customuploadbutton
```

## Usage

```python

import gradio as gr
from gradio_customuploadbutton import CustomUploadButton


example = CustomUploadButton().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        CustomUploadButton(label="Blank"),  # blank component
        CustomUploadButton(value=example, label="Populated"),  # populated component


if __name__ == "__main__":
    demo.launch()

```

## `CustomUploadButton`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"Upload a File"</code></td>
<td align="left">Text to display on the button. Defaults to "Upload a File".</td>
</tr>

<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | list[str] | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">File or list of files to upload by default.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>variant</code></td>
<td align="left" style="width: 25%;">

```python
Literal["primary", "secondary", "stop"]
```

</td>
<td align="left"><code>"secondary"</code></td>
<td align="left">'primary' for main call-to-action, 'secondary' for a more subdued style, 'stop' for a stop button.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>size</code></td>
<td align="left" style="width: 25%;">

```python
Literal["sm", "md", "lg"]
```

</td>
<td align="left"><code>"lg"</code></td>
<td align="left">size of the button. Can be "sm", "md", or "lg".</td>
</tr>

<tr>
<td align="left"><code>icon</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">URL or path to the icon file to display within the button. If None, no icon will be displayed.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the CustomUploadButton will be in a disabled state.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>type</code></td>
<td align="left" style="width: 25%;">

```python
Literal["filepath", "binary"]
```

</td>
<td align="left"><code>"filepath"</code></td>
<td align="left">Type of value to be returned by component. "file" returns a temporary file object with the same base name as the uploaded file, whose full path can be retrieved by file_obj.name, "binary" returns an bytes object.</td>
</tr>

<tr>
<td align="left"><code>file_count</code></td>
<td align="left" style="width: 25%;">

```python
Literal["single", "multiple", "directory"]
```

</td>
<td align="left"><code>"single"</code></td>
<td align="left">if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".</td>
</tr>

<tr>
<td align="left"><code>file_types</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">List of type of files to be uploaded. "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `click` | Triggered when the CustomUploadButton is clicked. |
| `upload` | This listener is triggered when the user uploads a file into the CustomUploadButton. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, passes the file as a `str` or `bytes` object, or a list of `str` or list of `bytes` objects, depending on `type` and `file_count`.
- **As input:** Should return, expects a `str` filepath or URL, or a `list[str]` of filepaths/URLs.

 ```python
 def predict(
     value: bytes | str | list[bytes] | list[str] | None
 ) -> str | list[str] | None:
     return value
 ```
 
