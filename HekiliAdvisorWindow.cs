// HekiliReborn - advisory overlay for a custom RotationSolverReborn fork.
// This view renders only existing, live RSR recommendations. It does NOT
// pretend to predict future GCDs or multiple future oGCDs.
using Dalamud.Bindings.ImGui;
using Dalamud.Interface.Windowing;
using RotationSolver.UI.HighlightTeachingMode;
using RotationSolver.Updaters;

namespace RotationSolver.UI.ExtraWindows;

internal static class HekiliAdvisorMode
{
    // Deliberately fixed for this experimental fork. The automatic execution
    // gate in MajorUpdater checks this constant. It is NOT a user setting.
    internal const bool GuidanceOnly = true;
}

internal sealed class HekiliAdvisorWindow : Window
{
    private const ImGuiWindowFlags AdvisorFlags = ImGuiWindowFlags.AlwaysAutoResize |
        ImGuiWindowFlags.NoScrollbar | ImGuiWindowFlags.NoScrollWithMouse;

    internal HekiliAdvisorWindow() : base("Hekili Reborn (prototype)##hekiliadvisor", AdvisorFlags)
    {
    }

    public override void Draw()
    {
        var next = ActionUpdater.NextAction;
        var gcd = ActionUpdater.NextGCDAction;

        ImGui.TextUnformatted("RSR-powered recommendations  |  MANUAL INPUT ONLY");
        ImGui.Separator();

        if (next == null && gcd == null)
        {
            ImGui.TextDisabled("No rotation prediction available.");
            ImGui.TextDisabled("Check that RSR's rotation/Teaching Mode is active.");
            return;
        }

        if (next != null)
        {
            ImGui.BeginGroup();
            ImGui.TextUnformatted("PRESS NOW");
            // Do not handle this control's return value: the overlay never
            // sends a skill request or queues a skill.
            _ = ActionIcon.Draw("##hekili_live_next", next, 72f, true);
            ImGui.EndGroup();
        }

        if (gcd != null)
        {
            if (next != null) ImGui.SameLine(0f, 22f);
            ImGui.BeginGroup();
            ImGui.TextUnformatted("NEXT GCD");
            _ = ActionIcon.Draw("##hekili_live_gcd", gcd, 60f, true);
            ImGui.EndGroup();
        }

        ImGui.Separator();
        ImGui.TextDisabled("Future GCDs: not yet simulated");
        ImGui.TextDisabled("Second weave: not yet simulated");
        ImGui.TextDisabled("Source: live RSR rotation logic; no actions executed.");
    }
}
