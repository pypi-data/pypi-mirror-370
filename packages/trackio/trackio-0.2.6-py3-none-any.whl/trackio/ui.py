import os
import re
import shutil
from typing import Any

import gradio as gr
import huggingface_hub as hf
import numpy as np
import pandas as pd

HfApi = hf.HfApi()

try:
    from trackio.sqlite_storage import SQLiteStorage
    from trackio.typehints import LogEntry
    from trackio.utils import (
        RESERVED_KEYS,
        TRACKIO_LOGO_DIR,
        downsample,
        get_color_mapping,
    )
except:  # noqa: E722
    from sqlite_storage import SQLiteStorage
    from typehints import LogEntry
    from utils import RESERVED_KEYS, TRACKIO_LOGO_DIR, downsample, get_color_mapping


def get_projects(request: gr.Request):
    dataset_id = os.environ.get("TRACKIO_DATASET_ID")
    projects = SQLiteStorage.get_projects()
    if project := request.query_params.get("project"):
        interactive = False
    else:
        interactive = True
        project = projects[0] if projects else None
    return gr.Dropdown(
        label="Project",
        choices=projects,
        value=project,
        allow_custom_value=True,
        interactive=interactive,
        info=f"&#x21bb; Synced to <a href='https://huggingface.co/datasets/{dataset_id}' target='_blank'>{dataset_id}</a> every 5 min"
        if dataset_id
        else None,
    )


def get_runs(project) -> list[str]:
    if not project:
        return []
    return SQLiteStorage.get_runs(project)


def get_available_metrics(project: str, runs: list[str]) -> list[str]:
    """Get all available metrics across all runs for x-axis selection."""
    if not project or not runs:
        return ["step", "time"]

    all_metrics = set()
    for run in runs:
        metrics = SQLiteStorage.get_metrics(project, run)
        if metrics:
            df = pd.DataFrame(metrics)
            numeric_cols = df.select_dtypes(include="number").columns
            numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]
            all_metrics.update(numeric_cols)

    # Always include step and time as options
    all_metrics.add("step")
    all_metrics.add("time")

    # Sort metrics by prefix
    sorted_metrics = sort_metrics_by_prefix(list(all_metrics))

    # Put step and time at the beginning
    result = ["step", "time"]
    for metric in sorted_metrics:
        if metric not in result:
            result.append(metric)

    return result


