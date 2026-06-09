# Auto-Handwriting Generator

A Flask API that converts text into realistic handwriting and physically draws it on paper using an [AxiDraw](https://axidraw.com/) pen plotter. Text is rendered to an SVG by a neural handwriting-synthesis model, cleaned up, and sent to the plotter.

## How It Works

```
Text  ->  Handwriting synthesis (SVG)  ->  Clean SVG  ->  Plot on AxiDraw
```

1. **Generate** — Input text is split into lines and passed to a handwriting-synthesis model (`demo.Hand`) which produces a handwritten-style SVG.
2. **Clean** — The SVG is stripped of non-stroke elements (`rect`, `line`, `circle`, `polygon`, `polyline`) and resized so it plots correctly.
3. **Plot** — The cleaned SVG is sent to the AxiDraw via `plot_no_scale.py` with a configurable serial port and vertical offset.

## Features

- **REST API** built with Flask for generating and plotting handwriting.
- **Automatic line wrapping** with a configurable character limit per line.
- **Adjustable handwriting style and bias** to vary the look of the output.
- **Thread-safe plotting** using a lock so only one plot runs at a time.
- **Live status tracking** (currently plotting, last plot time, last error).

## Requirements

- Python 3.x
- [Flask](https://flask.palletsprojects.com/)
- A handwriting-synthesis model exposing a `demo.Hand` class (e.g. [sjvasquez/handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis)), available in a conda environment named `handwriting`.
- An [AxiDraw](https://axidraw.com/) pen plotter and the `plot_no_scale.py` plotting script.
- A conda installation (the app activates the `handwriting` environment to run generation).

```bash
pip install flask
```

## Configuration

Defaults are set near the top of `Handwriting_code.py`:

| Setting | Default | Description |
| --- | --- | --- |
| `HANDWRITING_ENV` | `handwriting` | Conda env used to run the synthesis model |
| `OUTPUT_DIR` | `handwriting_from_image/axidrawtests` | Where generated SVGs are written |
| `DEFAULT_PORT` | `COM3` | Serial port for the AxiDraw |
| `DEFAULT_BIAS` | `0.65` | Handwriting bias (higher = neater) |
| `DEFAULT_STYLE` | `5` | Handwriting style index |
| `FIXED_Y_OFFSET_MM` | `82.55` | Default vertical plotting offset (mm) |

## Running

```bash
python Handwriting_code.py
```

The server starts on `http://localhost:5000`.

## API Endpoints

### `GET /`
Returns basic API info and available routes.

### `GET /health`
Returns service health and whether a plot is in progress.

### `GET /status`
Returns the current plotting status (`is_plotting`, `current_text`, `last_plot_time`, `last_error`).

### `POST /plot`
Generates handwriting from text and plots it.

**Request body (JSON)** — provide one of `lines`, `text`, or `smart_text`:

| Field | Type | Description |
| --- | --- | --- |
| `lines` | array of strings | Pre-split lines to write |
| `text` | string | Raw text (auto-wrapped to ~40 chars/line) |
| `smart_text` | string | Text using `\n` for explicit line breaks |
| `last_line` | string | Optional extra line appended at the end |
| `bias` | number | Override handwriting bias |
| `style` | number | Override handwriting style |
| `port` | string | Override serial port |
| `y_offset_inches` | number | Vertical offset in inches (converted to mm) |

**Example**

```bash
curl -X POST http://localhost:5000/plot \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world, this is handwritten by a robot!", "bias": 0.7, "style": 5}'
```

**Success response**

```json
{
  "status": "success",
  "message": "done",
  "svg_path": "handwriting_from_image/axidrawtests/api_cleaned.svg",
  "plot_time_seconds": 12.34,
  "text_plotted": ["Hello world, this is handwritten by a robot!"]
}
```

## Files

- `Handwriting_code.py` — Flask API: handwriting generation, SVG cleaning, and AxiDraw plotting.
- `api_generated_cropped.svg` / `api_generated_compressed.svg` — Sample generated handwriting output.

## Notes

- The app shells out to a conda environment and an AxiDraw plotting script, so it expects those to be installed and configured on the host machine.
- Plotting is serialized with a lock; concurrent `/plot` requests will wait their turn.
