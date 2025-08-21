from . import BackupSystem, ConfigLoader


def setup():
    cfg = ConfigLoader().run()

    if cfg.backup:
        BackupSystem(cfg).run()

    return cfg
