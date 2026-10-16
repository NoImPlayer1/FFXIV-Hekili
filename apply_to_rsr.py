#!/usr/bin/env python3
"""Apply the HekiliReborn prototype to a clean upstream RSR checkout.
This script intentionally aborts if upstream code changed, to avoid silently
breaking automation guards or creating a misbuilt plugin.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) >= 2 else None
if root is None:
    raise SystemExit('Usage: py apply_to_rsr.py "C:\\path\\to\\RotationSolverReborn"')
if not (root / 'RotationSolver/RotationSolverPlugin.cs').exists():
    raise SystemExit('Not an RSR checkout: RotationSolver/RotationSolverPlugin.cs missing')

plugin = root / 'RotationSolver/RotationSolverPlugin.cs'
major = root / 'RotationSolver/Updaters/MajorUpdater.cs'
added = root / 'RotationSolver/UI/ExtraWindows/HekiliAdvisorWindow.cs'
if added.exists():
    raise SystemExit('Already patched: HekiliAdvisorWindow.cs exists')

# Use exact anchors verified against upstream main as of 2026-10-16.
changes = {
    plugin: [
        ('private static NextActionWindow? _nextActionWindow;',
         'private static NextActionWindow? _nextActionWindow;\n\tprivate static HekiliAdvisorWindow? _hekiliAdvisorWindow;'),
        ('_nextActionWindow = new();',
         '_nextActionWindow = new();\n\t\t_hekiliAdvisorWindow = new();'),
        ('windowSystem.AddWindow(_nextActionWindow);',
         'windowSystem.AddWindow(_nextActionWindow);\n\t\twindowSystem.AddWindow(_hekiliAdvisorWindow);'),
        ('_nextActionWindow!.IsOpen = isValid && Service.Config.ShowNextActionWindow;',
         '_nextActionWindow!.IsOpen = false; // Replaced by Hekili advisor overlay.\n'
        '\t\t_hekiliAdvisorWindow!.IsOpen = MajorUpdater.IsValid;'),    ],
    major: [
        ('if (canDoAction)\n\t\t{',
         'if (canDoAction && !RotationSolver.UI.ExtraWindows.HekiliAdvisorMode.GuidanceOnly)\n\t\t{'),
        ('AutoAttackUpdater.Update();',
         '// Hekili guidance-only fork: never initiate auto attacks.\n'
         '\t\t\t// AutoAttackUpdater.Update();'),
        ('if (DataCenter.IsTargetOnly)\n\t\t{',
         'if (DataCenter.IsTargetOnly && !RotationSolver.UI.ExtraWindows.HekiliAdvisorMode.GuidanceOnly)\n\t\t{'),
        ('if (!DataCenter.IsTargetOnly && Service.Config.TeachingMode && Service.Config.TeachingModeAutoTarget && DataCenter.InCombat)',
         'if (!DataCenter.IsTargetOnly && Service.Config.TeachingMode && Service.Config.TeachingModeAutoTarget && DataCenter.InCombat && !RotationSolver.UI.ExtraWindows.HekiliAdvisorMode.GuidanceOnly)'),
    ],
}

# Verify every anchor exactly once in every target before modifying anything.
new_contents = {}
for path, replacements in changes.items():
    txt = path.read_text(encoding='utf-8-sig')
    for old, new in replacements:
        n = txt.count(old)
        if n != 1:
            raise SystemExit(f'STOP: expected exactly one occurrence in {path.name} of {old[:70]!r}; found {n}.\n'
                             'Upstream changed. Do not force this patch; have it reviewed first.')
        txt = txt.replace(old, new, 1)
    new_contents[path] = txt

added.parent.mkdir(parents=True, exist_ok=True)
added.write_bytes((Path(__file__).parent / 'HekiliAdvisorWindow.cs').read_bytes())
for path, txt in new_contents.items():
    path.write_text(txt, encoding='utf-8-sig')
print('Patch applied to RSR source. Guidance-only core action gate installed.')
print('Build the RSR solution on Windows, then load the modified fork as a dev plugin.')
