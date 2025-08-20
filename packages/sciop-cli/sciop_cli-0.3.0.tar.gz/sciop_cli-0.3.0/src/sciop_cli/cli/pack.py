import click

from sciop_cli.pack import ALGO_MAP, PACK_MODES, PackArgs, PackManager, run_packing_pipeline


@click.command("pack")
@click.option(
    "--path",
    "-p",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Directory to pack (walked recursively).",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["heuristic", "leaf", "depth"], case_sensitive=False),
    default="heuristic",
    show_default=True,
    help=(
        "Directory-selection strategy:\n"
        "  - heuristic → score each sub-directory using --min-filecount, "
        "--max-mean-kib, and --min-total-mib (optionally --top-n or --weights); "
        "compress the top matches.\n"
        "  - leaf      → inspect only leaf dirs (contain files but no subfolders); "
        "skip a leaf if >= --skip-threshold of its files are already compressed.\n"
        "  - depth     → compress those dirs exactly --depth levels below base "
        "(depth 1 = children, 2 = grandchildren, etc.)."
    ),
)
@click.option("--depth", type=int, default=None, help="Depth level for depth mode.")
@click.option(
    "--skip-threshold",
    type=float,
    default=None,
    help="Leaf mode: fraction of present compressed files in a leaf that causes skipping.",
)
@click.option("--min-filecount", type=int, default=None, help="Heuristic: minimum # files.")
@click.option("--max-mean-kib", type=int, default=None, help="Heuristic: max mean file size (KiB).")
@click.option("--min-total-mib", type=int, default=None, help="Heuristic: min total size (MiB).")
@click.option(
    "--top-n",
    type=int,
    default=None,
    help="Heuristic: cap number of directories to compress.",
)
@click.option(
    "--hash-algo",
    "-a",
    type=click.Choice(list(ALGO_MAP.keys()), case_sensitive=False),
    default="sha512",
    show_default=True,
    help="Which checksum algorithm to write into manifest-<algo>.txt",
)
def pack(
    path: str,
    mode: PACK_MODES = "heuristic",
    depth: int | None = None,
    skip_threshold: float | None = None,
    min_filecount: int | None = None,
    max_mean_kib: int | None = None,
    min_total_mib: int | None = None,
    top_n: int | None = None,
    hash_algo: str = "sha512",
) -> None:
    args = PackArgs.from_kwargs(
        mode=mode,
        base_dir=path,
        depth=depth,
        skip_threshold=skip_threshold,
        min_filecount=min_filecount,
        max_mean_kib=max_mean_kib,
        min_total_mib=min_total_mib,
        top_n=top_n,
        hash_algo=hash_algo,
    )

    try:
        run_packing_pipeline(args)
    except Exception as e:
        click.echo(click.style(f"Packing failed: {e}", fg="red"), err=True)
        raise SystemExit(1) from e


@click.command("unpack")
@click.option(
    "-p",
    "--base-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Directory that contains <base>.packmap.json and the .tar.zst archives.",
)
def unpack(base_dir: str) -> None:
    try:
        pm = PackManager(PackArgs.from_kwargs(mode="leaf", base_dir=base_dir))
        restored = pm.restore_directory()
        click.echo(f"Restored {len(restored)} archive(s).")
    except Exception as e:
        click.echo(click.style(f"Restore failed: {e}", fg="red"), err=True)
        raise SystemExit(1) from e
