from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TypedDict, cast

import gradio as gr

from ..memoryset import LabeledMemory, LabeledMemoryset

# Suppress all httpx logs
logging.getLogger("httpx").setLevel(logging.CRITICAL)

# Optionally suppress other libraries Gradio might use
logging.getLogger("gradio").setLevel(logging.CRITICAL)


class RelabelStatus(TypedDict):
    memory_id: str
    approved: bool
    new_label: int | None
    full_memory: LabeledMemory


def display_suggested_memory_relabels(memoryset: LabeledMemoryset):
    suggested_relabels = memoryset.query(
        filters=[("metrics.neighbor_predicted_label_matches_current_label", "==", False)]
    )
    # Sort memories by confidence score (higher confidence first)
    suggested_relabels.sort(key=lambda x: (x.metrics.get("neighbor_predicted_label_confidence", 0.0)), reverse=True)

    def update_approved(memory_id: str, selected: bool, current_memory_relabel_map: dict[str, RelabelStatus]):
        current_memory_relabel_map[memory_id]["approved"] = selected
        return current_memory_relabel_map

    def approve_all(current_all_approved, selected: bool):
        for mem_id in current_all_approved:
            current_all_approved[mem_id]["approved"] = selected
        return current_all_approved, selected

    def apply_selected(current_memory_relabel_map: dict[str, RelabelStatus], progress=gr.Progress(track_tqdm=True)):
        progress(0, desc="Processing label updates...")
        to_be_deleted = []
        approved_relabels = [mem for mem in current_memory_relabel_map.values() if mem["approved"]]
        for memory in progress.tqdm(approved_relabels, desc="Applying label updates..."):
            memory = cast(RelabelStatus, memory)
            new_label = memory["new_label"]
            assert isinstance(new_label, int)
            memoryset.update(
                {
                    "memory_id": memory["memory_id"],
                    "label": new_label,
                }
            )
            to_be_deleted.append(memory["memory_id"])
        for mem_id in to_be_deleted:
            del current_memory_relabel_map[mem_id]
        return (
            current_memory_relabel_map,
            gr.HTML(
                f"<h1 style='display: inline-block; position: fixed; z-index: 1000; left: 36px; top: 14px;'>Suggested Label Updates: {len(current_memory_relabel_map)}</h1>",
            ),
        )

    def update_label(mem_id: str, label: str, current_memory_relabel_map: dict[str, RelabelStatus]):
        match = re.search(r".*\((\d+)\)$", label)
        if match:
            new_label = int(match.group(1))
            current_memory_relabel_map[mem_id]["new_label"] = new_label
            confidence = "--"
            current_metrics = current_memory_relabel_map[mem_id]["full_memory"].metrics
            if current_metrics and new_label == current_metrics.get("neighbor_predicted_label"):
                confidence = (
                    round(current_metrics.get("neighbor_predicted_label_confidence", 0.0), 2) if current_metrics else 0
                )
            return (
                gr.HTML(
                    f"<p style='font-size: 10px; color: #888;'>Confidence: {confidence}</p>",
                    elem_classes="no-padding",
                ),
                current_memory_relabel_map,
            )
        else:
            logging.error(f"Invalid label format: {label}")

    with gr.Blocks(
        fill_width=True,
        title="Suggested Label Updates",
        css_paths=str(Path(__file__).parent / "analysis_ui_style.css"),
    ) as demo:
        label_names = memoryset.label_names

        refresh = gr.State(False)
        all_approved = gr.State(False)
        memory_relabel_map = gr.State(
            {
                mem.memory_id: RelabelStatus(
                    memory_id=mem.memory_id,
                    approved=False,
                    new_label=(
                        mem.metrics.get("neighbor_predicted_label")
                        if (mem.metrics and isinstance(mem.metrics.get("neighbor_predicted_label"), int))
                        else None
                    ),
                    full_memory=mem,
                )
                for mem in suggested_relabels
            }
        )

        @gr.render(
            inputs=[memory_relabel_map, all_approved],
            triggers=[demo.load, refresh.change, all_approved.change, memory_relabel_map.change],
        )
        def render_table(current_memory_relabel_map, current_all_approved):
            if len(current_memory_relabel_map):
                with gr.Group(elem_classes="header"):
                    title = gr.HTML(
                        f"<h1 style='display: inline-block; position: fixed; z-index: 1000; left: 36px; top: 14px;'>Suggested Label Updates: {len(current_memory_relabel_map)}</h1>"
                    )
                    apply_selected_button = gr.Button("Apply Selected", elem_classes="button")
                    apply_selected_button.click(
                        apply_selected,
                        inputs=[memory_relabel_map],
                        outputs=[memory_relabel_map, title],
                        show_progress="full",
                    )
                with gr.Row(equal_height=True, variant="panel", elem_classes="margin-top"):
                    with gr.Column(scale=9):
                        gr.Markdown("**Value**")
                    with gr.Column(scale=2, min_width=90):
                        gr.Markdown("**Current Label**")
                    with gr.Column(scale=3, min_width=150):
                        gr.Markdown("**Suggested Label**", elem_classes="centered")
                    with gr.Column(scale=2, min_width=50):
                        approve_all_checkbox = gr.Checkbox(
                            show_label=False,
                            value=current_all_approved,
                            label="",
                            container=False,
                            elem_classes="centered",
                        )
                        approve_all_checkbox.change(
                            approve_all,
                            inputs=[memory_relabel_map, approve_all_checkbox],
                            outputs=[memory_relabel_map, all_approved],
                        )
                for i, memory_relabel in enumerate(current_memory_relabel_map.values()):
                    mem = memory_relabel["full_memory"]
                    predicted_label = mem.metrics["neighbor_predicted_label"]
                    predicted_label_name = label_names[predicted_label]
                    predicted_label_confidence = mem.metrics.get("neighbor_predicted_label_confidence", 0)

                    with gr.Row(equal_height=True, variant="panel"):
                        with gr.Column(scale=9):
                            assert isinstance(mem.value, str)
                            gr.Markdown(mem.value, label="Value", height=50)
                        with gr.Column(scale=2, min_width=90):
                            gr.Markdown(f"{mem.label_name} ({mem.label})", label="Current Label", height=50)
                        with gr.Column(scale=3, min_width=150):
                            dropdown = gr.Dropdown(
                                choices=[f"{label_name} ({i})" for i, label_name in enumerate(label_names)],
                                label="SuggestedLabel",
                                value=f"{predicted_label_name} ({predicted_label})",
                                interactive=True,
                                container=False,
                            )
                            confidence = gr.HTML(
                                f"<p style='font-size: 10px; color: #888;'>Confidence: {predicted_label_confidence:.2f}</p>",
                                elem_classes="no-padding",
                            )
                            dropdown.change(
                                lambda val, map, mem_id=mem.memory_id: update_label(mem_id, val, map),
                                inputs=[dropdown, memory_relabel_map],
                                outputs=[confidence, memory_relabel_map],
                            )
                        with gr.Column(scale=2, min_width=50):
                            checkbox = gr.Checkbox(
                                show_label=False,
                                label="",
                                value=current_memory_relabel_map[mem.memory_id]["approved"],
                                container=False,
                                elem_classes="centered",
                                interactive=True,
                            )
                            checkbox.input(
                                lambda selected, map, mem_id=mem.memory_id: update_approved(mem_id, selected, map),
                                inputs=[checkbox, memory_relabel_map],
                                outputs=[memory_relabel_map],
                            )

            else:
                gr.HTML("<h1>No suggested label updates</h1>")

    demo.launch()
