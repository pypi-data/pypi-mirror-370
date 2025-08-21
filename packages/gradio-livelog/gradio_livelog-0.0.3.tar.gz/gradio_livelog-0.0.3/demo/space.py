
import gradio as gr
from app import demo as app
import os

_docs = {'LiveLog': {'description': 'A component for displaying real-time logs and progress bars.\nIt receives structured data via a generator to update its state.', 'members': {'__init__': {'value': {'type': 'typing.Union[\n    typing.List[typing.Dict[str, typing.Any]],\n    typing.Callable,\n    NoneType,\n][\n    typing.List[typing.Dict[str, typing.Any]][\n        typing.Dict[str, typing.Any][str, Any]\n    ],\n    Callable,\n    None,\n]', 'default': 'None', 'description': 'The initial value, a list of log/progress dictionaries. Can be a callable.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The component label.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' seconds."}, 'height': {'type': 'int | str', 'default': '400', 'description': 'The height of the log panel in pixels or CSS units.'}, 'autoscroll': {'type': 'bool', 'default': 'True', 'description': 'If True, the panel will automatically scroll to the bottom on new logs.'}, 'line_numbers': {'type': 'bool', 'default': 'False', 'description': 'If True, shows line numbers for logs.'}, 'background_color': {'type': 'str', 'default': '"#000000"', 'description': 'The background color of the log panel as a CSS-valid string.'}, 'display_mode': {'type': '"full" | "log" | "progress"', 'default': '"full"', 'description': '"full" (logs and progress), "log" (only logs), or "progress" (only progress bar).'}, 'disable_console': {'type': 'bool', 'default': 'True', 'description': 'If True, logs will not be propagated to the standard Python console.'}, 'show_download_button': {'type': 'bool', 'default': 'True', 'description': 'If True, shows the download button in the header.'}, 'show_copy_button': {'type': 'bool', 'default': 'True', 'description': 'If True, shows the copy button in the header.'}, 'show_clear_button': {'type': 'bool', 'default': 'True', 'description': 'If True, shows the clear button in the header.'}, 'show_label': {'type': 'bool', 'default': 'True', 'description': 'If True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative size compared to adjacent Components.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum pixel width, will wrap if not sufficient screen space.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional string or list of strings assigned as the class of this component.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, this component will not be rendered.'}, 'key': {'type': 'int | str | tuple[int | str, Ellipsis] | None', 'default': 'None', 'description': 'A unique key for the component.'}}, 'postprocess': {'value': {'type': 'typing.Optional[typing.List[typing.Dict[str, typing.Any]]][\n    typing.List[typing.Dict[str, typing.Any]][\n        typing.Dict[str, typing.Any][str, Any]\n    ],\n    None,\n]', 'description': "The output data received by the component from the user's function in the backend."}}, 'preprocess': {'return': {'type': 'typing.Optional[typing.List[typing.Dict[str, typing.Any]]][\n    typing.List[typing.Dict[str, typing.Any]][\n        typing.Dict[str, typing.Any][str, Any]\n    ],\n    None,\n]', 'description': "The preprocessed input data sent to the user's function in the backend."}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the LiveLog changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the LiveLog using the clear button for the component.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'LiveLog': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_livelog`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_livelog/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_livelog"></a>  
</div>

A Live Log Component for Gradio Interface
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_livelog
```

## Usage

```python
# demo/app.py

import sys
import gradio as gr
import torch
import logging
import random
import numpy as np
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
import threading
import queue
import asyncio
import spaces

# Import the component and ALL its utilities
from gradio_livelog import LiveLog
from gradio_livelog.utils import ProgressTracker, Tee, TqdmToQueueWriter, capture_logs

# --- 1. SETUP ---
MODEL_ID = "SG161222/RealVisXL_V5.0_Lightning"
MAX_SEED = np.iinfo(np.int32).max

# --- 2. LOGIC FOR THE "LIVELOG FEATURE DEMO" TAB ---
app_logger = logging.getLogger("logging_app")
app_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.flush = sys.stderr.flush
app_logger.addHandler(console_handler)

async def run_process(disable_console: bool, rate_unit: str, run_error_case: bool):
    with capture_logs(log_level=logging.INFO, log_name=["logging_app"], disable_console=disable_console) as get_logs: #You can watch more than one log if you wish in log_name. If you do not pass log_name, the default log will be used.
        total_steps = 100
        tracker = ProgressTracker(total=total_steps, description="Simulating a process...", rate_unit=rate_unit)
        all_logs = []
        last_log_content = None
        
        initial_log = f"Starting simulated process with {total_steps} steps..."
        app_logger.info(initial_log)
        logs = [
            {
                "type": "log",
                "level": "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname,
                "content": record.getMessage()
            }
            for record in get_logs()
        ]
        all_logs.extend(logs)
        last_log_content = logs[-1]["content"] if logs else None        
        yield tracker.update(advance=0, status="running", logs=all_logs, log_content=None)

        for i in range(total_steps):
            await asyncio.sleep(0.03)
            current_step = i + 1
            
            if current_step == 10:
                app_logger.warning(f"Low disk space warning at step {current_step}.")
            elif current_step == 30:
                app_logger.log(logging.INFO + 5, f"Asset pack loaded successfully at step {current_step}.")
            elif current_step == 75:
                app_logger.critical(f"Checksum mismatch! Data may be corrupt at step {current_step}.")
            
            if run_error_case and current_step == 50:
                app_logger.error("A fatal simulation error occurred! Aborting.")
                logs = [
                    {
                        "type": "log",
                        "level": "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname,
                        "content": record.getMessage()
                    }
                    for record in get_logs()
                ]
                all_logs.extend(logs)
                last_log_content = logs[-1]["content"] if logs else last_log_content
                yield tracker.update(advance=0, status="error", logs=all_logs, log_content=last_log_content)
                return
            
            logs = [
                {
                    "type": "log",
                    "level": "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname,
                    "content": record.getMessage()
                }
                for record in get_logs()
            ]
            all_logs.extend(logs)
            if logs:
                last_log_content = logs[-1]["content"]
            yield tracker.update(advance=1, status="running", logs=all_logs, log_content=last_log_content)
        
        final_log = "Process completed successfully!"
        app_logger.log(logging.INFO + 5, final_log)
        logs = [
            {
                "type": "log",
                "level": "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname,
                "content": record.getMessage()
            }
            for record in get_logs()
        ]
        all_logs.extend(logs)
        last_log_content = logs[-1]["content"] if logs else last_log_content
        yield tracker.update(advance=0, status="success", logs=all_logs, log_content=last_log_content)
        
def update_livelog_properties(mode, color, lines, scroll):
    return gr.update(display_mode=mode, background_color=color, line_numbers=lines, autoscroll=scroll)

def clear_output():
    return None

async def run_success_case(disable_console: bool, rate_unit: str):
    yield None    
    async for update in run_process(disable_console=disable_console, rate_unit=rate_unit, run_error_case=False):
        yield update

async def run_error_case(disable_console: bool, rate_unit: str):
    yield None
    async for update in run_process(disable_console=disable_console, rate_unit=rate_unit, run_error_case=True):
        yield update


# --- 3. LOGIC FOR THE "DIFFUSION PIPELINE INTEGRATION" TAB ---
diffusion_pipeline = None
pipeline_lock = threading.Lock()
def load_pipeline(on_load=True):
    \"\"\"A function to load the model, ensuring it's only done once.\"\"\"
    global diffusion_pipeline
    with pipeline_lock:
        if diffusion_pipeline is None:
            print("Loading Stable Diffusion model for the first time...")
            pipe = StableDiffusionXLPipeline.from_pretrained(
                MODEL_ID, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False
            )
            pipe.enable_vae_tiling()
            pipe.enable_model_cpu_offload()
            pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)        
            diffusion_pipeline = pipe
            print("Model loaded successfully!")
        
    if not on_load:
        return diffusion_pipeline

@spaces.GPU(duration=60, enable_queue=True)
def run_diffusion_in_thread(prompt: str, disable_console: bool, update_queue: queue.Queue):
    \"\"\"
    This function now uses capture_logs to listen to internal diffusers logs
    while retaining the superior data structure you designed.
    \"\"\"
    tracker = None    
    with capture_logs(log_level=logging.INFO, log_name=["logging_app"], disable_console=disable_console) as get_logs: #You can watch more than one log if you wish in log_name. If you do not pass log_name, the default log will be used.
        try:            
            pipe = load_pipeline(on_load=False)
            
            #We will capture pipeline tqdm s/it progress instead            
            rate_queue = queue.Queue()
            tqdm_writer = TqdmToQueueWriter(rate_queue)
            
            progress_bar_handler = Tee(sys.stderr, tqdm_writer)
            pipe.set_progress_bar_config(file=progress_bar_handler,  #if you dont need to see the tqdm progress on console set file=tqdm_writer instead            
                                        disable=False,  
                                        ncols=100,
                                        dynamic_ncols=True,
                                        ascii=" █")
            
            seed = random.randint(0, MAX_SEED)
            generator = torch.Generator(device="cuda").manual_seed(seed)
            prompt_style = f"hyper-realistic 8K image of {prompt}. ultra-detailed, lifelike, high-resolution, sharp, vibrant colors, photorealistic"
            negative_prompt_style = "cartoonish, low resolution, blurry, simplistic, abstract, deformed, ugly"
            num_inference_steps = 10
            
            all_logs = []
            last_known_rate_data = None

            # Helper function to process and store new logs
            def process_and_send_updates(status="running", advance=0, final_image_payload=None):
                \"\"\"
                This is the core callback function. It captures new logs, formats them,
                and sends a complete update object (logs + progress) to the UI queue.
                This should also be called after the log record.
                \"\"\"
                nonlocal all_logs, last_known_rate_data
                new_rate_data = None
                while not rate_queue.empty():
                    try:
                        new_rate_data = rate_queue.get_nowait()
                    except queue.Empty:
                        break
                
                if new_rate_data is not None:
                    last_known_rate_data = new_rate_data
                
                new_records = get_logs()
                if new_records:
                    new_logs = [{
                        "type": "log",
                        "level": "SUCCESS" if r.levelno == logging.INFO + 5 else r.levelname,
                        "content": r.getMessage()
                    } for r in new_records]
                    all_logs.extend(new_logs)
                
                # Use the tracker to generate the progress update dictionary if it exists.
                # If not, create a preliminary update dictionary.
                update_dict = {}
                
                if tracker:
                    update_dict = tracker.update(
                        advance=advance, 
                        status=status, 
                        logs=all_logs,
                        rate_data=last_known_rate_data                               
                    )
                else:
                    # Initial state before the tracker is created.
                    update_dict = {
                        "type": "progress", 
                        "logs": all_logs, 
                        "current": 0, 
                        "total": num_inference_steps, 
                        "desc": "Diffusion Steps" # Description is sent once
                    }

                # Put the update on the queue. The image payload is usually None
                # until the very end.
                update_queue.put((final_image_payload, update_dict))
                
            app_logger.info(f"Using seed: {seed}")
            process_and_send_updates()
                        
            app_logger.info("Starting diffusion process...")
            process_and_send_updates()
                        
            tracker = ProgressTracker(total=num_inference_steps, description="Diffusion Steps", rate_unit='it/s')
            
            def progress_callback(pipe_instance, step, timestep, callback_kwargs):
                process_and_send_updates(advance=1) 
                return callback_kwargs
                        
            images = pipe(
                prompt=prompt_style, negative_prompt=negative_prompt_style, width=1024, height=1024,
                guidance_scale=3.0, num_inference_steps=num_inference_steps,
                generator=generator, callback_on_step_end=progress_callback
            ).images
            
            app_logger.log(logging.INFO + 5, "Image generated successfully!")
            process_and_send_updates(status="success", final_image_payload=images)
           

        except Exception as e:
            app_logger.error(f"Error in diffusion thread: {e}, process aborted!", exc_info=True)                    
            process_and_send_updates(status="error")                                                        
        finally:
            update_queue.put(None)
            
            
@spaces.GPU(duration=60, enable_queue=True)
def generate(prompt):
    \"\"\"This function starts the worker thread and yields updates from the queue.\"\"\"   
    yield None, None, gr.update(interactive=False)    
    update_queue = queue.Queue()
    diffusion_thread = threading.Thread(target=run_diffusion_in_thread,  args=(prompt, False, update_queue))
    diffusion_thread.start()
    final_images = None
    while True:
        update = update_queue.get()
        if update is None: 
            break
        
        images, log_update = update
        
        if images:
            final_images = images
      
        yield final_images, log_update, gr.skip()
    
    yield final_images, log_update, gr.update(interactive=True)

# --- 4. THE COMBINED GRADIO UI with TABS ---
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.HTML("<h1><center>LiveLog Component Showcase</center></h1>")

    with gr.Tabs():
        with gr.TabItem("LiveLog Feature Demo"):            
            gr.Markdown("### Test all features of the LiveLog component interactively.")
            with gr.Row():
                with gr.Column(scale=3):
                    feature_logger = LiveLog(
                        label="Process Output", line_numbers=True, height=550,
                        background_color="#000000", display_mode="full"
                    )
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### Component Properties")
                        display_mode_radio = gr.Radio(["full", "log", "progress"], label="Display Mode", value="full")
                        rate_unit = gr.Radio(["it/s","s/it"], label="Progress rate unit", value="it/s")
                        bg_color_picker = gr.ColorPicker(label="Background Color", value="#000000")
                        line_numbers_checkbox = gr.Checkbox(label="Show Line Numbers", value=True)
                        autoscroll_checkbox = gr.Checkbox(label="Autoscroll", value=True)
                        disable_console_checkbox = gr.Checkbox(label="Disable Python Console Output", value=False)
                    with gr.Group():
                        gr.Markdown("### Simulation Controls")
                        start_btn = gr.Button("Run Success Case", variant="primary")
                        error_btn = gr.Button("Run Error Case")
            
            start_btn.click(fn=run_success_case, inputs=[disable_console_checkbox, rate_unit], outputs=feature_logger)
            error_btn.click(fn=run_error_case, inputs=[disable_console_checkbox, rate_unit], outputs=feature_logger)
            feature_logger.clear(fn=clear_output, inputs=None, outputs=feature_logger)
            controls = [display_mode_radio, bg_color_picker, line_numbers_checkbox, autoscroll_checkbox]
            for control in controls:
                control.change(fn=update_livelog_properties, inputs=controls, outputs=feature_logger)
        
        with gr.TabItem("Diffusion Pipeline Integration"):               
            gr.Markdown("### Use `LiveLog` to monitor a real image generation process.")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Group():
                        prompt = gr.Textbox(
                            label="Enter your prompt", show_label=False,
                            placeholder="A cinematic photo of a robot in a floral garden...",
                            scale=8, container=False
                        )
                        run_button = gr.Button("Generate", scale=1, variant="primary")
                    
                    livelog_viewer = LiveLog(
                        label="Process Monitor", height=250, display_mode="full", line_numbers=False
                    )
                
                with gr.Column(scale=2):
                    result_gallery = gr.Gallery(
                        label="Result", columns=1, show_label=False, height=500, min_width=768, preview=True, allow_preview=True
                    )
            
            run_button.click(fn=generate, inputs=[prompt], outputs=[result_gallery, livelog_viewer, run_button])
            prompt.submit(fn=generate, inputs=[prompt], outputs=[result_gallery, livelog_viewer])
            livelog_viewer.clear(fn=clear_output, inputs=None, outputs=[livelog_viewer])
            
    # This ensures the model is downloaded/loaded once when the app starts.
    demo.load(load_pipeline, None, None)
                
if __name__ == "__main__":
    demo.queue(max_size=50).launch(debug=True)
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `LiveLog`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["LiveLog"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["LiveLog"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As output:** Should return, the output data received by the component from the user's function in the backend.

 ```python
def predict(
    value: typing.Optional[typing.List[typing.Dict[str, typing.Any]]][
    typing.List[typing.Dict[str, typing.Any]][
        typing.Dict[str, typing.Any][str, Any]
    ],
    None,
]
) -> typing.Optional[typing.List[typing.Dict[str, typing.Any]]][
    typing.List[typing.Dict[str, typing.Any]][
        typing.Dict[str, typing.Any][str, Any]
    ],
    None,
]:
    return value
```
""", elem_classes=["md-custom", "LiveLog-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          LiveLog: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