def load_run_data(
    project: str | None,
    run: str | None,
    smoothing: bool,
    x_axis: str,
    log_scale: bool = False,
):
    if not project or not run:
        return None
    metrics = SQLiteStorage.get_metrics(project, run)
    if not metrics:
        return None
    df = pd.DataFrame(metrics)

    if "step" not in df.columns:
        df["step"] = range(len(df))

    if x_axis == "time" and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        first_timestamp = df["timestamp"].min()
        df["time"] = (df["timestamp"] - first_timestamp).dt.total_seconds()
        x_column = "time"
    elif x_axis == "step":
        x_column = "step"
    else:
        x_column = x_axis

    if log_scale and x_column in df.columns:
        x_vals = df[x_column]
        if (x_vals <= 0).any():
            df[x_column] = np.log10(np.maximum(x_vals, 0) + 1)
        else:
            df[x_column] = np.log10(x_vals)

    if smoothing:
        numeric_cols = df.select_dtypes(include="number").columns
        numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]

        df_original = df.copy()
        df_original["run"] = f"{run}_original"
        df_original["data_type"] = "original"

        df_smoothed = df.copy()
        window_size = max(3, min(10, len(df) // 10))  # Adaptive window size
        df_smoothed[numeric_cols] = (
            df_smoothed[numeric_cols]
            .rolling(window=window_size, center=True, min_periods=1)
            .mean()
        )
        df_smoothed["run"] = f"{run}_smoothed"
        df_smoothed["data_type"] = "smoothed"

        combined_df = pd.concat([df_original, df_smoothed], ignore_index=True)
        combined_df["x_axis"] = x_column
        return combined_df
    else:
        df["run"] = run
        df["data_type"] = "original"
        df["x_axis"] = x_column
        return df


def update_runs(project, filter_text, user_interacted_with_runs=False):
    if project is None:
        runs = []
        num_runs = 0
    else:
        runs = get_runs(project)
        num_runs = len(runs)
        if filter_text:
            runs = [r for r in runs if filter_text in r]
    if not user_interacted_with_runs:
        return gr.CheckboxGroup(choices=runs, value=runs), gr.Textbox(
            label=f"Runs ({num_runs})"
        )
    else:
        return gr.CheckboxGroup(choices=runs), gr.Textbox(label=f"Runs ({num_runs})")


def filter_runs(project, filter_text):
    runs = get_runs(project)
    runs = [r for r in runs if filter_text in r]
    return gr.CheckboxGroup(choices=runs, value=runs)


def update_x_axis_choices(project, runs):
    """Update x-axis dropdown choices based on available metrics."""
    available_metrics = get_available_metrics(project, runs)
    return gr.Dropdown(
        label="X-axis",
        choices=available_metrics,
        value="step",
    )


def toggle_timer(cb_value):
    if cb_value:
        return gr.Timer(active=True)
    else:
        return gr.Timer(active=False)


def check_auth(hf_token: str | None) -> None:
    if os.getenv("SYSTEM") == "spaces":  # if we are running in Spaces
        # check auth token passed in
        if hf_token is None:
            raise PermissionError(
                "Expected a HF_TOKEN to be provided when logging to a Space"
            )
        who = HfApi.whoami(hf_token)
        access_token = who["auth"]["accessToken"]
        owner_name = os.getenv("SPACE_AUTHOR_NAME")
        repo_name = os.getenv("SPACE_REPO_NAME")
        # make sure the token user is either the author of the space,
        # or is a member of an org that is the author.
        orgs = [o["name"] for o in who["orgs"]]
        if owner_name != who["name"] and owner_name not in orgs:
            raise PermissionError(
                "Expected the provided hf_token to be the user owner of the space, or be a member of the org owner of the space"
            )
        # reject fine-grained tokens without specific repo access
        if access_token["role"] == "fineGrained":
            matched = False
            for item in access_token["fineGrained"]["scoped"]:
                if (
                    item["entity"]["type"] == "space"
                    and item["entity"]["name"] == f"{owner_name}/{repo_name}"
                    and "repo.write" in item["permissions"]
                ):
                    matched = True
                    break
                if (
                    (
                        item["entity"]["type"] == "user"
                        or item["entity"]["type"] == "org"
                    )
                    and item["entity"]["name"] == owner_name
                    and "repo.write" in item["permissions"]
                ):
                    matched = True
                    break
            if not matched:
                raise PermissionError(
                    "Expected the provided hf_token with fine grained permissions to provide write access to the space"
                )
        # reject read-only tokens
        elif access_token["role"] != "write":
            raise PermissionError(
                "Expected the provided hf_token to provide write permissions"
            )


def upload_db_to_space(
    project: str, uploaded_db: gr.FileData, hf_token: str | None
) -> None:
    check_auth(hf_token)
    db_project_path = SQLiteStorage.get_project_db_path(project)
    if os.path.exists(db_project_path):
        raise gr.Error(
            f"Trackio database file already exists for project {project}, cannot overwrite."
        )
    os.makedirs(os.path.dirname(db_project_path), exist_ok=True)
    shutil.copy(uploaded_db["path"], db_project_path)


def log(
    project: str,
    run: str,
    metrics: dict[str, Any],
    step: int | None,
    hf_token: str | None,
) -> None:
    check_auth(hf_token)
    SQLiteStorage.log(project=project, run=run, metrics=metrics, step=step)


def bulk_log(
    logs: list[LogEntry],
    hf_token: str | None,
) -> None:
    check_auth(hf_token)

    logs_by_run = {}
    for log_entry in logs:
        key = (log_entry["project"], log_entry["run"])
        if key not in logs_by_run:
            logs_by_run[key] = {"metrics": [], "steps": []}
        logs_by_run[key]["metrics"].append(log_entry["metrics"])
        logs_by_run[key]["steps"].append(log_entry.get("step"))

    for (project, run), data in logs_by_run.items():
        SQLiteStorage.bulk_log(
            project=project,
            run=run,
            metrics_list=data["metrics"],
            steps=data["steps"],
        )


def filter_metrics_by_regex(metrics: list[str], filter_pattern: str) -> list[str]:
    """
    Filter metrics using regex pattern.

    Args:
        metrics: List of metric names to filter
        filter_pattern: Regex pattern to match against metric names

    Returns:
        List of metric names that match the pattern
    """
    if not filter_pattern.strip():
        return metrics

    try:
        pattern = re.compile(filter_pattern, re.IGNORECASE)
        return [metric for metric in metrics if pattern.search(metric)]
    except re.error:
        return [
            metric for metric in metrics if filter_pattern.lower() in metric.lower()
        ]


def sort_metrics_by_prefix(metrics: list[str]) -> list[str]:
    """
    Sort metrics by grouping prefixes together.
    Metrics without prefixes come first, then grouped by prefix.

    Example:
    Input: ["train/loss", "loss", "train/acc", "val/loss"]
    Output: ["loss", "train/acc", "train/loss", "val/loss"]
    """
    no_prefix = []
    with_prefix = []

    for metric in metrics:
        if "/" in metric:
            with_prefix.append(metric)
        else:
            no_prefix.append(metric)

    no_prefix.sort()

    prefix_groups = {}
    for metric in with_prefix:
        prefix = metric.split("/")[0]
        if prefix not in prefix_groups:
            prefix_groups[prefix] = []
        prefix_groups[prefix].append(metric)

    sorted_with_prefix = []
    for prefix in sorted(prefix_groups.keys()):
        sorted_with_prefix.extend(sorted(prefix_groups[prefix]))

    return no_prefix + sorted_with_prefix


def configure(request: gr.Request):
    sidebar_param = request.query_params.get("sidebar")
    match sidebar_param:
        case "collapsed":
            sidebar = gr.Sidebar(open=False, visible=True)
        case "hidden":
            sidebar = gr.Sidebar(open=False, visible=False)
        case _:
            sidebar = gr.Sidebar(open=True, visible=True)

    if metrics := request.query_params.get("metrics"):
        return metrics.split(","), sidebar
    else:
        return [], sidebar


css = """
#run-cb .wrap { gap: 2px; }
#run-cb .wrap label {
    line-height: 1;
    padding: 6px;
}
.logo-light { display: block; } 
.logo-dark { display: none; }
.dark .logo-light { display: none; }
.dark .logo-dark { display: block; }
"""

with gr.Blocks(theme="citrus", title="Trackio Dashboard", css=css) as demo:
    with gr.Sidebar(open=False) as sidebar:
        logo = gr.Markdown(
            f"""
                <img src='/gradio_api/file={TRACKIO_LOGO_DIR}/trackio_logo_type_light_transparent.png' width='80%' class='logo-light'>
                <img src='/gradio_api/file={TRACKIO_LOGO_DIR}/trackio_logo_type_dark_transparent.png' width='80%' class='logo-dark'>            
            """
        )
        project_dd = gr.Dropdown(label="Project", allow_custom_value=True)
        run_tb = gr.Textbox(label="Runs", placeholder="Type to filter...")
        run_cb = gr.CheckboxGroup(
            label="Runs", choices=[], interactive=True, elem_id="run-cb"
        )
        gr.HTML("<hr>")
        realtime_cb = gr.Checkbox(label="Refresh metrics realtime", value=True)
        smoothing_cb = gr.Checkbox(label="Smooth metrics", value=True)
        x_axis_dd = gr.Dropdown(
            label="X-axis",
            choices=["step", "time"],
            value="step",
        )
        log_scale_cb = gr.Checkbox(label="Log scale X-axis", value=False)
        metric_filter_tb = gr.Textbox(
            label="Metric Filter (regex)",
            placeholder="e.g., loss|ndcg@10|gpu",
            value="",
            info="Filter metrics using regex patterns. Leave empty to show all metrics.",
        )

    timer = gr.Timer(value=1)
    metrics_subset = gr.State([])
    user_interacted_with_run_cb = gr.State(False)

    gr.on([demo.load], fn=configure, outputs=[metrics_subset, sidebar])
    gr.on(
        [demo.load],
        fn=get_projects,
        outputs=project_dd,
        show_progress="hidden",
    )
    gr.on(
        [timer.tick],
        fn=update_runs,
        inputs=[project_dd, run_tb, user_interacted_with_run_cb],
        outputs=[run_cb, run_tb],
        show_progress="hidden",
    )
    gr.on(
        [demo.load, project_dd.change],
        fn=update_runs,
        inputs=[project_dd, run_tb],
        outputs=[run_cb, run_tb],
        show_progress="hidden",
    )
    gr.on(
        [demo.load, project_dd.change, run_cb.change],
        fn=update_x_axis_choices,
        inputs=[project_dd, run_cb],
        outputs=x_axis_dd,
        show_progress="hidden",
    )

    realtime_cb.change(
        fn=toggle_timer,
        inputs=realtime_cb,
        outputs=timer,
        api_name="toggle_timer",
    )
    run_cb.input(
        fn=lambda: True,
        outputs=user_interacted_with_run_cb,
    )
    run_tb.input(
        fn=filter_runs,
        inputs=[project_dd, run_tb],
        outputs=run_cb,
    )

    gr.api(
        fn=upload_db_to_space,
        api_name="upload_db_to_space",
    )
    gr.api(
        fn=log,
        api_name="log",
    )
    gr.api(
        fn=bulk_log,
        api_name="bulk_log",
    )

    x_lim = gr.State(None)
    last_steps = gr.State({})

    def update_x_lim(select_data: gr.SelectData):
        return select_data.index

    def update_last_steps(project, runs):
        """Update the last step from all runs to detect when new data is available."""
        if not project or not runs:
            return {}

        return SQLiteStorage.get_max_steps_for_runs(project, runs)

    timer.tick(
        fn=update_last_steps,
        inputs=[project_dd, run_cb],
        outputs=last_steps,
        show_progress="hidden",
    )

    @gr.render(
        triggers=[
            demo.load,
            run_cb.change,
            last_steps.change,
            smoothing_cb.change,
            x_lim.change,
            x_axis_dd.change,
            log_scale_cb.change,
            metric_filter_tb.change,
        ],
        inputs=[
            project_dd,
            run_cb,
            smoothing_cb,
            metrics_subset,
            x_lim,
            x_axis_dd,
            log_scale_cb,
            metric_filter_tb,
        ],
        show_progress="hidden",
    )
    def update_dashboard(
        project,
        runs,
        smoothing,
        metrics_subset,
        x_lim_value,
        x_axis,
        log_scale,
        metric_filter,
    ):
        dfs = []
        original_runs = runs.copy()

        for run in runs:
            df = load_run_data(project, run, smoothing, x_axis, log_scale)
            if df is not None:
                dfs.append(df)

        if dfs:
            master_df = pd.concat(dfs, ignore_index=True)
        else:
            master_df = pd.DataFrame()

        if master_df.empty:
            return

        x_column = "step"
        if dfs and not dfs[0].empty and "x_axis" in dfs[0].columns:
            x_column = dfs[0]["x_axis"].iloc[0]

        numeric_cols = master_df.select_dtypes(include="number").columns
        numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]
        if metrics_subset:
            numeric_cols = [c for c in numeric_cols if c in metrics_subset]

        if metric_filter and metric_filter.strip():
            numeric_cols = filter_metrics_by_regex(list(numeric_cols), metric_filter)

        numeric_cols = sort_metrics_by_prefix(list(numeric_cols))
        color_map = get_color_mapping(original_runs, smoothing)

        with gr.Row(key="row"):
            for metric_idx, metric_name in enumerate(numeric_cols):
                metric_df = master_df.dropna(subset=[metric_name])
                color = "run" if "run" in metric_df.columns else None
                if not metric_df.empty:
                    plot = gr.LinePlot(
                        downsample(
                            metric_df, x_column, metric_name, color, x_lim_value
                        ),
                        x=x_column,
                        y=metric_name,
                        color=color,
                        color_map=color_map,
                        title=metric_name,
                        key=f"plot-{metric_idx}",
                        preserved_by_key=None,
                        x_lim=x_lim_value,
                        show_fullscreen_button=True,
                        min_width=400,
                    )
                plot.select(update_x_lim, outputs=x_lim, key=f"select-{metric_idx}")
                plot.double_click(
                    lambda: None, outputs=x_lim, key=f"double-{metric_idx}"
                )


if __name__ == "__main__":
    demo.launch(allowed_paths=[TRACKIO_LOGO_DIR], show_api=False, show_error=True)
