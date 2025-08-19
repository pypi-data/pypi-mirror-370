from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import gradio as gr

from ..memoryset import LabeledMemoryLookup, ScoredMemoryLookup, LabeledMemoryset

if TYPE_CHECKING:
    from ..telemetry import _Prediction


def inspect_prediction_result(prediction_result: _Prediction):

    def update_label(val: str, memory: LabeledMemoryLookup, progress=gr.Progress(track_tqdm=True)):
        progress(0)
        match = re.search(r".*\((\d+)\)$", val)
        if match:
            progress(0.5)
            new_label = int(match.group(1))
            memory.update(label=new_label)
            progress(1)
            return "&#9989; Changes saved"
        else:
            logging.error(f"Invalid label format: {val}")

    def update_score(val: float, memory: ScoredMemoryLookup, progress=gr.Progress(track_tqdm=True)):
        progress(0)
        memory.update(score=val)
        progress(1)
        return "&#9989; Changes saved"

    with gr.Blocks(
        fill_width=True,
        title="Prediction Results",
        css_paths=str(Path(__file__).parent / "prediction_result_ui.css"),
    ) as prediction_result_ui:
        gr.Markdown("# Prediction Results")
        gr.Markdown(f"**Input:** {prediction_result.input_value}")

        if isinstance(prediction_result.memoryset, LabeledMemoryset) and prediction_result.label is not None:
            label_names = prediction_result.memoryset.label_names
            gr.Markdown(f"**Prediction:** {label_names[prediction_result.label]} ({prediction_result.label})")
        else:
            gr.Markdown(f"**Prediction:** {prediction_result.score:.2f}")

        gr.Markdown("### Memory Lookups")

        with gr.Row(equal_height=True, variant="panel"):
            with gr.Column(scale=7):
                gr.Markdown("**Value**")
            with gr.Column(scale=3, min_width=150):
                gr.Markdown("**Label**" if prediction_result.label is not None else "**Score**")

        for i, mem_lookup in enumerate(prediction_result.memory_lookups):
            with gr.Row(equal_height=True, variant="panel", elem_classes="white" if i % 2 == 0 else None):
                with gr.Column(scale=7):
                    gr.Markdown(
                        (
                            mem_lookup.value
                            if isinstance(mem_lookup.value, str)
                            else "Time series data" if isinstance(mem_lookup.value, list) else "Image data"
                        ),
                        label="Value",
                        height=50,
                    )
                with gr.Column(scale=3, min_width=150):
                    if (
                        isinstance(prediction_result.memoryset, LabeledMemoryset)
                        and prediction_result.label is not None
                        and isinstance(mem_lookup, LabeledMemoryLookup)
                    ):
                        label_names = prediction_result.memoryset.label_names
                        dropdown = gr.Dropdown(
                            choices=[f"{label_name} ({i})" for i, label_name in enumerate(label_names)],
                            label="Label",
                            value=f"{label_names[mem_lookup.label]} ({mem_lookup.label})",
                            interactive=True,
                            container=False,
                        )
                        changes_saved = gr.HTML(lambda: "", elem_classes="success no-padding", every=15)
                        dropdown.change(
                            lambda val, mem=mem_lookup: update_label(val, mem),
                            inputs=[dropdown],
                            outputs=[changes_saved],
                            show_progress="full",
                        )
                    elif prediction_result.score is not None and isinstance(mem_lookup, ScoredMemoryLookup):
                        input = gr.Number(
                            value=mem_lookup.score,
                            label="Score",
                            interactive=True,
                            container=False,
                        )
                        changes_saved = gr.HTML(lambda: "", elem_classes="success no-padding", every=15)
                        input.change(
                            lambda val, mem=mem_lookup: update_score(val, mem),
                            inputs=[input],
                            outputs=[changes_saved],
                            show_progress="full",
                        )

    prediction_result_ui.launch()
