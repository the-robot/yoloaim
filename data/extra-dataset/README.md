# csgo-dataset
Formatted CSGO object detection dataset in YOLO format.

**CREDIT:** The raw images come from [this repository](https://github.com/Orinion/csgo_images).

The annotation used in the original repo is `center-x`, `center-y`, `width`, and `height`.
Therefore, I wrote a script to reformat the annotations into `top-left-x`, `top-left-y`, `bottom-right-x` and `bottom-right-y`.
- And also added a method to skip images with empty annotations (no objects inside).

There're only 2 labels. (same as original dataset).
- 0 for Terrorist (T)
- 1 for Counter Terrorist (CT)

> if you want to swap labels, you can change the config in `labels.py` inside.
