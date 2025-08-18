#!/usr/bin/env python3
"""
A comprehensive, single-file tool for the collection, processing, and
analysis of robot trajectory data for academic publications.

This script provides a full workflow via four commands:
  1. collect:  (Requires ROS 2) Records raw trajectory data from TF2 frames.
  2. process:  Calculates performance metrics from raw data files.
  3. report:   Generates all publication-quality png plots and LaTeX tables.
  4. animate:  Creates a high-quality video of a single experimental run.
"""

import argparse
import json
import math
import threading
from itertools import cycle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import rclpy
import seaborn as sns
from rclpy.node import Node
from rclpy.time import Duration, Time
from tf2_ros import Buffer, TransformListener

plt.style.use("seaborn-v0_8-whitegrid")
PLOT_STYLE = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Bitstream Vera Serif", "serif"],
    "axes.labelsize": 14,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 12,
    "figure.titlesize": 16,
    "figure.dpi": 300,
}
plt.rcParams.update(PLOT_STYLE)


class TrajectoryCollectorNode(Node):
    """ROS 2 Node for high-fidelity recording of trajectory and orientation data."""

    def __init__(self, args: argparse.Namespace):
        super().__init__("trajectory_collector")
        self.output_file = args.output
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.fixed_frame = args.fixed_frame
        self.robot_frame = args.robot_frame
        self.target_frame = args.target_frame
        self.data_lock = threading.Lock()
        self.data: List[Dict[str, float]] = []
        self.start_time: Optional[Time] = None

        self.timer = self.create_timer(1.0 / args.rate, self.timer_callback)
        self.get_logger().info("Collector started.")
        self.get_logger().info(f"Saving raw data to: {self.output_file}")
        self.get_logger().info(
            f"Tracking '{self.robot_frame}' and '{self.target_frame}' relative to '{self.fixed_frame}'."
        )
        self.get_logger().info("Press Ctrl+C to stop collection and save.")

    @staticmethod
    def _quaternion_to_yaw(q) -> float:
        """Converts a ROS Quaternion to a yaw angle in radians."""
        return math.atan2(
            2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

    def timer_callback(self):
        try:
            now = self.get_clock().now()
            robot_tf = self.tf_buffer.lookup_transform(
                self.fixed_frame,
                self.robot_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
            target_tf = self.tf_buffer.lookup_transform(
                self.fixed_frame,
                self.target_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )

            if self.start_time is None:
                self.start_time = now
                self.get_logger().info("First transform received. Recording started.")

            time_elapsed = (now - self.start_time).nanoseconds / 1e9
            robot_yaw = self._quaternion_to_yaw(robot_tf.transform.rotation)
            target_yaw = self._quaternion_to_yaw(target_tf.transform.rotation)

            with self.data_lock:
                self.data.append(
                    {
                        "time": time_elapsed,
                        "robot_x": robot_tf.transform.translation.x,
                        "robot_y": robot_tf.transform.translation.y,
                        "robot_yaw": robot_yaw,
                        "target_x": target_tf.transform.translation.x,
                        "target_y": target_tf.transform.translation.y,
                        "target_yaw": target_yaw,
                    }
                )
        except Exception as e:
            self.get_logger().warn(f"TF lookup failed: {e}", throttle_duration_sec=5.0)

    def save_data(self):
        """Saves the collected data to a CSV file upon shutdown."""
        self.get_logger().info("Shutdown signal received. Saving data...")
        if not self.data:
            self.get_logger().warn("No data was collected. Exiting without saving.")
            return
        df = pd.DataFrame(self.data)
        df.to_csv(self.output_file, index=False)
        self.get_logger().info(f"Saved {len(df)} data points to {self.output_file}")


def _process_file(input_path: Path):
    """Calculates performance metrics for a single raw trajectory file."""
    print(f"Processing: {input_path.name}")
    try:
        df = pd.read_csv(input_path)
    except pd.errors.EmptyDataError:
        print("  -> Skipping, file is empty.")
        return

    if len(df) < 5:
        print(
            "  -> Skipping, requires at least 5 data points for stable derivative calculation."
        )
        return

    df = df.sort_values(by="time").reset_index(drop=True)
    dt = df["time"].diff()
    dt.iloc[0] = dt.median()
    dt_filled = dt.replace(0, 1e-9)

    df["euclidean_error"] = np.sqrt(
        (df["target_x"] - df["robot_x"]) ** 2 + (df["target_y"] - df["robot_y"]) ** 2
    )

    orientation_error_raw = df["target_yaw"] - df["robot_yaw"]
    df["orientation_error_rad"] = np.arctan2(
        np.sin(orientation_error_raw), np.cos(orientation_error_raw)
    )

    df["robot_velocity"] = (
        np.sqrt(df["robot_x"].diff() ** 2 + df["robot_y"].diff() ** 2) / dt_filled
    ).fillna(0)
    df["robot_accel"] = (df["robot_velocity"].diff() / dt_filled).fillna(0)
    df["robot_jerk"] = (df["robot_accel"].diff() / dt_filled).fillna(0)

    summary = {
        "ate_m": df["euclidean_error"].mean(),
        "ate_rad": df["orientation_error_rad"].abs().mean(),
        "jerk_avg_m_s3": df["robot_jerk"].abs().mean(),
    }

    processed_csv_path = input_path.with_name(f"{input_path.stem}_processed.csv")
    summary_json_path = input_path.with_name(f"{input_path.stem}_summary.json")

    df.to_csv(processed_csv_path, index=False)
    with open(summary_json_path, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"  -> Saved processed data and summary for {input_path.name}")


def _load_and_group_experiments(
    exp_definitions: List[Tuple[str, str]],
) -> Dict[str, Dict[str, List[Path]]]:
    """Groups experiment files by trajectory and method for comparative analysis."""
    grouped_results = {}
    print("--- Loading and Grouping Experiment Files ---")
    for method_name, glob_pattern in exp_definitions:
        paths = sorted(list(Path(".").glob(glob_pattern)))
        if not paths:
            print(
                f"Warning: No files found for method '{method_name}' with pattern '{glob_pattern}'"
            )
            continue
        print(f"Found {len(paths)} files for method '{method_name}'")
        for path in paths:
            traj_name = path.stem.split("_")[0]
            if traj_name not in grouped_results:
                grouped_results[traj_name] = {}
            if method_name not in grouped_results[traj_name]:
                grouped_results[traj_name][method_name] = []
            grouped_results[traj_name][method_name].append(path)
    return grouped_results


def _plot_trajectories_with_confidence(grouped_results: Dict, output_dir: Path):
    """
    Generates trajectory plots centered at the origin with a shaded confidence interval
    and saves as png.
    """
    print(
        "\n--- Generating Centered Trajectory Plots with Confidence Intervals (png) ---"
    )

    color_palette = sns.color_palette("colorblind")
    method_color_map = {
        "DreamerV3": color_palette[0],
        "PPO": color_palette[1],
        "TD3": color_palette[2],
        "PPO (LSTM)": color_palette[3],
    }
    target_path_color = "black"
    fallback_colors = cycle(color_palette[4:] + color_palette[:4])

    for traj_name, methods in grouped_results.items():
        fig, ax = plt.subplots(figsize=(8, 8))

        target_df_for_centering = None
        for method_name, paths in methods.items():
            for p in paths:
                proc_path = p.with_name(f"{p.stem}_processed.csv")
                if proc_path.exists():
                    df_temp = pd.read_csv(proc_path)
                    if not df_temp.empty:
                        target_df_for_centering = df_temp[
                            [
                                "target_x",
                                "target_y",
                            ]
                        ].copy()
                        break
            if target_df_for_centering is not None:
                break

        if target_df_for_centering is None:
            print(f"Skipping plot for '{traj_name}' due to missing data.")
            plt.close(fig)
            continue

        min_x = target_df_for_centering["target_x"].min()
        max_x = target_df_for_centering["target_x"].max()
        min_y = target_df_for_centering["target_y"].min()
        max_y = target_df_for_centering["target_y"].max()
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        target_df_plotted = False
        for i, (method_name, paths) in enumerate(methods.items()):
            all_x, all_y = [], []
            target_df = None
            for p in paths:
                proc_path = p.with_name(f"{p.stem}_processed.csv")
                if not proc_path.exists():
                    continue
                df = pd.read_csv(proc_path)

                df["robot_x"] -= center_x
                df["robot_y"] -= center_y
                df["target_x"] -= center_x
                df["target_y"] -= center_y

                df["robot_x"] = -df["robot_x"]
                df["robot_y"] = -df["robot_y"]
                df["target_x"] = -df["target_x"]
                df["target_y"] = -df["target_y"]

                all_x.append(df["robot_x"].values)
                all_y.append(df["robot_y"].values)
                if target_df is None:
                    target_df = df[["target_x", "target_y"]]

            if not all_x:
                continue

            min_len = min(len(x) for x in all_x)
            aligned_x = np.array(
                [
                    np.interp(np.linspace(0, 1, min_len), np.linspace(0, 1, len(x)), x)
                    for x in all_x
                ]
            )
            aligned_y = np.array(
                [
                    np.interp(np.linspace(0, 1, min_len), np.linspace(0, 1, len(y)), y)
                    for y in all_y
                ]
            )

            mean_x, mean_y = aligned_x.mean(axis=0), aligned_y.mean(axis=0)

            method_color = method_color_map.get(method_name, next(fallback_colors))

            ax.plot(
                mean_x,
                mean_y,
                color=method_color,
                label=method_name,
                linewidth=2.0,
                zorder=i + 2,
            )

            if target_df is not None and not target_df_plotted:
                ax.plot(
                    target_df["target_x"],
                    target_df["target_y"],
                    color=target_path_color,
                    linestyle="dashed",
                    label="Target Path",
                    linewidth=3.0,
                    zorder=1,
                )
                target_df_plotted = True

        ax.set_xlim(-2.75, 2.75)
        ax.set_ylim(-1.575, 1.575)
        ax.set_aspect("equal", adjustable="box")
        fig.tight_layout()

        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

        plot_path = output_dir / f"trajectory_{traj_name}.png"
        fig.savefig(plot_path, format="png")
        print(f"Saved centered trajectory plot: {plot_path}")
        plt.close(fig)


def _generate_summary_plots_and_table(
    exp_definitions: List[Tuple[str, str]], output_dir: Path, caption: str, label: str
):
    """Generates bar charts (as png) and a LaTeX table from all experiment summary files."""
    summary_rows = []
    for method_name, glob_pattern in exp_definitions:
        for path in Path(".").glob(glob_pattern):
            summary_path = path.with_name(f"{path.stem}_summary.json")
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    data = json.load(f)
                    summary_rows.append(
                        {
                            "Method": method_name,
                            "ATE (m)": data["ate_m"] * 100.0,
                            "Orientation Error (rad)": data.get("ate_rad", 0.0)
                            * 180
                            / np.pi,
                            "Jerk (m/s³)": data["jerk_avg_m_s3"],
                        }
                    )

    if not summary_rows:
        print("Error: No summary data could be found. Cannot generate report.")
        return
    df_summary = pd.DataFrame(summary_rows)

    print("\n--- Generating Performance Bar Charts (png) ---")
    for metric in ["ATE (m)", "Orientation Error (rad)", "Jerk (m/s³)"]:
        if metric not in df_summary.columns or df_summary[metric].sum() == 0:
            continue
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(
            data=df_summary, x="Method", y=metric, ax=ax, palette="viridis", capsize=0.1
        )
        ax.set_title(f"Performance Comparison: {metric}")
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        plot_path = output_dir / f"comparison_{metric.split(' ')[0].lower()}.png"
        fig.savefig(plot_path, format="png")
        print(f"Saved comparison plot: {plot_path}")
        plt.close(fig)

    print("\n--- Generating LaTeX Table ---")
    df_agg = df_summary.groupby("Method").agg([np.mean, np.std])

    ate_means = df_agg[("ATE (m)", "mean")]
    jerk_means = df_agg[("Jerk (m/s³)", "mean")]
    min_ate_method = ate_means.idxmin()
    min_jerk_method = jerk_means.idxmin()

    if "Orientation Error (rad)" in df_summary.columns:
        orient_means = df_agg[("Orientation Error (rad)", "mean")]
        min_orient_method = orient_means.idxmin()
    else:
        min_orient_method = None

    formatted_rows = {}
    for method, row in df_agg.iterrows():
        ate_str = f"{row[('ATE (m)', 'mean')]:.3f} $\\pm$ {row[('ATE (m)', 'std')]:.3f}"
        jerk_str = f"{row[('Jerk (m/s³)', 'mean')]:.3f} $\\pm$ {row[('Jerk (m/s³)', 'std')]:.3f}"
        if method == min_ate_method:
            ate_str = f"\\textbf{{{ate_str}}}"
        if method == min_jerk_method:
            jerk_str = f"\\textbf{{{jerk_str}}}"

        formatted_rows[method] = {"ATE (m)": ate_str, "Jerk (m/s³)": jerk_str}

        if min_orient_method:
            orient_str = f"{row[('Orientation Error (rad)', 'mean')]:.3f} $\\pm$ {row[('Orientation Error (rad)', 'std')]:.3f}"
            if method == min_orient_method:
                orient_str = f"\\textbf{{{orient_str}}}"
            formatted_rows[method]["Orientation Error (rad)"] = orient_str

    df_final = pd.DataFrame.from_dict(formatted_rows, orient="index")
    column_format = "lrrr" if min_orient_method else "lrr"

    latex_str = df_final.to_latex(
        index=True,
        escape=False,
        caption=caption,
        label=label,
        column_format=column_format,
        position="!ht",
    )
    latex_path = output_dir / f"{label}.tex"
    with open(latex_path, "w") as f:
        f.write(latex_str)
    print(f"Saved LaTeX table: {latex_path}")
    print("\n--- LaTeX Source ---")
    print(latex_str)


def run_animation(args: argparse.Namespace):
    """Generates a high-quality MP4 animation of a single run."""
    if isinstance(args.processed_file, (str, Path)):
        proc_paths = [args.processed_file]
    else:
        proc_paths = args.processed_file

    for proc_path in proc_paths:
        if not proc_path.exists():
            print(f"Error: Processed file not found: {proc_path}")
            return

        print(f"--- Generating Animation for {proc_path.name} ---")
        df = pd.read_csv(proc_path)

        min_x = df["target_x"].min()
        max_x = df["target_x"].max()
        min_y = df["target_y"].min()
        max_y = df["target_y"].max()
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        for col in ["robot_x", "target_x"]:
            df[col] = -(df[col] - center_x)
        for col in ["robot_y", "target_y"]:
            df[col] = -(df[col] - center_y)

        for col in ["robot_yaw", "target_yaw"]:
            df[col] = np.arctan2(np.sin(df[col] + np.pi), np.cos(df[col] + np.pi))

        fig, ax = plt.subplots(figsize=(10, 10))

        all_pos = np.concatenate(
            [
                df[["target_x", "target_y"]].values,
                df[["robot_x", "robot_y"]].values,
            ]
        )
        ax.set_xlim(all_pos[:, 0].min() - 0.5, all_pos[:, 0].max() + 0.5)
        ax.set_ylim(all_pos[:, 1].min() - 0.5, all_pos[:, 1].max() + 0.5)
        ax.set_aspect("equal", adjustable="box")

        ax.plot(
            df["target_x"], df["target_y"], "r--", linewidth=1.5, label="Target Path"
        )
        (robot_path,) = ax.plot([], [], "b-", linewidth=2.5, label="Rover Path")
        target_quiver = ax.quiver(
            [],
            [],
            [],
            [],
            color="red",
            scale=25,
            width=0.008,
            label="Target Pose",
        )
        robot_quiver = ax.quiver(
            [], [], [], [], color="blue", scale=25, width=0.008, label="Rover Pose"
        )
        time_text = ax.text(
            0.02,
            0.98,
            "",
            transform=ax.transAxes,
            fontsize=12,
            va="top",
            bbox=dict(facecolor="white", alpha=0.8),
        )

        ax.legend(loc="upper right", ncol=2)

        def update(frame: int) -> Tuple:
            robot_path.set_data(df["robot_x"][: frame + 1], df["robot_y"][: frame + 1])
            robot_x, robot_y, robot_yaw = (
                df["robot_x"][frame],
                df["robot_y"][frame],
                df["robot_yaw"][frame],
            )
            robot_quiver.set_offsets(np.c_[robot_x, robot_y])
            robot_quiver.set_UVC(np.cos(robot_yaw), np.sin(robot_yaw))

            target_x, target_y, target_yaw = (
                df["target_x"][frame],
                df["target_y"][frame],
                df["target_yaw"][frame],
            )
            target_quiver.set_offsets(np.c_[target_x, target_y])
            target_quiver.set_UVC(np.cos(target_yaw), np.sin(target_yaw))

            orient_err_deg = np.rad2deg(df["orientation_error_rad"][frame])
            time_text.set_text(
                f"Position Error: {100.0 * abs(df['euclidean_error'][frame]):.1f} cm\n"
                f"Orientation Error: {abs(orient_err_deg):.1f}°"
            )
            return robot_path, target_quiver, robot_quiver, time_text

        frame_step = max(1, len(df) // 450)
        ani = animation.FuncAnimation(
            fig, update, frames=range(0, len(df), frame_step), blit=True, interval=33
        )

        anim_path = (
            args.output_dir
            / f"{proc_path.stem.replace('_processed', '')}_animation.mp4"
        )
        try:
            writer = animation.FFMpegWriter(
                fps=30, metadata=dict(artist="LCS-SnT"), bitrate=3000
            )
            ani.save(str(anim_path), writer=writer, dpi=200)
            print(f"Saved animation: {anim_path}")
        except FileNotFoundError:
            print(
                "\nERROR: FFmpeg NOT FOUND. Animation not saved. Please install ffmpeg.\n"
            )
        plt.close(fig)


def run_collection(args: argparse.Namespace):
    """Entry point for the 'collect' command."""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = TrajectoryCollectorNode(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.save_data()
        node.destroy_node()
        rclpy.shutdown()


def run_processing(args: argparse.Namespace):
    """Entry point for the 'process' command."""
    print("--- Starting Batch Data Processing ---")
    for file_path in args.input_files:
        if file_path.is_file() and "_processed" not in file_path.name:
            _process_file(file_path)
        else:
            print(f"Skipping: {file_path} (not a valid raw data file)")


def run_report(args: argparse.Namespace):
    """Entry point for the 'report' command."""
    args.output_dir.mkdir(parents=True, exist_ok=True)
    grouped_results = _load_and_group_experiments(args.exp)
    if not grouped_results:
        print("No data found. Exiting report generation.")
        return
    _plot_trajectories_with_confidence(grouped_results, args.output_dir)
    _generate_summary_plots_and_table(
        args.exp, args.output_dir, args.caption, args.label
    )


def main():
    """Main function to parse arguments and execute the selected command."""
    parser = argparse.ArgumentParser(
        description="A comprehensive tool for rover trajectory evaluation.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    p_collect = subparsers.add_parser(
        "collect",
        help="Run as a ROS 2 node to collect trajectory data.",
        description="Launches a ROS 2 node to listen to TF2 transforms and record raw trajectory data to a CSV file.",
    )
    p_collect.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Path to the output CSV file for the raw data.",
    )
    p_collect.add_argument(
        "--robot-frame",
        type=str,
        default="robot",
        help="The TF frame of the robot.",
    )
    p_collect.add_argument(
        "--target-frame",
        type=str,
        default="target",
        help="The TF frame of the dynamic target.",
    )
    p_collect.add_argument(
        "--fixed-frame",
        type=str,
        default="world",
        help="The fixed TF frame (e.g., odom, map).",
    )
    p_collect.add_argument(
        "--rate", type=float, default=50.0, help="Data collection frequency (Hz)."
    )
    p_collect.set_defaults(func=run_collection)

    p_process = subparsers.add_parser(
        "process",
        help="Batch process raw CSV files to calculate metrics.",
        description="Takes raw CSV files as input, calculates performance metrics (error, jerk, etc.), and saves both a processed CSV and a summary JSON file for each input.",
    )
    p_process.add_argument(
        "input_files",
        type=Path,
        nargs="+",
        help="One or more raw trajectory CSV files to process.",
    )
    p_process.set_defaults(func=run_processing)

    p_report = subparsers.add_parser(
        "report",
        help="Generate all plots (png) and tables for a publication.",
        description="Compares multiple methods by analyzing processed data. Generates trajectory plots with confidence intervals, performance bar charts with error bars, and a publication-ready LaTeX table.",
    )
    p_report.add_argument(
        "--exp",
        action="append",
        nargs=2,
        metavar=("METHOD_NAME", "RAW_CSV_GLOB"),
        required=True,
        help="Define a method and the glob pattern for its raw CSVs.\nCan be used multiple times for comparison.\nExample: --exp PPO 'data/*_ppo_*.csv' --exp DreamerV3 'data/*_dreamer_*.csv'",
    )
    p_report.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("./paper_results"),
        help="Directory to save all generated figures and tables.",
    )
    p_report.add_argument(
        "--caption",
        type=str,
        default="Comparison of Real-World Performance Metrics.",
        help="Caption for the LaTeX table.",
    )
    p_report.add_argument(
        "--label",
        type=str,
        default="tab:results",
        help="Label for the LaTeX table (e.g., 'tab:my_results').",
    )
    p_report.set_defaults(func=run_report)

    p_anim = subparsers.add_parser(
        "animate",
        help="Create an MP4 animation for a single run.",
        description="Generates a high-quality MP4 video of a single trajectory run, showing the rover's path and orientation over time.",
    )
    p_anim.add_argument(
        "processed_file",
        type=Path,
        nargs="+",
        help="Path to one or more '..._processed.csv' file to animate.",
    )
    p_anim.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("./paper_results"),
        help="Directory to save the animation.",
    )
    p_anim.set_defaults(func=run_animation)

    args = parser.parse_args()
    if hasattr(args, "output_dir"):
        args.output_dir.mkdir(parents=True, exist_ok=True)
    args.func(args)


if __name__ == "__main__":
    main()
