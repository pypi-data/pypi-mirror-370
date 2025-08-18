import argparse, importlib, pkgutil, os, logging
from core import ConfigManager, BackupManager
from logger import setup_logging
from utils import ts, host
from actions.doctor import do_doctor
from actions.defaults import defaults_export_all, defaults_import_dir
from actions.diffpack import do_diff, do_pack
from actions.profile import profile_list, profile_use, profile_save

from _version import VERSION

def build_parser():
    p = argparse.ArgumentParser(prog="myconfig", description="macOS configuration export/restore tool - readable and extensible")
    p.add_argument("-y","--yes", action="store_true")
    p.add_argument("-n","--dry-run", action="store_true")
    p.add_argument("-v","--verbose", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--no-mas", action="store_true")
    p.add_argument("--preview", action="store_true", help="Preview mode, show what will be processed")
    p.add_argument("--version", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("export", help="Export to backup directory")
    sp.add_argument("outdir", nargs="?")
    sp.add_argument("--compress", action="store_true", help="Create compressed backup archive (.tar.gz)")

    sp = sub.add_parser("restore", help="Restore from backup directory")
    sp.add_argument("srcdir")

    sub.add_parser("doctor", help="Health check and diagnosis")

    sp = sub.add_parser("defaults", help="System defaults extended operations")
    s2 = sp.add_subparsers(dest="sub")
    s2.add_parser("export-all", help="Export all defaults domains (with exclusion list)")
    spi = s2.add_parser("import", help="Import defaults from directory (batch plist)")
    spi.add_argument("dir")

    sp = sub.add_parser("diff", help="Compare differences between two backup directories")
    sp.add_argument("a"); sp.add_argument("b")

    sp = sub.add_parser("pack", help="Pack and encrypt backup (zip/gpg optional)")
    sp.add_argument("srcdir"); sp.add_argument("outfile", nargs="?")
    sp.add_argument("--gpg", action="store_true", help="Use gpg symmetric encryption")
    
    sp = sub.add_parser("unpack", help="Unpack compressed backup archive")
    sp.add_argument("archive", help="Path to backup archive (.tar.gz)")
    sp.add_argument("outdir", nargs="?", help="Output directory (optional, will create temp dir if not specified)")

    sp = sub.add_parser("profile", help="Configuration profiles (profiles/*.toml)")
    s3 = sp.add_subparsers(dest="sub")
    s3.add_parser("list", help="List available profiles")
    spu = s3.add_parser("use", help="Apply profile to config.toml")
    spu.add_argument("name")
    s3s = s3.add_parser("save", help="Save current config.toml as new profile")
    s3s.add_argument("name")

    # Auto-register plugins (requires register(subparsers) in src/plugins/*.py)
    plug_dir = os.path.join(os.path.dirname(__file__), "plugins")
    for m in pkgutil.iter_modules([plug_dir]):
        mod = importlib.import_module(f"plugins.{m.name}")
        if hasattr(mod, "register"):
            mod.register(sub)

    return p

def main():
    p = build_parser()
    args = p.parse_args()
    if args.version:
        print(f"myconfig {VERSION}"); return
    
    # Load and update configuration
    config_manager = ConfigManager("./config/config.toml")
    cfg = config_manager.load()
    cfg = cfg.update(
        interactive = (not args.yes) if args.yes else cfg.interactive,
        dry_run = True if args.dry_run else cfg.dry_run,
        verbose = True if args.verbose else cfg.verbose,
        quiet   = True if args.quiet else cfg.quiet,
        enable_mas = False if args.no_mas else cfg.enable_mas,
    )
    
    # Setup logging
    setup_logging(verbose=cfg.verbose, quiet=cfg.quiet)
    
    # Create backup manager
    backup_manager = BackupManager(cfg)
    
    # Preview mode handling
    preview_mode = getattr(args, 'preview', False)

    if args.cmd == "export":
        default_outdir = args.outdir or f"./backups/backup-{host()}-{ts()}"
        compress = getattr(args, 'compress', False)
        if preview_mode:
            backup_manager.preview_export(default_outdir)
        else:
            backup_manager.export(default_outdir, compress=compress)
    elif args.cmd == "restore":
        if preview_mode:
            backup_manager.preview_restore(args.srcdir)
        else:
            backup_manager.restore(args.srcdir)
    elif args.cmd == "doctor":
        do_doctor(cfg)
    elif args.cmd == "defaults":
        if args.sub == "export-all": defaults_export_all(cfg)
        elif args.sub == "import":   defaults_import_dir(cfg, args.dir)
        else: p.print_help()
    elif args.cmd == "diff":
        do_diff(cfg, args.a, args.b)
    elif args.cmd == "pack":
        do_pack(cfg, args.srcdir, args.outfile, use_gpg=args.gpg)
    elif args.cmd == "unpack":
        extracted_dir = backup_manager.unpack(args.archive, args.outdir)
        if extracted_dir:
            logger = logging.getLogger(__name__)
            logger.info(f"Archive contents available at: {extracted_dir}")
            if not args.outdir:
                logger.info("To restore: myconfig restore " + extracted_dir)
    elif args.cmd == "profile":
        if args.sub == "list": profile_list()
        elif args.sub == "use": profile_use(args.name)
        elif args.sub == "save": profile_save(args.name)
        else: p.print_help()
    else:
        p.print_help()
